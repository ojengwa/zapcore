from flask import jsonify
from sqlalchemy import types


def get_json(model):

    provided = [
        '__class__', '__delattr__', '__dict__', '__doc__',
        '__format__', '__getattribute__', '__hash__', '__init__',
        '__mapper__', '__module__', '__new__', '__reduce__', '__reduce_ex__',
        '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
        '__table__', '__tablename__', '__weakref__', '_decl_class_registry',
        '_sa_class_manager', 'metadata', 'query', 'query_class'
    ]

    class_structure = dict()

    for attr in list(dir(model)):
        if attr not in provided:
            class_structure[attr] = str(find_type(model, attr))

    return jsonify(structure=class_structure)


def find_type(class_, colname):
    if hasattr(class_, '__table__') and colname in class_.__table__.c:
        return class_.__table__.c[colname].type
    for base in class_.__bases__:
        return find_type(base, colname)
    raise NameError(colname)


def get_types():

    sqlalchemy_data_types = {}

    for attribute in [a for a in types.__all__ if callable(
        getattr(types, a)) and a not in [
            'TypeDecorator', 'TypeEngine', 'UserDefinedType',
            'JSON', 'BLOB', 'LargeBinary', 'Binary', 'PickleType']]:

        try:
            attribute = types.to_instance(getattr(types, attribute))

            if isinstance(attribute, types.TypeEngine):
                fields = vars(attribute)

                sqlalchemy_data_types[str(attribute)] = fields

        except TypeError:
            continue

    return sqlalchemy_data_types
