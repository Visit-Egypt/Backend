from ctypes import Union
import mergedeep
import pycountry
from datetime import datetime
from bson.objectid import ObjectId, InvalidId
from pydantic import BaseModel, BaseConfig, ValidationError
from pydantic.error_wrappers import ErrorWrapper
from typing import Dict


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")


class MongoModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }

    @classmethod
    def from_mongo(cls, data: dict, lang: str = 'en'):
        """We must convert _id into "id"."""
        if not data:
            return data
        id = data.pop("_id", None)
        new_data = dict(data, id=id)
        if data.get('translations'): 
            lang_data = data.get('translations').get(lang)
            print(lang_data)
            mergedeep.merge(new_data, lang_data)
            
        return cls(**new_data)

    def mongo(self, **kwargs):
        exclude_unset = kwargs.pop("exclude_unset", True)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.dict(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = parsed.pop("id")

        return parsed


class Translatable(Dict[str, BaseModel]):
    """
    Validate Translation Dict Field (Json) where Language is Key and Translation as Value
        Languages : ISO 639-1 code
        Translation : Dict (Contains the translations), None

    ref:
    - https://pydantic-docs.helpmanual.io/usage/types/#classes-with-__get_validators__

    By: Khalid Murad
    """

    @property
    def __translation_interface__(self):
        return self.dict()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, base_dictionary):
        result = dict()
        dictionary = dict()
        errors = []

        dictionary = base_dictionary

        for key in dictionary:
            try:
                parsed_language = pycountry.languages.get(alpha_2=key.upper())
            except ValueError as exc:
                errors.append(ErrorWrapper(Exception(f"Invalid language: {key}."), loc="language"))
            if not parsed_language:
                errors.append(ErrorWrapper(Exception(f"Invalid language: {key}."), loc="language"))
            if isinstance(dictionary[key], BaseModel):
                result[key] = dictionary[key]
            else:
                errors.append(ErrorWrapper(Exception(f"Invalid content for language: {key}."), loc=("language","content")))

        if errors:
            raise ValidationError(
            errors,
            cls,
            )

        return cls(result)