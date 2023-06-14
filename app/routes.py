import os

import pandas as pd
import requests, json

from flask import render_template, flash, redirect, url_for, request, make_response, jsonify, session
from sqlalchemy import Integer

from app import app, db
from app.forms import LoginForm, RegistrationForm, CompanyCreationForm, SecurityCreationForm, MoneyOutputForm, \
    MoneyInputForm
from app.models import User, Company, Account, Security
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from decimal import Decimal


# TODO: DESIGN
#       Darstellung Konto (bzw. Allgemein)

# TODO: FUNKTIONEN
#       USP (Excel import von Wertpapieren)
#       Abfragen der Boersen
#       "on delete cascade" konsistent durchziehen
#       Schnittstellen implementieren (POST)

# ============================================================================================================
# Starting site
# ============================================================================================================
@app.route('/')
@app.route('/index')
@login_required
def home_site():
    user = {'username': 'Andi'}
    companies = Company.query.all()
    securities = Security.query.all()
    companies.sort(key=lambda x: x.company_name)
    securities.sort(key=lambda x: (x.name, x.comp_id))
    return render_template('index.html', title='Home', user=user, companies=companies, securities=securities)


# ============================================================================================================
# Everything needed for USER
# ============================================================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home_site'))

    # validates login data
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # checks login data
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # if necessary login is tried to avoided
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home_site')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_site'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    admin_tag=form.admin_tag.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# ============================================================================================================
# Everything needed for COMPANY
# ============================================================================================================
@app.route('/company/overview')
@login_required
def company_overview():
    companies = Company.query.all()
    return render_template('company_overview.html', title='Company Overview', companies=companies)


@app.route('/company/details/<int:company_id>')
@login_required
def company_details(company_id):
    company = Company.query.get_or_404(company_id)
    securities = Security.query.filter_by(comp_id=company_id).all
    return render_template('company_details.html', title=company.company_name, company=company, securities=securities)


@app.route('/company/creation', methods=['GET', 'POST', 'PUT'])
@login_required
def company_creation():
    form = CompanyCreationForm()
    if form.validate_on_submit():
        # saving the companies picture in the static folder
        if form.picture.data:
            if form.picture.data.filename:
                filename = secure_filename(form.picture.data.filename)
            else:
                filename = ''
            file_ext = filename.split('.')[-1]
            if file_ext in 'jpg':
                file_path = os.path.join(app.root_path, 'static', form.company_name.data + str('_house.') + file_ext)
                form.picture.data.save(file_path)
            else:
                flash('Invalid file type! Only JPG allowed')

        company = Company(company_name=form.company_name.data,
                          address=form.address.data,
                          employee_nr=form.employee_nr.data,
                          company_info=form.company_info.data,
                          industry_type=form.industry_type.data,
                          amount_securities=0,
                          account_nr=None,
                          opening_hours=form.opening_hours.data)
        db.session.add(company)
        db.session.commit()

        account = Account(owner=company.company_id, balance=0)
        db.session.add(account)
        db.session.commit()

        company.account_nr = account.account_id
        db.session.commit()

        flash(f'Congratulations, you have successfully created the company: {company.company_name} '
              f'and its linked Account: {account.account_id}')
        return redirect(url_for('home_site'))
    return render_template('company_creation.html', title='Create Company', form=form)


@app.route('/firmen/company/update/<int:comp_id>', methods=['GET', 'POST'])
def update_comp(comp_id):
    comp = Company.query.get(comp_id)
    old_comp_name = comp.company_name
    if request.method == 'POST':
        comp.company_name = request.form['name']
        comp.address = request.form['address']
        comp.employee_nr = request.form['employee_nr']
        comp.opening_hours = request.form['ohours']
        comp.industry_type = request.form['industry_type']
        comp.company_info = request.form['description']

        db.session.commit()

        new_name = comp.company_name + "_house.jpg"
        old_path = os.path.join(app.static_folder, old_comp_name + '_house.jpg')
        new_path = os.path.join(app.static_folder, new_name)
        os.rename(old_path, new_path)

        flash('Firma: "' + comp.company_name + '" updated. ')

        previous_url = session.pop('previous_url', '/')
        return redirect(previous_url)

    session['previous_url'] = request.referrer
    return render_template('company_update.html', object=comp)


@app.route('/company/deletion/<int:company_id>', methods=['GET', 'DEL'])
@login_required
def company_deletion(company_id):
    company = Company.query.get(company_id)
    # checking if there are securities still available
    secs = Security.query.all()
    filtered_secs = []
    for x in secs:
        if x.comp_id == company.company_id:
            filtered_secs.append(x)

    if len(filtered_secs) > 0:
        flash('Still securities available! Cannot delete company.')
        return redirect(request.referrer or url_for('home_site'))

    # deleting the companies picture
    file_path = app.root_path + '/static/' + company.company_name + str('_house.jpg')
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        flash('Filepath does not exist')

    acc = Account.query.get(company.account_nr)
    db.session.delete(company)
    db.session.commit()

    db.session.delete(acc)
    db.session.commit()

    flash('Firma: "' + company.company_name +
          f'" und der verlinkte Account: {acc.account_id} gelöscht!')
    return redirect(request.referrer or url_for('company_overview'))


# ============================================================================================================
# TODO: Everything needed for Account
# ============================================================================================================
@app.route('/associated_account/<int:account_id>', methods=['GET'])
@login_required
def account_index(account_id):
    account = Account.query.get(account_id)
    company = Company.query.filter_by(account_nr=account_id).first()
    inputForm = MoneyInputForm()
    outputForm = MoneyOutputForm()
    return render_template('account_index.html', title="Account overview", account=account,
                           inputForm=inputForm, outputForm=outputForm, name=company)


@app.route('/edit_balance_up/<int:account_id>', methods=['POST', 'PUT'])
@login_required
def edit_balance_up(account_id):
    acc = Account.query.get(account_id)
    form = MoneyInputForm(request.form)
    acc.balance += form.money.data
    db.session.commit()
    flash("Balance has been edited")
    return redirect(request.referrer)


@app.route('/edit_balance_down/<int:account_id>', methods=['POST', 'PUT'])
@login_required
def edit_balance_down(account_id):
    acc = Account.query.get(account_id)
    form = MoneyOutputForm(request.form)
    acc.balance -= form.money.data
    db.session.commit()
    flash("Balance has been edited")
    return redirect(request.referrer)


# ============================================================================================================
# TODO: Everything needed for Securities
# ============================================================================================================
@app.route('/security/overview')
@login_required
def security_overview():
    securities = Security.query.all()
    return render_template('security_overview.html', title='Security Overview', securities=securities)


@app.route('/security/details/<int:sec_id>')
@login_required
def security_details(sec_id):
    sec = Security.query.get_or_404(sec_id)
    return render_template('security_details.html', title=sec.name, security=sec)


@app.route('/security/creation', methods=['GET', 'POST'])
@login_required
def security_creation():
    form = SecurityCreationForm()
    if form.validate_on_submit():
        sec = Security.query.all()
        for x in sec:
            if x.name == form.sec_name.data:
                flash('Security with that name already exists')
                return redirect(request.referrer)

        security = Security(name=form.sec_name.data,
                            price=form.price.data,
                            amount=form.amount.data,
                            currency=form.currency.data,
                            market_id=form.market_id.data,
                            comp_id=form.comp_id.data)

        db.session.add(security)
        db.session.commit()

        # POST API
        market_msg = str(send_securities(security))

        comp_name = Company.query.get(security.comp_id)
        flash(f'Congratulations, you have successfully created the Security: {security.name} '
              f'from company: {comp_name}.'
              f'Message from Market: {market_msg}')

        return redirect(url_for('home_site'))
    return render_template('security_creation.html', title='Create Security', form=form)

@app.route('/security/creation/xlsx', methods=['GET', 'POST'])
@login_required
def security_creation_xlsx():
    if request.method == 'POST':
        file = request.files['excel-file']
        if file:
            securities = []
            # Read the Excel file into a DataFrame
            df = pd.read_excel(file)

            for index, row in df.iterrows():
                name = row['name']
                price = row['price']
                amount = row['amount']
                currency = row['currency']
                company_id = row['company_id']
                market_id = row['market_id']

                # Create the Security object and add it to the database
                security = Security(name=name, price=price, amount=amount, currency=currency,
                                    comp_id=company_id, market_id=market_id)
                securities.append(security.to_dict())

            session['securities'] = jsonify(securities).data
            return redirect(url_for('security_creation_additional_confirmation'))

    return render_template("security_creation_xlsx_one.html")


@app.route('/security/creation/xlsx_two', methods=['GET', 'POST'])
@login_required
def security_creation_additional_confirmation():
    secs_json = session.get('securities')

    if not secs_json:
        flash('No Excel-file given!')
        return redirect(url_for('security_creation_xlsx'))

    secs = json.loads(secs_json)

    if request.method == 'POST':
        for sec_data in secs:
            sec_data.pop('id', None)
            # Transforms dictionary back into Security object
            security = Security(**sec_data)
            msg = send_securities(security)
            if msg == "Successfully sent!":
                db.session.add(security)
                # print('Successfully sent: ' + str(security.name))
            else:
                print('skipped: ' + str(security.name))
                continue

        db.session.commit()



        session.pop('securities', None)
        flash('Successfully created securities!')
        return redirect(url_for('home_site'))

    return render_template("security_creation_xlsx_two.html", securities=secs)


@app.route('/firmen/security/<int:sec_id>', methods=['GET', 'POST'])
def update_sec(sec_id):
    sec = Security.query.get(sec_id)
    comp = Company.query.get(sec.comp_id)
    amount = sec.amount
    if request.method == 'POST':
        sec.name = request.form['name']
        sec.amount = request.form['amount']
        if amount < int(sec.amount):
            send_securities(sec)

        db.session.commit()

        flash('Security: "' + sec.name + '" updated. ')

        previous_url = session.pop('previous_url', '/')
        return redirect(previous_url)

    session['previous_url'] = request.referrer
    return render_template('security_update.html', object=sec, comp=comp)


@app.route('/security/deletion/<int:security_id>', methods=['GET', 'DEL'])
@login_required
def security_deletion(security_id):
    security = Security.query.get(security_id)
    db.session.delete(security)
    db.session.commit()
    print(security)
    flash(f'Security: {security.name} deleted successfully!')
    return redirect(request.referrer or url_for('security_overview'))


# ============================================================================================================
# TODO: Everything needed for interaction with other applications
# ============================================================================================================
# ==============
# GET
# ==============
@app.route('/firmen/wertpapiere/market/<int:market_id>', methods=['GET'])
def get_specific_marketSec(market_id):
    secs = Security.query.filter_by(market_id=market_id).all()
    dict = [s.to_dict() for s in secs]
    return jsonify(dict)


@app.route('/firmen/<int:comp_id>', methods=['GET'])
def get_specific_company(comp_id):
    comps = Company.query.filter_by(company_id=comp_id).all()
    dict = [x.to_dict() for x in comps]
    return jsonify(dict)


@app.route('/firmen', methods=['GET'])
def get_companies():
    comps = Company.query.all()
    dict = [x.to_dict() for x in comps]
    return jsonify(dict)


@app.route('/firmen/wertpapiere/<int:sec_id>', methods=['GET'])
def get_specific_security(sec_id):
    sec = Security.query.get(sec_id)
    dict = sec.to_dict()
    return jsonify(dict)


@app.route('/firmen/wertpapiere', methods=['GET'])
def get_securities():
    secs = Security.query.all()
    dict = [x.to_dict() for x in secs]
    return jsonify(dict)


@app.route('/firmen/specificCompany/wertpapiere/<int:comp_id>', methods=['GET'])
def get_companies_sec(comp_id):
    secs = Security.query.filter_by(comp_id=comp_id).all()
    dict = [x.to_dict() for x in secs]
    return jsonify(dict)


# ==============
# PUT
# ==============
@app.route('/firmen/wertpapier/kauf/<int:sec_id>', methods=['PUT'])
def put_boughtSec(sec_id):
    secs = Security.query.get(sec_id)
    if not secs:
        return make_response(jsonify({'message': 'Security not found'}), 404)

    amount = 0
    price = 0
    fee = 0

    company = Company.query.get(secs.comp_id)
    account = Account.query.get(company.account_nr)

    data = request.get_json()
    # check if needed data is provided
    if 'price' not in data or 'amount' not in data or 'market_fee' not in data:
        return make_response(jsonify({'message': 'Data needed not found'}), 404)

    if 'amount' in data:
        amount = float(data['amount'])
    if 'price' in data:
        price = float(data['price'])
    if 'market_fee' in data:
        fee = float(data['market_fee'])

    result = (price * amount) + fee
    result = Decimal(result)

    if account.balance < result:
        return make_response(jsonify({'message': 'Company does not have enough money'}), 404)
    else:
        account.balance = account.balance - result

    db.session.commit()
    return make_response(jsonify({'message': 'Securities bought'}), 200)


@app.route('/firmen/wertpapier/verkauf/<int:sec_id>', methods=['PUT'])
def put_buySec(sec_id):
    secs = Security.query.get(sec_id)
    if not secs:
        return make_response(jsonify({'message': 'Security not found'}), 404)

    price = float(secs.price)

    company = Company.query.get(secs.comp_id)
    account = Account.query.get(company.account_nr)

    data = request.get_json()
    if 'amount' in data:
        amount = float(data['amount'])
    else:
        return make_response(jsonify({'message': 'Data needed not found'}), 404)

    result = (price * amount)
    result = Decimal(result)
    account.balance += result

    db.session.commit()
    return make_response(jsonify({'message': 'Securities bought'}), 200)


# ==============
# POST
# ==============
def send_securities(security):
    url = "http://localhost:50052/markets/" + str(security.market_id) + "/offer"
    data = security.to_dict()
    data_json = jsonify(data).data
    header = {"Content-Type": "application/json"}
    response = requests.post(url, data=data_json, headers=header)

    if response.status_code == 404:
        return "Data wrong!"
    elif response.status_code == 400:
        return "Syntax wrong!"
    else:
        return "Successfully sent!"
