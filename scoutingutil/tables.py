from dataclasses import dataclass
from typing import Any, Callable

class Column:
    "Defines how data should be processed from raw data, and what google sheets column it should end up in."

    default_get:"Callable[[ProcessingContext], Any]" = lambda ctx: ctx.data

    def __init__(self, column_name:str, raw_attr:str|None=None, process_data:"Callable[[ProcessingContext], Any]"=default_get, strict=False):
        self.raw_attr = raw_attr
        self.column_name = column_name
        self.process_data = process_data
        self.strict = strict
        self._attr_name:str = None
    
    def __get__(self, instance:"Table", owner:"type[Table]"):
        if instance is None:
            return self
        else:
            return instance.__dict__[self._attr_name]
    
    def __set__(self, instance:"Table", value):
        if instance is not None:
            instance.__dict__[self._attr_name] = value

    def __set_name__(self, owner:"Table", name:str):
        self._attr_name = name

@dataclass(slots=True)
class ProcessingContext:
    "Context used when processing raw data into column data."

    sheets:"Table"
    column:"Column"
    raw:dict[str]
    data:Any|None=None

class Table:
    "Base class for object that stores collected and processed data. Instances of this class and its subclasses act as rows in the table."

    __columns = ()

    def __init_subclass__(cls):
        cls.__columns = tuple(column for column in cls.__dict__.values() if isinstance(column, Column))
        
    @classmethod
    def get_column_pairs(cls):
        "Return each pair of attribute name and column object."
        for column in cls.__columns:
            yield column._attr_name, column
        
    @classmethod
    def get_columns(cls):
        "Returns all column objects."
        return iter(cls.__columns)

    @classmethod
    def process_data(cls, raw_data:dict[str]):
        instance = cls.__new__(cls)
        for attr, column in cls.get_column_pairs():
            value = column.process_data(ProcessingContext(
                instance,
                column,
                raw_data,
                None if column.raw_attr is None else raw_data[column.raw_attr] if column.strict else raw_data.get(column.raw_attr)
            ))
            setattr(instance, attr, value)
        return instance