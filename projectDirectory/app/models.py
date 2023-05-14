from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


# Thats how to create a Table in the DB
# This part is responsible for user's login-data + (de-)hashing the password
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin_tag = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # kinda similar to the toString() Method
    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# ====================================================================
# the next part is responsible for the database itself.
class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.Text, index=True, unique=True)
    address = db.Column(db.Text)
    employee_nr = db.Column(db.Integer)
    company_info = db.Column(db.Text)
    industry_type = db.Column(db.Text)
    opening_hours = db.Column(db.Text)
    amount_securities = db.Column(db.Text)
    account_nr = db.Column(db.Integer)

    def __init__(self, company_name, address, employee_nr, company_info, industry_type, amount_securities, account_nr, opening_hours):
        self.generate_company_id()
        self.company_name = company_name
        self.address = address
        self.employee_nr = employee_nr
        self.company_info = company_info
        self.industry_type = industry_type
        self.amount_securities = amount_securities
        self.account_nr = account_nr
        self.opening_hours = opening_hours
        self.amount_securities = 0


    def generate_company_id(self):
        # query to get the most recent one
        last_company = Company.query.order_by(Company.company_id.desc()).first()
        if last_company:
            self.company_id = last_company.company_id + 1
        else:
            self.company_id = 1

    def to_dict(self):
        return {'id': self.company_id, 'address': self.address, 'employee_nr': self.employee_nr,
                'industry_type': self.industry_type, 'opening_hours': self.opening_hours,
                'amount_securities': self.amount_securities, 'account_nr': self.account_nr,
                'company_name': self.company_name, 'company_info': self.company_info}

    def __repr__(self):
        return 'Company {}'.format(self.company_name, self.address, self.employee_nr)


class Account(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(precision=10, scale=5))
    owner = db.Column(db.Text)

    def __init__(self, balance, owner):
        self.balance = balance
        self.owner = owner
        self.generate_account_id()

    def generate_account_id(self):
        # query to get the most recent one
        last_account = Account.query.order_by(Account.account_id.desc()).first()
        if last_account:
            self.account_id = last_account.account_id + 1
        else:
            self.account_id = 1

    def to_dict(self):
        return {'id': self.account_id, 'balance': self.balance, 'owner': self.owner}

    def __repr__(self):
        return '<Account: {}>'.format(self.account_id, self.owner, self.balance)


class Security(db.Model):
    security_id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(precision=10, scale=5))
    amount = db.Column(db.Integer)
    currency = db.Column(db.String)
    name = db.Column(db.String, index=True, unique=True)
    market_id = db.Column(db.Integer)
    comp_id = db.Column(db.Integer)

    def __init__(self, price, amount, currency, name, market_id, comp_id):
        self.generate_security_id()
        self.price = price
        self.amount = amount
        self.currency = currency
        self.name = name
        self.market_id = market_id
        self.comp_id = comp_id

    def to_dict(self):
        return {'id': self.security_id, 'price': self.price, 'amount': self.amount, 'currency': self.currency,
                'name': self.name, 'market_id': self.market_id, 'comp_id': self.comp_id}

    def generate_security_id(self):
        # query to get the most recent one
        last_security = Security.query.order_by(Security.security_id.desc()).first()
        if last_security:
            self.security_id = last_security.security_id + 1
        else:
            self.security_id = 1

    def __repr__(self):
        return '<Security: {}>'.format(self.security_id, self.name, self.price,
                                       self.currency, self.amount)


company_securities = db.Table('company_securities', db.Model.metadata,
                              db.Column('sec_id', db.Integer, db.ForeignKey('security.security_id')),
                              db.Column('comp_id', db.Integer, db.ForeignKey('company.company_id'))
                              )

