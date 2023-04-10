from flask_wtf import FlaskForm
from werkzeug.routing import ValidationError
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, DecimalField, SelectField
from wtforms.validators import DataRequired, optional, Email, EqualTo
from app.models import User, Company, Security, company_securities, Account


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin_tag = BooleanField('Admin')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CompanyCreationForm(FlaskForm):
    class Meta:
        model = Company

    company_name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    employee_nr = IntegerField('Number of Employees')
    company_info = TextAreaField('About the Company (Info)')
    industry_type = StringField('Which Industry does the Company work in?', validators=[DataRequired()])
    opening_hours = TextAreaField('Opening Hours', validators=[DataRequired()])
    submit = SubmitField('Create Company')


class SecurityCreationForm(FlaskForm):
    class Meta:
        model = Security

    sec_name = StringField('Name:', validators=[DataRequired()])
    price = DecimalField('Price:', validators=[DataRequired()])
    amount = IntegerField('Amount:', validators=[DataRequired()])
    currency = StringField('Currency:', validators=[DataRequired()])

    market_id = SelectField('On which market should it be available to buy?', validators=[DataRequired()],
                            choices=[('1', 'Market 1'), ('2', 'Market 2'), ('3', 'Market 3')])

    # companies = Company.query.all()
    comp_id = SelectField('Which company is offering this security?', validators=[DataRequired()],
                          choices=[('1', 'Comp 1'), ('2', 'Comp 2'), ('3', 'Comp 3')])
    submit = SubmitField('Create Security')


class MoneyInputForm(FlaskForm):
    money = DecimalField(validators=[DataRequired()])
    submit = SubmitField('Increase Money')


class MoneyOutputForm(FlaskForm):
    money = DecimalField(validators=[DataRequired()])
    submit = SubmitField('Decrease Money')
