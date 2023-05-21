from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from werkzeug.routing import ValidationError
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, DecimalField, \
    SelectField, FileField
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
    employee_nr = IntegerField('Number of Employees', render_kw={'class': 'form-control', 'style': 'width: 50ch'})
    company_info = TextAreaField('About the Company (Info)', render_kw={'class': 'form-control', 'rows': 5, 'cols': 50})
    industry_type = StringField('Which Industry does the Company work in?', validators=[DataRequired()])
    opening_hours = TextAreaField('Opening Hours', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 5, 'cols': 50})
    picture = FileField('Picture', validators=[FileAllowed(['jpg'], 'Images only!')])
    submit = SubmitField('Create Company')


class SecurityCreationForm(FlaskForm):
    class Meta:
        model = Security

    sec_name = StringField('Name:', validators=[DataRequired()])
    price = DecimalField('Price:', validators=[DataRequired()])
    amount = IntegerField('Amount:', validators=[DataRequired()])
    currency = StringField('Currency:', validators=[DataRequired()])
    market_id = SelectField('On which market should it be available to buy?', validators=[DataRequired()])
    comp_id = SelectField('Which company is offering this security?', validators=[DataRequired()])
    submit = SubmitField('Create Security')

    # overrides the __init__ method in order to dynamically fetch names and ids of companies.
    # It displays the company name in the selection form, but uses the company-id to save them at the right place
    def __init__(self, *args, **kwargs):
        super(SecurityCreationForm, self).__init__(*args, **kwargs)
        self.market_id.choices = [('1', 'Market 1'), ('2', 'Market 2'), ('3', 'Market 3')]
        self.comp_id.choices = [(str(company.company_id), company.company_name) for company in Company.query.all()]


class MoneyInputForm(FlaskForm):
    money = DecimalField(validators=[DataRequired()])
    submit = SubmitField('Increase Money')


class MoneyOutputForm(FlaskForm):
    money = DecimalField(validators=[DataRequired()])
    submit = SubmitField('Decrease Money')
