from mashumaro.mixins.json import DataClassJSONMixin
from dataclasses import dataclass
import classes_orm
import datetime
import typing


@dataclass
class OwnerSchema(DataClassJSONMixin):
    first_name: str
    last_name: str


@dataclass
class TokenSchema(DataClassJSONMixin):
    api_token: str


@dataclass
class LimitSchema(DataClassJSONMixin):
    lower: float
    upper: float

    # upper must be > lower.
    def __post_init__(self):
        if self.lower >= self.upper:
            raise ValueError('field "lower" must be greater than field "upper"')


@dataclass
class VoltageRangeSchema(LimitSchema):
    pass


@dataclass
class CurrentRangeSchema(LimitSchema):
    pass


@dataclass
class PowerRangeSchema(LimitSchema):
    pass


@dataclass
class DailyPowerRangeSchema(PowerRangeSchema):
    pass


@dataclass
class MonthlyPowerRangeSchema(PowerRangeSchema):
    pass


@dataclass
class FrequencyRangeSchema(LimitSchema):
    pass


@dataclass
class AlarmSchema(DataClassJSONMixin):
    code: str
    description: str
    severity_level: str
    timestamp: datetime.datetime

    def __post_init__(self):
        # Prendi uno dei valori validi dalle enumerazioni.
        valid_values: list[code] = [e.value for e in classes_orm.AlarmCode]
        if self.code not in valid_values:
            raise ValueError(f'field "code" must be one of {valid_values}')

        valid_values: list[str] = [e.value for e in classes_orm.AlarmSeverityLevel]
        if self.severity_level not in valid_values:
            raise ValueError(f'field "severity_level" must be one of {valid_values}')

        self.code = self.code
        self.type = self.severity_level


@dataclass
class TicketSchema(DataClassJSONMixin):
    code: str
    alarm_ids: list[int]

    def __post_init__(self):
        # Prendi uno dei valori validi dalle enumerazioni.
        valid_values: list[code] = [e.value for e in classes_orm.TicketCode]
        if self.code not in valid_values:
            raise ValueError(f'field "code" must be one of {valid_values}')

        self.code = self.code


@dataclass
class BatterySpecificationSchema(DataClassJSONMixin):
    type: str
    voltage_range_id: int
    current_range_id: int
    capacity: float

    def __post_init__(self):
        # Prendi uno dei valori validi dalle enumerazioni.
        valid_values: list[str] = [e.value for e in classes_orm.BatteryType]
        if self.type not in valid_values:
            raise ValueError(f'field "name" must be one of {valid_values}')

        self.type = classes_orm.BatteryType[self.type.upper()].value


@dataclass
class BatterySchema(DataClassJSONMixin):
    name: str
    battery_specification_id: int


@dataclass
class PlantModuleSystemSchema(DataClassJSONMixin):
    ac_current_id: int
    dc_current_id: int
    capacity: float
    make: str = 'unknown'


@dataclass
class CurrentSystemSchema(DataClassJSONMixin):
    voltage_range_id: int
    current_range_id: int


@dataclass
class AcCurrentSystemSchema(CurrentSystemSchema):
    frequency_range_id: int


@dataclass
class DcCurrentSystemSchema(CurrentSystemSchema):
    pass


@dataclass
class PlantBatterySystemSchema(DataClassJSONMixin):
    battery_ids: list[int]
    make: str = 'unknown'


@dataclass
class PlantProductionSchema(DataClassJSONMixin):
    daily_kwh: float
    monthly_kwh: float
    daily_power_range_id: int
    monthly_power_range_id: int


@dataclass
class PlantSchema(DataClassJSONMixin):
    name: str
    owner_id: int
    plant_module_system_id: int
    plant_battery_system_id: int
    plant_production_id: int
    installer: str


@dataclass
class SensorReadingSchema(DataClassJSONMixin):
    voltage: float
    current: float
    frequency: float
    timestamp: datetime.datetime

    def __post_init__(self):
        # Prendi uno dei valori validi dalle enumerazioni.
        valid_values: list[code] = [e.value for e in classes_orm.AlarmCode]
        if self.alarm_code not in valid_values:
            raise ValueError(f'field "alarm_code" must be one of {valid_values}')


@dataclass
class PlantModuleSystemSensorReadingSchema(SensorReadingSchema):
    plant_module_system_id: int
    alarm_code: typing.Optional[str] = '-01'


@dataclass
class PlantBatterySystemSensorReadingSchema(SensorReadingSchema):
    battery_id: int
    alarm_code: typing.Optional[str] = '-01'
