import enum
import arrow
from sqlalchemy.ext.declarative import declared_attr
from ..app import db


def now():
    return arrow.utcnow().datetime


class BaseMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __mapper_args__ = {'always_refresh': True}

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=now)

    def __repr__(self):
        return '{0}: {1}'.format(self.__class__, self.id)


class Customer(BaseMixin, db.Model):
    # Sample customer model
    __tablename__ = 'customer'
    name = db.Column(db.String(250), nullable=False)


class RiskType(BaseMixin, db.Model):
    __tablename__ = 'risk_type'

    table_name = db.Column(db.String(250), nullable=False)
    risk_type_id = db.Column(db.Integer, nullable=False)


class Policy(BaseMixin, db.Model):
    __tablename__ = 'policy'
    effective_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    total_amount = db.Column(db.DECIMAL, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'),
                            nullable=False)
    customer = db.relationship('Customer',
                               backref=db.backref('policies', lazy=True))

    risk_id = db.Column(db.Integer, db.ForeignKey('risk_type.id'),
                        nullable=False)
    risk_type = db.relationship('RiskType',
                                backref=db.backref('policies', lazy=True))


class PolicyEditLog(BaseMixin, db.Model):
    __tablename__ = 'policy_edit_log'
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'),
                          nullable=False)
    policy = db.relationship('Policy',
                             backref=db.backref('edit_logs', lazy=True))
    edited_on = db.Column(db.DateTime, nullable=False, default=now)


class BillStatus(enum.Enum):
    CANCELLED = 0
    PENDING = 1
    PAID = 2


class Bill(BaseMixin, db.Model):
    __tablename__ = 'bill'
    due_date = db.Column(db.DateTime, nullable=False)
    minimum_payment = db.Column(db.DECIMAL, nullable=False)
    balance = db.Column(db.DECIMAL, nullable=False)
    status = db.Column(db.Enum(BillStatus), default=BillStatus.PENDING)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'),
                          nullable=False)
    policy = db.relationship('Policy',
                             backref=db.backref('edit_logs', lazy=True))


class Payment(BaseMixin, db.Model):
    __tablename__ = 'payment'
    paid_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.DECIMAL, nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'),
                        nullable=False)
    bill = db.relationship('Bill',
                           backref=db.backref('payments', lazy=True))


def model_factory(name, argnames, BaseClass=BaseMixin):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in argnames:
                raise TypeError("Argument %s not valid for %s"
                                % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name[:-len("Class")])
    newclass = type(name, (BaseClass,), {"__init__": __init__})
    return newclass
