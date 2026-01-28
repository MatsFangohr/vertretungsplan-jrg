import datetime as dt

from pydantic import BaseModel, ConfigDict


class SchoolClassModel(BaseModel):
    year: int
    letter: str

    model_config = ConfigDict(from_attributes=True)


class HourInfoModel(BaseModel):
    start: int
    end: int

    model_config = ConfigDict(from_attributes=True)


class TimetableChangeModel(BaseModel):
    date: dt.date
    klass: SchoolClassModel
    hours: HourInfoModel
    lessonname: str
    teacher: str
    message: str
    canceled: bool
    originalteacher: str

    model_config = ConfigDict(from_attributes=True)
