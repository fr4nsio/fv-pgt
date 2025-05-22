import classes_orm
from eralchemy import render_er


# Plant
render_er(
    classes_orm.Base,
    '../img/dbschema/0_plants.png',
    include_tables=[
        'plants', 
        'plant_module_systems',
        'plant_battery_systems',
        'owners',
        'plant_productions',
    ],
    exclude_columns=[
        'address_id',
        'contact_info_id',
        'first_name',
        'last_name',
        'make',
        'ac_current_id',
        'dc_current_id',
        'capacity',
        'daily_kwh',
        'monthly_kwh',
        'daily_power_range_id',
        'monthly_power_range_id',
    ]
)

# PlantModuleSystem
render_er(
    classes_orm.Base,
    '../img/dbschema/1_plant_module_systems.png',
    include_tables=[
        'plants', 
        'plant_module_systems',
        'ac_current_systems',
        'dc_current_systems',
        'plant_module_system_sensor_readings',
    ],
    exclude_columns=[
        'alarm_code',
        'current',
        'frequency',
        'timestamp',
        'voltage',
#        'plant_module_system_id',
        'installer',
        'name',
        'owner_id',
        'current_range_id',
        'frequency_range_id',
        'voltage_range_id',
        'plant_battery_system_id',
        'plant_production_id',
        'status',
    ]
)

# PlantBatterySystem
render_er(
    classes_orm.Base,
    '../img/dbschema/2_plant_battery_systems.png',
    include_tables=[
        'plant_battery_systems',
        'plants',
        'batteries',
    ],
    exclude_columns=[
        # Battery
        'current_range_id',
        'frequency_range_id',
        'voltage_range_id',
        'battery_specification',
        'battery_specification_id',

        # Plant
        'owner_id',
        'name',
        'installer',
        'name',
        'plant_module_system_id',
        'plant_production_id',
        'status',
    ]
)

# Battery
render_er(
    classes_orm.Base,
    '../img/dbschema/3_batteries.png',
    include_tables=[
        'batteries',
        'battery_specifications',
        'plant_battery_systems',
        'plant_battery_system_sensor_readings',
    ],
    exclude_columns=[
        # BatterySpecification
        'capacity',
        'current_range_id',
        'type',
        'voltage_range_id',

        # PlantBatterySystem
        'make',
        'uuid',

        # PlantBatterySystemSensorReading
        'alarm_code',
        'current',
        'frequency',
        'timestamp',
        'voltage',
    ]
)

# PlantModuleSystemSensorReading
render_er(
    classes_orm.Base,
    '../img/dbschema/4_plant_module_system_sensor_readings.png',
    include_tables=[
        'plant_module_system_sensor_readings',
        'plant_module_systems',
    ],
    exclude_columns=[
        'ac_current_id',
        'capacity',
        'dc_current_id',
        'make',
        'uuid',
    ],
)

# PlantBatterySystemSensorReading
render_er(
    classes_orm.Base,
    '../img/dbschema/5_plant_battery_system_sensor_readings.png',
    include_tables=[
        'plant_battery_system_sensor_readings',
        'batteries',
    ],
    exclude_columns=[
        'battery_specification_id',
        'name',
        'plant_battery_system_id',
    ],

)

# Alarm
render_er(
    classes_orm.Base,
    '../img/dbschema/6_alarms.png',
    include_tables=[
        'alarms',
        'tickets',
        'plants',
    ],
    exclude_columns=[
        # Plant
        'installer',
        'name',
        'owner_id',
        'plant_battery_system_id',
        'plant_module_system_id',
        'plant_production_id',
        'status',
        'uuid',
    ],
)

# Ticket
render_er(
    classes_orm.Base,
    '../img/dbschema/7_tickets.png',
    include_tables=[
        'tickets',
        'alarms',
        'plants',
    ],
    exclude_columns=[
        # Alarm
        'description',
        'severity_level',
        'timestamp',
        'visible',

        # Plant
        'installer',
        'name',
        'owner_id',
        'plant_battery_system_id',
        'plant_module_system_id',
        'plant_production_id',
        'status',
        'uuid',

    ],
)

# Full schema.
render_er(
    classes_orm.Base,
    '../img/dbschema/100_full.png',
)
