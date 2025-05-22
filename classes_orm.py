from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, relationship, declarative_base, deferred, declared_attr 
import uuid
from dataclasses import dataclass, field
import datetime
from typing import Optional, Tuple , Any
from enum import Enum
import pprint

Base = declarative_base()

class BatteryType(Enum):
    MASTER = 'master'
    SLAVE = 'slave'
 
 
class CurrentType(Enum):
    DC = 'dc'
    AC = 'ac'


class PlantStatus(Enum):
    OK = 'ok'
    ERROR = 'error'


class AlarmSeverityLevel(Enum):
    LOW = 'basso'
    MEDIUM = 'medio'
    HIGH = 'alto'


class AlarmCode(Enum):
    NO_PROBLEM = '-01'
    SOFTWARE_PROBLEM = '00'
    DC_PROBLEM = '01'
    BMS_PROBLEM = '02'
    SLAVE_BATTERY_PROBLEM = '03'
    PLANT_COMPONENT_PROBLEM = '04'


class TicketCode(Enum):
    IN_PROGRESS = 'IN PROGRESS'
    RESOLVED = 'RESOLVED'
    NOT_RESOLVED = 'NOT RESOLVED'


class Alarm(Base):
    __tablename__ = 'alarms'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    severity_level: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # 1 allarme appartiene ad 1 impianto.
    plant_id: Mapped[int] = mapped_column(Integer, ForeignKey('plants.id'), nullable=True)
    plant: Mapped['Plant'] = relationship(
        'Plant',
        back_populates='alarms',
        foreign_keys=[plant_id]
    )

    # 1 allarme appartiene ad 1 ticket.
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey('tickets.id'), nullable=True)
    ticket: Mapped['Ticket'] = relationship(
        'Ticket',
        back_populates='alarms',
        foreign_keys=[ticket_id]
    )

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'severity_level': self.severity_level,
            'timestamp': self.timestamp.astimezone(datetime.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds') + 'Z' if self.timestamp else None,
            'plant_id': self.plant_id,
            'ticket_id': self.ticket_id,
            'visible': self.visible,
        }


class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False)

    # 1 ticket sarà collegato ad n allarmi dello stesso tipo, in base a certe
    # regole.
    alarms: Mapped[list['Alarm']] = relationship('Alarm', back_populates='ticket')

    # 1 ticket appartiene ad 1 impianto.
    plant_id: Mapped[int] = mapped_column(Integer, ForeignKey('plants.id'), nullable=True)
    plant: Mapped['Plant'] = relationship(
        'Plant',
        back_populates='tickets',
        foreign_keys=[plant_id]
    )

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'code': self.code,

            # Ordina gli allarmi in modo decrescente di timestamp: l'allarme        
            # con timestamp più recente deve essere primo della lista degli id      
            # allarmi. Questo ci servirà nel frontend.
            'alarms': [a.id for a in sorted(self.alarms, key=lambda a: a.timestamp, reverse=True)],
            'plant_id': self.plant_id,
        }


@dataclass
class Token(Base):
    __tablename__ = 'tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'api_token': self.api_token,
        }


@dataclass
class ContactInfo(Base):
    __tablename__ = 'contact_infos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)

    owners: Mapped[list['Owner']] = relationship('Owner', back_populates='contact_info')

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'phone_number': self.phone_number
        }


@dataclass
class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    street: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    zip_code: Mapped[str] = mapped_column(String, nullable=False)

    # 1 indirizzo può appartenere ad n proprietari.
    owners: Mapped[list['Owner']] = relationship('Owner', back_populates='address')

    # Metodo per visualizzare i dati dall'API.
    def serialize(self) -> dict:
        return {
            'id': self.id,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code
        }


@dataclass
class Owner(Base):
    __tablename__ = 'owners'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    # Opzionali, non li prendiamo in considerazione.
    address_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('addresses.id'))
    contact_info_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('contact_infos.id'))

    # 1 proprietario può appartenere ad 1 solo indirizzo.
    address: Mapped[Optional[Address]] = relationship("Address", back_populates="owners")
    # 1 proprietario può appartenere ad 1 solo indirizzo.
    contact_info: Mapped[Optional[Address]] = relationship("ContactInfo", back_populates="owners")

    # Ad 1 proprietario possono corrispondere n impianti.
    plants: Mapped[list['Plant']] = relationship('Plant', back_populates='owner')

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address_id': self.address_id,
            'contact_info_id': self.contact_info_id
        }


@dataclass
class SensorReading(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    voltage: Mapped[float] = mapped_column(Float, nullable=False)
    current: Mapped[float] = mapped_column(Float, nullable=False)

    # La frequenza non ha senso per la corrente DC.
    frequency: Mapped[Optional[float]] = mapped_column(Float, default=0.0)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    alarm_code: Mapped[str] = mapped_column(String, nullable=False, default='-01')


class PlantModuleSystemSensorReading(SensorReading):
    # Singola lettura sensore per un modulo dell'impianto.
    __tablename__ = 'plant_module_system_sensor_readings'

    plant_module_system_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('plant_module_systems.id'), nullable=True)

    plant_module_system: Mapped[Optional['PlantModuleSystem']] = relationship('PlantModuleSystem', back_populates='plant_module_system_sensor_readings', foreign_keys=[plant_module_system_id])

    def __init__(self, voltage: float, current: float, timestamp: datetime.datetime, plant_module_system: Any, frequency: float = 0.0, alarm_code: str = '-01'):
        self.voltage = voltage
        self.current = current

        # La frequenza non ha senso per la corrente DC.
        self.frequency = frequency

        self.timestamp = timestamp

        self.alarm_code = alarm_code
        self.plant_module_system = plant_module_system


    def serialize(self) -> dict:
        return {
            'id': self.id,
            'voltage': self.voltage,
            'current': self.current,
            'timestamp': self.timestamp.astimezone(datetime.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds') + 'Z' if self.timestamp else None,
            'frequency': self.frequency,
            'alarm_code': self.alarm_code,
            'plant_module_system_id': self.plant_module_system_id,
        }


class PlantBatterySystemSensorReading(SensorReading):
    # Singola lettura sensore per una batteria dell'impianto.

    __tablename__ = 'plant_battery_system_sensor_readings'

    # 1 lettura appartiene ad una sola batteria.
    battery_id: Mapped[int] = mapped_column(Integer, ForeignKey('batteries.id'), nullable=True)

    battery: Mapped['PlantBatterySystem'] = relationship(
        'Battery',
        back_populates='plant_battery_system_sensor_readings',
        foreign_keys=[battery_id]
    )

    def __init__(self, voltage: float, current: float, timestamp: datetime.datetime, battery: Any, frequency: float = 0.0, alarm_code: str = '-01'):
        self.voltage = voltage
        self.current = current

        # La frequenza non ha senso per la corrente DC, quindi anche per le batterie.
        self.frequency = 0.0

        self.timestamp = timestamp
        self.alarm_code = alarm_code

        self.battery = battery


    def serialize(self) -> dict:
        return {
            'id': self.id,
            'voltage': self.voltage,
            'current': self.current,
            'timestamp': self.timestamp.astimezone(datetime.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds') + 'Z' if self.timestamp else None,
            'frequency': self.frequency,
            'alarm_code': self.alarm_code,
            'battery_id': self.battery_id,
        }


@dataclass
class Limit(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lower: Mapped[float] = mapped_column(Float, nullable=False)
    upper: Mapped[float] = mapped_column(Float, nullable=False)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'lower': self.lower,
            'upper': self.upper,
        }


@dataclass
class VoltageRange(Limit):
    # Range di valori.
    __tablename__ = 'voltage_ranges'

    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper


@dataclass
class CurrentRange(Limit):
    __tablename__ = 'current_ranges'

    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper


@dataclass
class FrequencyRange(Limit):
    __tablename__ = 'frequency_ranges'

    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper


@dataclass
class PowerRange(Limit):
    __abstract__ = True

    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper


@dataclass
class DailyPowerRange(PowerRange):
    __tablename__ = 'daily_power_ranges'

    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper


@dataclass
class MonthlyPowerRange(PowerRange):
    __tablename__ = 'monthly_power_ranges'

    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper


class BatterySpecification(Base):
    __tablename__ = 'battery_specifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Tipo batteria. Di solito può essere solo 'master' o 'slave'.
    type: Mapped[str] = mapped_column(String, nullable=False)

    voltage_range_id: Mapped[int] = mapped_column(Integer, ForeignKey('voltage_ranges.id'))
    current_range_id: Mapped[int] = mapped_column(Integer, ForeignKey('current_ranges.id'))

    # In kWh.
    capacity: Mapped[float] = mapped_column(Float, nullable=False)

    voltage_range: Mapped['VoltageRange'] = relationship('VoltageRange', foreign_keys=[voltage_range_id])
    current_range: Mapped['CurrentRange'] = relationship('CurrentRange', foreign_keys=[current_range_id])

    # 1 specifica di batteria può appartenere a n batterie.
    batteries: Mapped[list['Battery']] = relationship('Battery', back_populates='battery_specification')

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
            'voltage_range_id': self.voltage_range_id,
            'current_range_id': self.current_range_id,
            'capacity': self.capacity,
        }


@dataclass
class Battery(Base):
    __tablename__ = 'batteries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    battery_specification_id: Mapped[int] = mapped_column(Integer, ForeignKey('battery_specifications.id'))
    plant_battery_system_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('plant_battery_systems.id'), nullable=True)

    name: Mapped[str] = mapped_column(String, nullable=False, default='battery')

    # 1 batteria può appartenere ad 1 sola specifica di batteria.
    battery_specification: Mapped['BatterySpecification'] = relationship('BatterySpecification', foreign_keys=[battery_specification_id])

    # Ad 1 sistema batteria possono corrispondere n batterie.
    plant_battery_system: Mapped['PlantBatterySystem'] = relationship('PlantBatterySystem', back_populates='batteries', foreign_keys=[plant_battery_system_id])

    # Ad 1 batteria possono corrispondere n letture di sensori. 
    plant_battery_system_sensor_readings: Mapped[list['PlantBatterySystemSensorReading']] = relationship('PlantBatterySystemSensorReading', back_populates='battery')

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'battery_specification_id': self.battery_specification_id,
            'plant_battery_system_id': self.plant_battery_system_id,
            'sensor_readings': [s.id for s in self.plant_battery_system_sensor_readings],
            'name': self.name,
        }



class CurrentSystem(Base):
    # Tabella per identificare corrente AC o DC.
    # Ogni impianto ha 2 sistemi corrente: `AC` e `DC`
    __abstract__ = True

    @declared_attr
    def id(cls) -> Mapped[int]:
        return mapped_column(Integer, primary_key=True)

    @declared_attr
    def voltage_range_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey('voltage_ranges.id'))

    @declared_attr
    def current_range_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey('current_ranges.id'))

    @declared_attr
    def voltage_range(cls) -> Mapped['VoltageRange']:
        return relationship('VoltageRange', foreign_keys=[cls.voltage_range_id])

    @declared_attr
    def current_range(cls) -> Mapped['CurrentRange']:
        return relationship('CurrentRange', foreign_keys=[cls.current_range_id])


@dataclass
class DcCurrentSystem(CurrentSystem):
    __tablename__ = 'dc_current_systems'

    # Il frequency_range per corrente di tipo DC è sempre 0, per cui non
    # è compreso qui.

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'voltage_range_id': self.voltage_range_id,
            'current_range_id': self.current_range_id,
        }


@dataclass
class AcCurrentSystem(CurrentSystem):
    __tablename__ = 'ac_current_systems'

    frequency_range_id: Mapped[int] = mapped_column(Integer, ForeignKey('frequency_ranges.id'))
    frequency_range: Mapped['FrequencyRange'] = relationship('FrequencyRange', foreign_keys=[frequency_range_id])

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'voltage_range_id': self.voltage_range_id,
            'current_range_id': self.current_range_id,
            'frequency_range_id': self.frequency_range_id,
        }


@dataclass
class PlantModuleSystem(Base):
    # Tabella per legare i sistemi di corrente alle letture attuali,
    # (non batterie) di un impianto.
    __tablename__ = 'plant_module_systems'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String, nullable=False, default=lambda: str(uuid.uuid4()))
    ac_current_id: Mapped[int] = mapped_column(Integer, ForeignKey('ac_current_systems.id'))
    dc_current_id: Mapped[int] = mapped_column(Integer, ForeignKey('dc_current_systems.id'))

    ac_current: Mapped['AcCurrentSystem'] = relationship('AcCurrentSystem', foreign_keys=[ac_current_id])
    dc_current: Mapped['DcCurrentSystem'] = relationship('DcCurrentSystem', foreign_keys=[dc_current_id])

    # In kWh.
    capacity: Mapped[float] = mapped_column(Float, nullable=False)

    # Marca.
    make: Mapped[str] = mapped_column(String, nullable=False)

    # Ad 1 modulo possono appartenere n letture di sensori.
    plant_module_system_sensor_readings: Mapped[list['PlantModuleSystemSensorReading']] = relationship('PlantModuleSystemSensorReading', back_populates='plant_module_system')

    # Ad 1 modulo impianto corrisponde 1 impianto: relazione 1 a 1.
    #
    # Dalla documentazione di SQLAlchemy:
    #
    #   If a scalar is desired where normally a list would be present, such as a bi-directional one-to-one relationship, use an appropriate Mapped annotation or set relationship.uselist to False.
    plant: Mapped['Plant'] = relationship('Plant', back_populates='plant_module_system', uselist=False)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'uuid': self.uuid,
            'make': self.make,
            'ac_current_id': self.ac_current_id,
            'dc_current_id': self.dc_current_id,
            'sensor_readings_ids': [s.id for s in self.plant_module_system_sensor_readings],
            'plant_id': self.plant.id if self.plant is not None else None
        }


@dataclass
class PlantBatterySystem(Base):
    # Tabella per legare le batterie alle letture attuali di un impianto.
    __tablename__ = 'plant_battery_systems'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String, nullable=False, default=lambda: str(uuid.uuid4()))

    # Marca.
    make: Mapped[str] = mapped_column(String, nullable=False)

    # Ad 1 sistema batteria possono appartenere n batterie.
    batteries: Mapped[list['Battery']] = relationship('Battery', back_populates='plant_battery_system')

    # A 1 sistema batterie corrisponde esattamente 1 impianto.
    plant: Mapped['Plant'] = relationship('Plant', back_populates='plant_battery_system', uselist=False)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'uuid': self.uuid,
            'make': self.make,
            'battery_ids': [b.id for b in self.batteries],
            'plant_id': self.plant.id if self.plant is not None else None
        }


@dataclass
class PlantProduction(Base):
    # Tabella per la produzione in KWh di un impianto.
    __tablename__ = 'plant_productions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Valori attuali.
    daily_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_kwh: Mapped[float] = mapped_column(Float, nullable=False)

    daily_power_range_id: Mapped[int] = mapped_column(Integer, ForeignKey('daily_power_ranges.id'), unique=True)

    # A 1 produzione impianto corrisponde esattamente 1 range giornaliero.
    daily_power_range: Mapped['DailyPowerRange'] = relationship('DailyPowerRange', foreign_keys=[daily_power_range_id])

    monthly_power_range_id: Mapped[int] = mapped_column(Integer, ForeignKey('monthly_power_ranges.id'), unique=True)

    # A 1 produzione impianto corrisponde esattamente 1 range mensile.
    monthly_power_range: Mapped['MonthlyPowerRange'] = relationship('MonthlyPowerRange', foreign_keys=[monthly_power_range_id])

    # A 1 produzione impianto corrisponde esattamente 1 impianto.
    plant: Mapped['Plant'] = relationship('Plant', back_populates='plant_production', uselist=False)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'daily_kwh': self.daily_kwh,
            'monthly_kwh': self.monthly_kwh,
            'daily_power_range_id': self.daily_power_range_id,
            'monthly_power_range_id': self.monthly_power_range_id,
            'plant_id': self.plant.id if self.plant is not None else None
        }


@dataclass
class Plant(Base):
    # Tabella principale del database che rappresenta l'impianto.
    __tablename__ = 'plants'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String, nullable=False, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False, default='new plant')
    installer: Mapped[str] = mapped_column(String, nullable=False, default='Installer Ltd.')

    # Ad 1 impianto corrisponde 1 proprietario.
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('owners.id'))
    owner: Mapped['Owner'] = relationship('Owner', foreign_keys=[owner_id])

    # Ad 1 impianto corrisponde 1 modulo impianto.
    plant_module_system_id: Mapped[int] = mapped_column(Integer, ForeignKey('plant_module_systems.id'), unique=True)
    plant_module_system: Mapped['PlantModuleSystem'] = relationship('PlantModuleSystem', back_populates='plant', foreign_keys=[plant_module_system_id])

    # Ad 1 impianto corrisponde 1 sistema batterie.
    plant_battery_system_id: Mapped[int] = mapped_column(Integer, ForeignKey('plant_battery_systems.id'), unique=True)
    plant_battery_system: Mapped['PlantBatterySystem'] = relationship('PlantBatterySystem', back_populates='plant', foreign_keys=[plant_battery_system_id])

    # Ad 1 impianto corrisponde 1 produzione impianto.
    plant_production_id: Mapped[int] = mapped_column(Integer, ForeignKey('plant_productions.id'), unique=True)
    plant_production: Mapped['PlantProduction'] = relationship('PlantProduction', back_populates='plant', foreign_keys=[plant_production_id])

    # Ad 1 batteria possono corrispondere n letture di sensori. 
    alarms: Mapped[list['Alarm']] = relationship('Alarm', back_populates='plant')
    tickets: Mapped[list['Ticket']] = relationship('Ticket', back_populates='plant')

    status: Mapped[str] = mapped_column(String, nullable=False, default=PlantStatus['OK'].value)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'owner_id': self.owner_id,
            'plant_module_system_id': self.plant_module_system_id,
            'plant_battery_system_id': self.plant_battery_system_id,
            'plant_production_id': self.plant_production_id,
            'installer': self.installer,
            'alarms': [a.id for a in self.alarms],
            'tickets': [t.id for t in self.tickets],
            'status': self.status
        }


if __name__ == '__main__':
    pass
