from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from typing import Any

from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, select, and_, or_, desc, func

import mashumaro

import logging
import threading
import apprise
import datetime

import classes_orm
import json_http_schema
import utils
import scripts.populate
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.DEBUG)


# Autenticazione. Molto semplice, però la password è salvata in chiaro!
users = {
    'admin0': generate_password_hash('password0'),
    'admin1': generate_password_hash('password1')
}

auth = HTTPBasicAuth()
auth_token = HTTPTokenAuth(scheme='Bearer')

@auth.verify_password
def verify_password(username, password):
    if (username in users
       and check_password_hash(users.get(username), password)):
        return username


# Iniziallizazione.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STATIC_FOLDER'] = 'frontend/dist'
db = SQLAlchemy(app, model_class=classes_orm.Base)
with app.app_context():
    # Crea tutte le tabelle.
    db.create_all()


@app.route('/')
@auth.login_required
def index():
    return send_from_directory(app.config['STATIC_FOLDER'], 'index.html')


# Componenti Svelte.
@app.route('/<path:path>')
@auth.login_required
def static_proxy(path):
    return send_from_directory(app.config['STATIC_FOLDER'], path)


@app.route('/token', methods=['GET', 'POST'])
@auth.login_required
def rest_token():
    if request.method == 'GET':
        # NOTA BENE:
        # I token disponibili possono essere visualizzati solo usando
        # le credenziali admin.
        return utils.list_db_objects(classes_orm.Token, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.TokenSchema, request.data)
        if not ok:
            return new_data

        # Controlla che il token non esista già.
        token = db.session.query(classes_orm.Token).filter(
                classes_orm.Token.api_token == new_data.api_token
        ).first()
        if token is not None:
            # Se il token esiste, avverti l'utente.
            return jsonify({'error': f'token {new_data.api_token} already used'}), 401

        return utils.new_db_object(
            classes_orm.Token(
                api_token=new_data.api_token,
            ),
            db
        )


@app.route('/token/<int:token_id>', methods=['GET', 'PUT'])
@auth.login_required
def rest_show_token(token_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.Token, token_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/alarm', methods=['GET', 'POST'])
def rest_alarm():
    if request.method == 'GET':
        objs = db.session.query(classes_orm.Alarm).all()
        # Abbiamo bisogno del timestamp in formato UTC (Zulu) e il
        # metodo serialize nel database lo implementa.
        d: list[dict] = [obj.serialize() for obj in objs]

        # La vista degli allarmi deve essere presentata con i timestamp in
        # ordine descrescente. 
        return jsonify(sorted(d, key=lambda x: x['timestamp'], reverse=True)), 200
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.AlarmSchema, request.data)
        if not ok:
            return new_data

        return utils.new_db_object(
            classes_orm.Alarm(
                code=new_data.code,
                description=new_data.description,
                severity_level=new_data.severity_level,
                timestamp=new_data.timestamp,
                visible=True,
            ),
            db
        )


@app.route('/alarm/<int:alarm_id>', methods=['GET', 'PUT'])
def rest_show_alarm(alarm_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.Alarm, alarm_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/ticket', methods=['GET', 'POST'])
def rest_ticket():
    if request.method == 'GET':
        # Ordina i ticket in ordine decrescente di timestamp di
        # Ticket.alarms[0].
        # L'ID allarme con timestamp più recente è già il primo della lista per
        # ogni ticket.
        tickets = db.session.query(classes_orm.Ticket).all()

        tickets_with_timestamps: list[tuple[classes_orm.Ticket, datetime.datetime]] = []
        for ticket in tickets:
            # Qui bisogna ordinare perchè l'ordinamento avviene solo nel
            # metodo serialize, non nell'ORM.
            sorted_alarms = sorted(ticket.alarms, key=lambda a: a.timestamp, reverse=True)
            
            if sorted_alarms:
                first_alarm_timestamp = sorted_alarms[0].timestamp
            else:
                # Caso improbabile: nessun allarme collegato al ticket,
                # posiziona alla fine.
                first_alarm_timestamp = float('inf')

            tickets_with_timestamps.append((ticket, first_alarm_timestamp))

        # Ordina i ticket in base al timestamp del primo allarme.
        sorted_tickets = sorted(tickets_with_timestamps, key=lambda x: x[1], reverse=True)

        # Seleziona solo i ticket.
        sorted_ticket_instances = [ticket for ticket, _ in sorted_tickets]
        return jsonify([ticket.serialize() for ticket in sorted_ticket_instances]), 200

    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.TicketSchema, request.data)
        if not ok:
            return new_data

        alarms = db.session.query(classes_orm.Alarm).filter(
            and_(
                classes_orm.Alarm.id.in_(new_data.alarm_ids),
                classes_orm.Alarm.ticket_id.is_(None)
            )
        ).all()
        if alarms is None or len(alarms) < len(new_data.alarm_ids):
            return jsonify({'error': f'at least 1 alarm in the list {str(new_data.alarm_ids)} not found or at least 1 alarm already belongs to a ticket'}), 404

        return utils.new_db_object(
            classes_orm.Ticket(
                code=new_data.code,
                alarms=alarms,
            ),
            db
        )


@app.route('/ticket/<int:ticket_id>', methods=['GET', 'PUT'])
def rest_show_ticket(ticket_id):
    if request.method == 'GET':
        # Ordina gli allarmi in modo decrescente di timestamp: l'allarme
        # con timestamp più recente deve essere primo della lista degli id
        # allarmi.
        return utils.detail_db_object(classes_orm.Ticket, ticket_id, db)
    elif request.method == 'PUT':
        # Chiudendo il ticket (stato "RESOLVED") gli allarmi associati vengono
        # nascosti.
        #
        # Esempio query:
        #
        # curl \
        #    -X PUT \
        #    http://localhost:8080/ticket/1 \
        #    -H "Content-Type: application/json" \
        #    -d '{"status": "RESOLVED"}'

        # Troviamo il ticket.
        ticket = utils.detail_db_object(classes_orm.Ticket, ticket_id, db, False)
        if not ticket:
             return jsonify({'error': f'Ticket {ticket_id} not found'}), 404

        # Ci aspettiamo solo di avere `status` come parametro JSON.
        data = request.get_json()
        if 'status' not in data:
            return jsonify({'error': 'missing "status" parameter'}), 400
        
        new_status = data['status']

        valid_status: list[code] = [e.value for e in classes_orm.TicketCode]
        if new_status in valid_status:
            # Aggiorno lo stato del ticket.
            try:
                ticket.code = new_status
                db.session.commit()
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

            if new_status == 'RESOLVED':
                # Nascondiamo tutti gli allarmi associati al ticket risolto.
                visible = False
            else:
                # Nei ticket ri-aperti gli allarmi associati sono resi di
                # nuovo visibili.
                visible = True
            try:
                (
                    db.session.query(classes_orm.Alarm)
                        .filter(classes_orm.Alarm.ticket_id == ticket_id)
                        .update({'visible': visible})
                )
                db.session.commit()
                db.session.flush()
                return jsonify(ticket.serialize()), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({'error': f"invalid status, expecting one of {valid_status}"}), 400



@app.route('/voltage_range', methods=['GET', 'POST'])
def rest_voltage_range():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.VoltageRange, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.VoltageRangeSchema, request.data)
        if not ok:
            return new_data

        return utils.new_db_object(
            classes_orm.VoltageRange(
                lower=new_data.lower,
                upper=new_data.upper,
            ),
            db
        )


@app.route('/voltage_range/<int:voltage_range_id>', methods=['GET', 'PUT'])
def rest_show_voltage_range(voltage_range_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.VoltageRange, voltage_range_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/current_range', methods=['GET', 'POST'])
def rest_current_range():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.CurrentRange, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.CurrentRangeSchema, request.data)
        if not ok:
            return new_data

        return utils.new_db_object(
            classes_orm.CurrentRange(
                lower=new_data.lower,
                upper=new_data.upper,
            ),
            db
        )


@app.route('/current_range/<int:current_range_id>', methods=['GET', 'PUT'])
def rest_show_current_range(current_range_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.CurrentRange, current_range_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/daily_power_range', methods=['GET', 'POST'])
def rest_daily_power_range():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.DailyPowerRange, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.DailyPowerRangeSchema, request.data)
        if not ok:
            return new_data

        return utils.new_db_object(
            classes_orm.DailyPowerRange(
                lower=new_data.lower,
                upper=new_data.upper,
            ),
            db
        )


@app.route('/daily_power_range/<int:daily_power_range_id>', methods=['GET', 'PUT'])
def rest_show_daily_power_range(daily_power_range_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.DailyPowerRange, daily_power_range_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/monthly_power_range', methods=['GET', 'POST'])
def rest_monthly_power_range():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.MonthlyPowerRange, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.MonthlyPowerRangeSchema, request.data)
        if not ok:
            return new_data

        return utils.new_db_object(
            classes_orm.MonthlyPowerRange(
                lower=new_data.lower,
                upper=new_data.upper,
            ),
            db
        )


@app.route('/monthly_power_range/<int:monthly_power_range_id>', methods=['GET', 'PUT'])
def rest_show_monthly_power_range(monthly_power_range_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.MonthlyPowerRange, monthly_power_range_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/frequency_range', methods=['GET', 'POST'])
def rest_frequency_range():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.FrequencyRange, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.FrequencyRangeSchema, request.data)
        if not ok:
            return new_data

        return utils.new_db_object(
            classes_orm.FrequencyRange(
                lower=new_data.lower,
                upper=new_data.upper,
            ),
            db
        )


@app.route('/frequency_range/<int:frequency_range_id>', methods=['GET', 'PUT'])
def rest_show_frequency_range(frequency_range_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.FrequencyRange, frequency_range_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/battery_specification', methods=['GET', 'POST'])
def rest_battery_specification():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.BatterySpecification, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.BatterySpecificationSchema, request.data)
        if not ok:
            return new_data

        voltage_range = utils.detail_db_object(classes_orm.VoltageRange, new_data.voltage_range_id, db, False, 'voltage_range')
        if voltage_range is None:
            return jsonify({'error': f'object {new_data.voltage_range_id} not found'}), 404
   
        current_range = utils.detail_db_object(classes_orm.CurrentRange, new_data.current_range_id, db, False, 'current_range')
        if current_range is None:
            return jsonify({'error': f'object {new_data.current_range_id} not found'}), 404

        return utils.new_db_object(
            classes_orm.BatterySpecification(
                type=new_data.type,
                voltage_range=voltage_range,
                current_range=current_range,
                capacity=new_data.capacity,
            ),
            db
        )


@app.route('/battery_specification/<int:battery_specification_id>', methods=['GET', 'PUT'])
def rest_show_battery_specification(battery_specification_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.BatterySpecification, battery_specification_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/battery', methods=['GET', 'POST'])
def rest_battery():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.Battery, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.BatterySchema, request.data)
        if not ok:
            return new_data

        battery_specification = utils.detail_db_object(classes_orm.BatterySpecification, new_data.battery_specification_id, db, False, 'battery_specification')
        if battery_specification is None:
            return jsonify({'error': f'battery_specification {new_data.battery_specification_id} not found'}), 404

        return utils.new_db_object(
            classes_orm.Battery(
                name=new_data.name,
                battery_specification=battery_specification,
            ),
            db
        )


@app.route('/battery/<int:battery_id>', methods=['GET', 'PUT'])
def rest_show_battery(battery_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.Battery, battery_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/dc_current_system', methods=['GET', 'POST'])
def rest_dc_current_system():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.DcCurrentSystem, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.DcCurrentSystemSchema, request.data)
        if not ok:
            return new_data

        voltage_range = utils.detail_db_object(classes_orm.VoltageRange, new_data.voltage_range_id, db, False, 'voltage_range_id')
        if voltage_range is None:
            return jsonify({'error': f'voltage_range {new_data.voltage_range_id} not found'}), 404

        current_range = utils.detail_db_object(classes_orm.CurrentRange, new_data.current_range_id, db, False, 'current_range_id')
        if current_range is None:
            return jsonify({'error': f'current_range {new_data.current_range_id} not found'}), 404


        return utils.new_db_object(
            classes_orm.DcCurrentSystem(
                voltage_range=voltage_range,
                current_range=current_range,
            ),
            db
        )


@app.route('/dc_current_system/<int:dc_current_system_id>', methods=['GET', 'PUT'])
def rest_show_dc_current_system(dc_current_system_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.DcCurrentSystem, dc_current_system_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/ac_current_system', methods=['GET', 'POST'])
def rest_ac_current_system():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.AcCurrentSystem, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.AcCurrentSystemSchema, request.data)
        if not ok:
            return new_data

        voltage_range = utils.detail_db_object(classes_orm.VoltageRange, new_data.voltage_range_id, db, False, 'voltage_range_id')
        if voltage_range is None:
            return jsonify({'error': f'voltage_range {new_data.voltage_range_id} not found'}), 404

        current_range = utils.detail_db_object(classes_orm.CurrentRange, new_data.current_range_id, db, False, 'current_range_id')
        if current_range is None:
            return jsonify({'error': f'current_range {new_data.current_range_id} not found'}), 404


        frequency_range = utils.detail_db_object(classes_orm.FrequencyRange, new_data.frequency_range_id, db, False, 'frequency_range_id')
        if frequency_range is None:
            return jsonify({'error': f'frequency_range {new_data.frequency_range_id} not found'}), 404


        return utils.new_db_object(
            classes_orm.AcCurrentSystem(
                voltage_range=voltage_range,
                current_range=current_range,
                frequency_range=frequency_range,
            ),
            db
        )


@app.route('/ac_current_system/<int:ac_current_system_id>', methods=['GET', 'PUT'])
def rest_show_ac_current_system(ac_current_system_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.AcCurrentSystem, ac_current_system_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/plant_module_system', methods=['GET', 'POST'])
def rest_plant_module_system():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.PlantModuleSystem, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.PlantModuleSystemSchema, request.data)
        if not ok:
            return new_data

        ac_current = utils.detail_db_object(classes_orm.AcCurrentSystem, new_data.ac_current_id, db, False, 'ac_current')
        if ac_current is None:
            return jsonify({'error': f'ac_current {new_data.ac_current_id} not found'}), 404

        dc_current = utils.detail_db_object(classes_orm.DcCurrentSystem, new_data.dc_current_id, db, False, 'dc_current')
        if dc_current is None:
            return jsonify({'error': f'ac_current {new_data.dc_current_id} not found'}), 404

        return utils.new_db_object(
            classes_orm.PlantModuleSystem(
                ac_current=ac_current,
                dc_current=dc_current,
                capacity=new_data.capacity,
                make=new_data.make,
            ),
            db
        )


@app.route('/plant_module_system/<int:plant_module_system_id>', methods=['GET', 'PUT'])
def rest_show_plant_module_system(plant_module_system_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.PlantModuleSystem, plant_module_system_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/plant_battery_system', methods=['GET', 'POST'])
def rest_plant_battery_system():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.PlantBatterySystem, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.PlantBatterySystemSchema, request.data)
        if not ok:
            return new_data

        batteries = db.session.query(classes_orm.Battery).filter(
            and_(
                classes_orm.Battery.id.in_(new_data.battery_ids),
                classes_orm.Battery.plant_battery_system_id.is_(None)
            )
        ).all()
        if batteries is None or len(batteries) < len(new_data.battery_ids):
            return jsonify({'error': f'at least 1 battery in the list {str(new_data.battery_ids)} not found or at least 1 battery already belongs to a plant battery system'}), 404

        return utils.new_db_object(
            classes_orm.PlantBatterySystem(
                batteries=batteries,
                make=new_data.make,
            ),
            db
        )


@app.route('/plant_battery_system/<int:plant_battery_system_id>', methods=['GET', 'PUT'])
def rest_show_plant_battery_system(plant_battery_system_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.PlantBatterySystem, plant_battery_system_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/plant_production', methods=['GET', 'POST'])
def rest_plant_production():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.PlantProduction, db)
    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.PlantProductionSchema, request.data)
        if not ok:
            return new_data

        daily_power_range = utils.detail_db_object(classes_orm.DailyPowerRange, new_data.daily_power_range_id, db, False, 'daily_power_range')
        if daily_power_range is None:
            return jsonify({'error': f'daily_power_range {new_data.daily_power_range_id} not found'}), 404

        monthly_power_range = utils.detail_db_object(classes_orm.MonthlyPowerRange, new_data.monthly_power_range_id, db, False, 'monthly_power_range')
        if monthly_power_range is None:
            return jsonify({'error': f'monthly_power_range {new_data.monthly_power_range_id} not found'}), 404

        return utils.new_db_object(
            classes_orm.PlantProduction(
                daily_kwh=new_data.daily_kwh,
                monthly_kwh=new_data.monthly_kwh,
                daily_power_range=daily_power_range,
                monthly_power_range=monthly_power_range,
            ),
            db
        )


@app.route('/plant_production/<int:plant_production_id>', methods=['GET', 'PUT'])
def rest_show_plant_production_system(plant_production_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.PlantProduction, plant_production_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/owner', methods=['GET', 'POST'])
def rest_owner():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.Owner, db)

    elif request.method == 'POST':
        ok, new_data = utils.validate_json(json_http_schema.OwnerSchema, request.data)
        if not ok:
            return new_data

        return utils.new_db_object(
            classes_orm.Owner(
                first_name=new_data.first_name,
                last_name=new_data.last_name,
            ),
            db
        )


@app.route('/owner/<int:owner_id>', methods=['GET', 'PUT'])
def rest_show_owner(owner_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.Owner, owner_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/plant', methods=['GET', 'POST'])
def rest_plant():
    if request.method == 'GET':
        return utils.list_db_objects(classes_orm.Plant, db)

    elif request.method == 'POST':

        try:
            ok, new_data = utils.validate_json(json_http_schema.PlantSchema, request.data)
            if not ok:
                return new_data


            # Ricerco il proprietario dell'impianto.
            owner = utils.detail_db_object(classes_orm.Owner, new_data.owner_id, db, False, 'owner')
            if owner is None:
                return jsonify({'error': f'ac_current {new_data.owner_id} not found'}), 404


            # Il sistema modulo e il sistema batteria non devono già essere usati
            # da altri impianti. Qui sarebbe da usare il filtro `is_(None)` ma
            # a causa del "lazy loading" viene ritornato un errore di
            # implementazione da SQLAlchemy. Per questo motivo il controllo
            # deve essere fatto separatamente.
            plant_module_system = db.session.query(classes_orm.PlantModuleSystem).filter(
                classes_orm.PlantModuleSystem.id == new_data.plant_module_system_id,
            ).first()

            is_available: bool = False
            if plant_module_system is not None:
                if plant_module_system.plant is None:
                    is_available = True
            if not is_available:
                return jsonify({'error': f'plant_module_system {new_data.plant_module_system_id} not found or already used'}), 404

            plant_battery_system = db.session.query(classes_orm.PlantBatterySystem).filter(
                classes_orm.PlantBatterySystem.id == new_data.plant_battery_system_id,
            ).first()

            is_available: bool = False
            if plant_battery_system is not None:
                if plant_battery_system.plant is None:
                    is_available = True
            if not is_available:
                return jsonify({'error': f'plant_battery_system {new_data.plant_battery_system_id} not found or already used'}), 404

            plant_production = db.session.query(classes_orm.PlantProduction).filter(
                classes_orm.PlantProduction.id == new_data.plant_production_id,
            ).first()

            is_available: bool = False
            if plant_production is not None:
                if plant_production.plant is None:
                    is_available = True
            if not is_available:
                return jsonify({'error': f'plant_production {new_data.plant_production_id} not found or already used'}), 404

            # Creazione nuova istanza impianto basasta solo sugli id degli
            # oggetti (FK) esistenti.
            return utils.new_db_object(
                classes_orm.Plant(
                    name=new_data.name,
                    owner=owner,
                    installer=new_data.installer,
                    plant_module_system=plant_module_system,
                    plant_battery_system=plant_battery_system,
                    plant_production=plant_production
                ),
                db
            )

        except Exception as e:
            return {'error': f'{request.data} invalid data {e}'}, 500


@app.route('/plant/<int:plant_id>', methods=['GET', 'PUT'])
def rest_show_plant(plant_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.Plant, plant_id, db)
    elif request.method == 'PUT':
        # Aggiornamento dati esistenti.
        pass


@auth_token.verify_token
def is_valid_token(api_token: str) -> bool:
    # Query the database for the token
    if classes_orm.Token.query.filter_by(api_token=api_token).first():
        return True
    else:
        return False


class DummyDcFrequency:
    lower = 0.0
    upper = 0.0


def new_issues(new_data, obj: Any, db):
    r"""Controllo tutti i possibili allarmi di inverter e batterie, uno per uno,
        ed eventualmente creo gli allarmi, apro i ticket e chiudo i ticket
        non più rilevanti. Questa è una funzione con molta logica orientata
        alla manipolazione del database.
    """

    if isinstance(obj, classes_orm.PlantModuleSystem):
        # Modulo impianto.
        object_type = 'plant_module_system'
        if new_data.frequency == 0.0:
            # DC.
            current_system = obj.dc_current
            frequency_range = DummyDcFrequency()
        else:
            # AC.
            current_system = obj.ac_current
            frequency_range = current_system.frequency_range
        voltage_range = current_system.voltage_range
        current_range = current_system.current_range
        plant = obj.plant
    elif isinstance(obj, classes_orm.Battery):
        object_type = 'plant_battery_system'
        battery_specification = obj.battery_specification
        voltage_range = battery_specification.voltage_range
        current_range = battery_specification.current_range
        plant = obj.plant_battery_system.plant

    alarms: list = []
    if new_data.voltage < voltage_range.lower:
        alarms.append(
        {
            'message': 'rilevata tensione (V) inferiore al range',
            'alarm_code': '01',
        })
    if new_data.voltage > voltage_range.upper:
        alarms.append(
        {
            'message': 'rilevata tensione (V) superiore al range',
            'alarm_code': '01',
        })
    if new_data.current < current_range.lower:
        alarms.append(
        {
            'message': 'rilevata corrente (A) inferiore al range',
            'alarm_code': '01',
        })
    if new_data.current > current_range.upper:
        alarms.append(
        {
            'message': 'rilevata corrente (A) superiore al range',
            'alarm_code': '01',
        })
    if isinstance(obj, classes_orm.PlantModuleSystem):
        if new_data.frequency < frequency_range.lower:
            alarms.append(
            {
                'message': 'rilevata frequenza (Hz) inferiore al range',
                'alarm_code': '01',
            })
        if new_data.frequency > frequency_range.upper:
            alarms.append(
            {
                'message': 'rilevata frequenza (Hz) superiore al range',
                'alarm_code': '01',
            })

    # Caso allarme passato direttamente dall'API o dai microcontrollori.
    if new_data.alarm_code != '-01':
        if new_data.alarm_code == '00':
            message = 'errore software'
        elif new_data.alarm_code == '01':
            message = 'problema CC inverter'
        elif new_data.alarm_code == '02':
            message = 'problema BMS'
        elif new_data.alarm_code == '03':
            message = 'problema batteria slave'
        elif new_data.alarm_code == '04':
            message = 'problema componenti impianto'
        alarms.append(
        {
            'message': message,
            'alarm_code': new_data.alarm_code,
        })

    # Crea tutti gli allarmi necessari.
    for alarm in alarms:
        utils.new_db_object(
            classes_orm.Alarm(
                code=alarm['alarm_code'],
                description=alarm['message'],
                severity_level='medio',
                timestamp=new_data.timestamp,
                plant=plant
            ),
            db
        )

    # Creazione dei ticket.
    #
    # Controlla se esiste un'allarme dello stesso tipo (stesso codice errore,
    # stesso impianto, etc) >= 1 ora prima di questo controllo: se esiste
    # apri il ticket. Se non esiste, ignora.

    # Nota: nel database i timestamp sono salvati come oggetti naive UTC, non
    # aware, nonstante sia specificato che debbano essere aware. Questo
    # probabilmente dipende dal tipo di database (in memory).
    #
    # Per questo motivo dobbiamo togliere l'awareness dal timestamp
    # per il confronto.
    #
    # Si può verificare questa informazione con questo codice:
    #
    # Alm = classes_orm.Alarm
    #
    # def is_aware(dt):
    #    return dt.tzinfo is not None
    #
    # all_alarms = db.session.execute(select(Alm)).scalars().all()
    # for alarm in all_alarms:
    #    print(alarm.timestamp)
    #    print(is_aware(alarm.timestamp))
    #
    # Fondamentalmente i casi sono questi:
    #
    # given alarms of the same type (same code, description, severity level, plant_id, ticket_id==None)
    #
    # case 0: get both alarms a0 and a1
    #
    # ```
    # __*_____|_____*___|___>
    #    a0  -1h   a1   now
    # ```
    #
    # case 1: get both alarms a0 and a1
    #
    # ```________|__*_____*___|___>
    #          -1h  a0   a1  now
    # ```
    #
    # case 2: ignore both alarms a0 and a1
    #
    # ```
    # _*_____*___|______|__>
    #  a0    a1 -1h    now
    # ```
    #
    # case 3: only 1 alarm older than 1 hour old: ignore
    # ```
    # _*_________|______|__>
    # a0        -1h    now
    # ```
    #
    # case 4: only 1 alarm newer than 1 hour old: ignore
    # ```
    # __|__*____|__>
    #  -1h a0  now
    # ```
    #
    # case 0->1: (a: there can be 1 alarm more recent than 1 hour old to
    #             trigger match, plus at least 1 alarm older than 1 hour
    #             OR b:1->n alarms newer than 1 hour old)
    #             OR (both a and b)
    one_hour_ago: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    one_hour_ago_naive = one_hour_ago.replace(tzinfo=None)

    Alm = classes_orm.Alarm
    Tkt = classes_orm.Ticket

    # Colonne per ogni riga di dato finale.
    select_data = select(
        Alm.code,
        Alm.description,
        Alm.severity_level,
        Alm.plant_id,
        Alm.ticket_id,

        # Prendi il timestamp più recente del gruppo di allarmi.
        func.max(Alm.timestamp).label('latest_timestamp'),

        # Prendi il conteggio di tutti gli allarmi equivalenti.
        func.count().label('count'),

        # Prendi tutti gli id allarmi. Questo ci serve dopo per associarli
        # al nuovo ticket.
        func.group_concat(Alm.id).label('alarm_ids')
    )

    # Aggregazione per tipo di allarme.
    group_by_data = [
        Alm.code,                                                           
        Alm.description,                                                    
        Alm.severity_level,                                                 
        Alm.plant_id,                                                       
        Alm.ticket_id
    ]

    subquery = (
        select_data
        .where(
            # Ricerca allarmi non collegati a nessun ticket.
            # Serve a evitare ticket duplicati.
            Alm.ticket_id.is_(None)
        )
        .group_by(*group_by_data)
        .having(
            # Controlla solo gli allarmi più recenti di un ora a partire dall'
            # esecuzione di questa query.
            func.count().filter(Alm.timestamp >= one_hour_ago_naive) >= 1,  # At least one in the last hour
        )
    ).subquery()

    # Prendi tutti gli allarmi più vecchi di un'ora dello stesso tipo di quelli
    # della subquery.
    alarms_to_tickets = (
        select_data
        .where(
            and_(
                Alm.ticket_id.is_(None),
                and_(
                    Alm.code == subquery.c.code,
                    Alm.description == subquery.c.description,
                    Alm.severity_level == subquery.c.severity_level,
                    Alm.plant_id == subquery.c.plant_id
                )
            )
        )
        .group_by(*group_by_data)
        .having(
            # Ci devono essere >= 2 allarmi corrispondenti ai criteri.
            func.count() >= 2,
        )
    )

    # Esegui la query.
    results = db.session.execute(alarms_to_tickets).all()
    logging.info(results)

    if results:
        # Per ogni gruppo di allarmi apri un nuovo ticket.
        for code, desc, sl, plant_id, ticket_id, timestamp, count, alarm_ids in results:
            # Trasformo gli id in interi.
            alarm_ids: list[int] = [int(i) for i in alarm_ids.split(',')]

            # Creazione nuovo ticket.
            ticket_data = utils.new_db_object(
                Tkt(
                    code='NOT RESOLVED',
                    plant_id=plant_id,
                ),
                db,
                return_raw=True,
            )

            # Associa gli allarmi filtrati al nuovo ticket.
            alarms = db.session.query(Alm).filter(Alm.id.in_(alarm_ids)).all()
            (
                db.session.query(Alm)
                    .filter(Alm.id.in_(alarm_ids))
                    .update({Alm.ticket_id: ticket_data['id']},
                    synchronize_session=False
                )
            )

            # Aggiorna il DB.
            try:
                db.session.commit()
                db.session.flush()
            except IntegrityError as e:                         
                db.session.rollback()
                logging.error(f'IntegrityError: {str(e)}')
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f'SQLAlchemyError: {str(e)}')
            except Exception as e:
                db.session.rollback()
                logging.error(f'Unexpected error: {str(e)}')

            """
            # Controllo che il nuovo ticket abbia associato i nuovi allarmi.
            a = db.session.query(Alm).filter(Alm.id == alarm_ids[0])
            for e in a:
                logging.info(a)
            tk =  db.session.query(classes_orm.Ticket).filter(classes_orm.Ticket.id == ticket_data['id'])
            for j in tk[0].alarms:
                logging.info(j.id)
            """

    # Bisogna chiudere automaticamente i ticket con stato "NOT RESOLVED"
    # che non hanno un allarmi da 0 a -1 ora: questo significa che non c'è
    # stata attività recente dell'allarme.
    #
    # Teoricamente questa parte andrebbe in un crontab eseguito ogni ora, ma
    # per semplicità la facciamo qui.
    
    # 1. ricerca ticket "NOT RESOLVED" con allarme più recente più vecchio di
    # un'ora (-1 ora), ma assolutamente non anche con allarme da 0 a -1 ora
    tickets = (
        db.session.query(Tkt)

            # Ci servono i dati dei timestamp degli allarmi.
            .join(Tkt.alarms)
            .filter(Tkt.code == 'NOT RESOLVED')

            # Evita duplicati.
            .group_by(Tkt.id)
            .having(func.max(Alm.timestamp) <= one_hour_ago_naive)
            .all()
    )

    # 2. chiusura automatica ticket punto 1 e set visible=False per tutti gli
    # allarmi associati. Aggiornamento bulk.
    if tickets:
        ticket_ids = [ticket.id for ticket in tickets]

        # Segno i ticket come risolti.
        (
            db.session.query(Tkt)
                .filter(Tkt.id.in_(ticket_ids))
                .update({Tkt.code: 'SOLVED'}, synchronize_session=False)
        )

        # Tutti gli allarmi associati ai ticket filtrati sono da nascondere.
        (
            db.session.query(Alm)
                .filter(Alm.ticket_id.in_(ticket_ids))
                .update({Alm.visible: False}, synchronize_session=False)
        )

        # Aggiona il DB.
        db.session.commit()
        db.session.flush()



@app.route('/plant_module_system_sensor_reading', methods=['GET', 'POST'])
def rest_plant_module_system_sensor_reading():
    if request.method == 'GET':
        if 'plant_id' in request.args:
            element_found: bool = False

            # Cerca tutte le letture di sensore di modulo corrispondenti
            # all'impianto.
            plant_id: int = int(request.args.get('plant_id'))
            plant = utils.detail_raw_db_object(classes_orm.Plant, plant_id, db)
            if plant and plant.plant_module_system:
                element_found = True

                # Filtra tutti i PlantModuleSystemSensorReading che
                # hanno come
                #
                # plant_module_system_id == plant.plant_module_system.id
                # 
                # Questo ci permette di usare una sola query per
                # ottenere i dati
                # del grafico dell'impianto a partire dall' id dell'impianto.
                if 'results' in request.args:
                    # Opzionalmente prendi gli ultimi n risultati.
                    results: int = int(request.args.get('results'))

                    data = db.session.query(classes_orm.PlantModuleSystemSensorReading).filter(
                        classes_orm.PlantModuleSystemSensorReading.plant_module_system_id == plant.plant_module_system.id).order_by(
                            desc(classes_orm.PlantModuleSystemSensorReading.timestamp)
                        ).limit(results).all()

                    # Abbiamo bisogno del timestamp in formato UTC (Zulu) e il
                    # metodo serialize nel database lo implementa.
                    d: list[dict] = [obj.serialize() for obj in data]

                    # Ordina risultati per timestamp.
                    return jsonify(sorted(d, key=lambda x: x['timestamp'])), 200
                elif 'latest_reading_seconds' in request.args:
                    latest_reading_seconds: int = int(request.args.get('latest_reading_seconds'))
                    cutoff_time = datetime.datetime.now() - datetime.timedelta(seconds=latest_reading_seconds)

                    # Filtra i valori all'interno del range di tempo richiesto.
                    data = db.session.query(classes_orm.PlantModuleSystemSensorReading).filter(
                        classes_orm.PlantModuleSystemSensorReading.plant_module_system_id == plant.plant_module_system.id,
                        classes_orm.PlantModuleSystemSensorReading.timestamp >= cutoff_time,
                        classes_orm.PlantModuleSystemSensorReading.timestamp <= datetime.datetime.now()
                    ).all()

                    d: list[dict] = [obj.serialize() for obj in data]
                    return jsonify(sorted(d, key=lambda x: x['timestamp'])), 200
                else:
                    data = db.session.query(
                            classes_orm.PlantModuleSystemSensorReading).filter(
                                classes_orm.PlantModuleSystemSensorReading.plant_module_system_id == plant.plant_module_system.id
                                    ).all()

                    d = [obj.serialize() for obj in data]
                    return jsonify(d), 200

            if not element_found:
                return jsonify({'error': 'plant_id or plant.plant_module_system found'}), 404

        return utils.list_db_objects(classes_orm.PlantModuleSystemSensorReading, db)
    elif request.method == 'POST':
        token = request.headers.get('Authorization')

        if token and token.startswith('Bearer '):
            token_str = token.split(' ')[1]
            if is_valid_token(token_str):

                ok, new_data = utils.validate_json(json_http_schema.PlantModuleSystemSensorReadingSchema, request.data)
                if not ok:
                    return new_data

                plant_module_system = utils.detail_db_object(classes_orm.PlantModuleSystem, new_data.plant_module_system_id, db, False, 'owner')
                if plant_module_system is None:
                    return jsonify({'error': f'plant_module_system {new_data.plant_module_system_id} not found'}), 404
              
                # Controlla i range dei dati e attiva gli allarmi se necessario.
                new_issues(new_data, plant_module_system, db)

                return utils.new_db_object(
                    classes_orm.PlantModuleSystemSensorReading(
                        voltage=new_data.voltage,
                        current=new_data.current,
                        frequency=new_data.frequency,
                        timestamp=new_data.timestamp,
                        plant_module_system=plant_module_system,
                        alarm_code=new_data.alarm_code,
                    ),
                    db
                )
            else:
                return jsonify({'error': f'invalid API token'}), 401
        else:
            return jsonify({'error': f'API token is missing from headers'}), 401


@app.route('/plant_module_system_sensor_reading/<int:plant_module_system_sensor_reading_id>', methods=['GET', 'PUT'])
def rest_show_plant_module_system_sensor_reading(plant_module_system_sensor_reading_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.PlantModuleSystemSensorReading, plant_module_system_sensor_reading_id, db)
    elif request.method == 'PUT':
        pass


@app.route('/plant_battery_system_sensor_reading', methods=['GET', 'POST'])
def rest_plant_battery_system_sensor_reading():
    if request.method == 'GET':

        # Ricerca per id batteria
        if ('battery_id' in request.args
           and 'results' in request.args):
            # Prendi gli ultimi n risultati.
            results: int = int(request.args.get('results'))
            battery_id: int = int(request.args.get('battery_id'))

            data = db.session.query(classes_orm.PlantBatterySystemSensorReading).filter(
                classes_orm.PlantBatterySystemSensorReading.battery_id == battery_id).order_by(
                    desc(classes_orm.PlantBatterySystemSensorReading.timestamp)
                ).limit(results).all()

            # Abbiamo bisogno del timestamp in formato UTC (Zulu) e il
            # metodo serialize nel database lo implementa.
            d: list[dict] = [obj.serialize() for obj in data]

            # Ordina risultati per timestamp.
            try:
                return jsonify(sorted(d, key=lambda x: x['timestamp'])), 200
            except TypeError:
                return jsonify(d), 200

        elif ('plant_id' in request.args
           and 'battery_type' in request.args
           and request.args.get('battery_type') in ['master', 'slave']):
            element_found: bool = False

            # Cerca tutte le letture di sensore di batteria corrispondenti
            # all'impianto e al tipo di batteria passato ('master' o 'slave').
            plant_id: int = int(request.args.get('plant_id'))
            plant = utils.detail_raw_db_object(classes_orm.Plant, plant_id, db)
            if plant and plant.plant_battery_system:

                batteries = plant.plant_battery_system.batteries

                for battery in batteries:
                    if battery.battery_specification.type == request.args.get('battery_type'):
                        element_found = True

                        battery_id = battery.id

                        if 'latest_reading_seconds' in request.args:
                            latest_reading_seconds: int = int(request.args.get('latest_reading_seconds'))
                            cutoff_time = datetime.datetime.now() - datetime.timedelta(seconds=latest_reading_seconds)

                            # Filtra i valori all'interno del range di tempo richiesto.
                            data = db.session.query(classes_orm.PlantBatterySystemSensorReading).filter(
                                classes_orm.PlantBatterySystemSensorReading.battery_id == battery_id,
                                classes_orm.PlantBatterySystemSensorReading.timestamp >= cutoff_time,
                                classes_orm.PlantBatterySystemSensorReading.timestamp <= datetime.datetime.now()
                            ).all()

                            d: list[dict] = [obj.serialize() for obj in data]
                            return jsonify(sorted(d, key=lambda x: x['timestamp'])), 200

                        else:
                            # Filtra tutti i PlantBatterySystemSensorReading che
                            # hanno come
                            #
                            # battery_id == plant.plant_battery_system.batteries
                            # 
                            # e lo stesso tipo di batteria passato.
                            #
                            # Questo ci permette di usare una sola query per
                            # ottenere i dati
                            # del grafico batterie (master e slave separati ) a
                            # partire dall'impianto.
                            data = db.session.query(
                                    classes_orm.PlantBatterySystemSensorReading).filter(
                                        classes_orm.PlantBatterySystemSensorReading.battery_id == battery_id
                                            ).all()
                            d = [obj.serialize() for obj in data]
                            return jsonify(d), 200


            if not element_found:
                return jsonify({'error': 'plant_id, plant.plant_battery_system, plant.plant_battery_system.battery or battery.battery_specification.type not found'}), 404

        else:
            return utils.list_db_objects(classes_orm.PlantBatterySystemSensorReading, db)
    elif request.method == 'POST':
        token = request.headers.get('Authorization')                            
                                                                                
        if token and token.startswith('Bearer '):                                                       
            token_str = token.split(' ')[1]                                     
            if is_valid_token(token_str):

                ok, new_data = utils.validate_json(json_http_schema.PlantBatterySystemSensorReadingSchema, request.data)
                if not ok:
                    return new_data

                battery = utils.detail_db_object(classes_orm.Battery, new_data.battery_id, db, False, 'battery')
                if battery is None:
                    return jsonify({'error': f'battery {new_data.battery_id} not found'}), 404

                new_issues(new_data, battery, db)

                return utils.new_db_object(
                    classes_orm.PlantBatterySystemSensorReading(
                        voltage=new_data.voltage,
                        current=new_data.current,
                        frequency=new_data.frequency,
                        timestamp=new_data.timestamp,
                        battery=battery,
                        alarm_code=new_data.alarm_code,
                    ),
                    db
                )

            else:
                return jsonify({'error': f'invalid API token'}), 401
        else:
            return jsonify({'error': f'API token is missing from headers'}), 401


@app.route('/plant_battery_system_sensor_reading/<int:plant_battery_system_sensor_reading_id>', methods=['GET', 'PUT'])
def rest_show_plant_battery_system_sensor_reading(plant_battery_system_sensor_reading_id):
    if request.method == 'GET':
        return utils.detail_db_object(classes_orm.PlantBatterySystemSensorReading, plant_battery_system_sensor_reading_id, db)
    elif request.method == 'PUT':
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
