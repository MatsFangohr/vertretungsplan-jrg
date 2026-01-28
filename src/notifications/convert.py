from pydantic import TypeAdapter

from notifications.models import TimetableChangeModel
from untis.types import TimetableChange

ttchange_adapter = TypeAdapter(list[TimetableChange])
model_adapter = TypeAdapter(list[TimetableChangeModel])


def models_to_json(models: list[TimetableChangeModel]) -> bytes:
    return model_adapter.dump_json(models)


def json_to_models(data: bytes) -> list[TimetableChangeModel]:
    return model_adapter.validate_json(data)


def models_to_untis(models: list[TimetableChangeModel]) -> list[TimetableChange]:
    return ttchange_adapter.validate_python([m.model_dump() for m in models])


def untis_to_models(change: list[TimetableChange]) -> list[TimetableChangeModel]:
    return model_adapter.validate_python(change)
