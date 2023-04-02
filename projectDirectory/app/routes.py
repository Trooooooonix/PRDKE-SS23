from app import app
from flask import Flask, render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, CompanyCreationForm, SecurityCreationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Company, Account, Security, company_securities
from app import db
from werkzeug.urls import url_parse


# ============================================================================================================
# Starting site
# ============================================================================================================
@app.route("/")
@app.route("/index")
@login_required
def home_site():
    user = {'username': 'Andi'}
    companies = Company.query.all()
    securities = Security.query.all()
    return render_template('index.html', title='Home', user=user, companies=companies, securities=securities)


@app.route('/company/details/<int:company_id>')
def company_details(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('company_details.html', company=company)

# ============================================================================================================
# TODO: This method will load some basic data into the specific tables in order to have a decent starting point.
# ============================================================================================================


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


@app.route('/company/creation', methods=['GET', 'POST', 'PUT'])
@login_required
def company_creation():
    form = CompanyCreationForm()
    if form.validate_on_submit():
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


@app.route('/company/deletion/<int:company_id>', methods=['GET', 'DEL'])
@login_required
def company_deletion(company_id):
    company = Company.query.get(company_id)
    db.session.delete(company)
    db.session.commit()
    print(company)
    flash('Firma "' + company.company_name + '" gelöscht!')
    return redirect(url_for('company_overview'))

# ============================================================================================================
# TODO: Everything needed for Securities
# ============================================================================================================
@app.route('/security/overview')
@login_required
def security_overview():
    securities = Security.query.all()
    return render_template('security_overview.html', title='Security Overview', securities=securities)


@app.route('/security/creation', methods=['GET', 'POST'])
@login_required
def security_creation():
    form = SecurityCreationForm()
    if form.validate_on_submit():
        security = Security(name=form.sec_name.data,
                            price=form.price.data,
                            amount=form.amount.data,
                            currency=form.currency.data,
                            market_id=form.market_id.data,
                            comp_id=form.comp_id.data)

        db.session.add(security)
        db.session.commit()

        flash(f'Congratulations, you have successfully created the Security: {security.name} '
              f'from company: {security.comp_id}')
        return redirect(url_for('home_site'))
    return render_template('security_creation.html', title='Create Security', form=form)


@app.route('/security/deletion/<int:security_id>', methods=['GET', 'DEL'])
@login_required
def security_deletion(security_id):
    security = Security.query.get(security_id)
    db.session.delete(security)
    db.session.commit()
    print(security)
    flash(f'Security: {security.name} deleted successfully!')
    return redirect(url_for('security_overview'))

# ============================================================================================================
# TODO: Everything needed for interaction with other applications
# ============================================================================================================
# ==============
# GET
# ==============
@app.route('/firmen/wertpapiere/<int:market_id>', methods=['GET'])
@login_required
def get_specific_marketSec(market_id):
    return market_id

@app.route('/firmen/<int:comp_id>', methods=['GET'])
@login_required
def get_specific_company(comp_id):
    return comp_id

@app.route('/firmen', methods=['GET'])
@login_required
def get_companies():
    return 1

@app.route('/firmen/wertpapiere/<int:sec_id>', methods=['GET'])
@login_required
def get_specific_security(sec_id):
    return sec_id

@app.route('/firmen/wertpapiere', methods=['GET'])
@login_required
def get_securities():
    return 1

@app.route('/firmen/<int:comp_id>', methods=['GET'])
@login_required
def get_companies_sec(comp_id):
    return comp_id

# ==============
# PUT
# ==============
@app.route('/firmen/wertpapier/bought/<int:sec_id>', methods=['PUT'])
@login_required
def put_boughtSec(sec_id):
    return sec_id

@app.route('/firmen/wertpapier/buy/<int:sec_id>', methods=['PUT'])
@login_required
def put_buySec(sec_id):
    return sec_id

# ==============
# POST
# ==============

@app.route('/boerse/offer/<int:market_id>', methods=['POST'])
@login_required
def send_securities(market_id):
    return market_id