import arrow
from ..app import db


def now():
    return arrow.utcnow().datetime


class BaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, nullable=False, default=now)

    def __init__(self, classtype, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        self._type = classtype


def model_factory(name, argnames, BaseModel=BaseModel):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in argnames:
                raise TypeError("Argument %s not valid for %s"
                                % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseModel.__init__(self, name[:-len("Class")])
    newclass = type(name, (BaseModel,), {"__init__": __init__})
    return newclass
