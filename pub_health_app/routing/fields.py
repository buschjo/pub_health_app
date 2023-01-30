# app/fields.py

from django.db import models

class IntegerListField(models.CharField):

    description = 'list of integers'

    def from_db_value(self, value, expression, connection):
        if value is None or value == "":
            return None
        return list(map(int, value.split(',')))

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return None
        return list(map(int, value.split(',')))

    def get_prep_value(self, value):
        if value is None:
            return None
        return ','.join(map(str, value))