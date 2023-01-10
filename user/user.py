import sqlite3
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, get_flashed_messages, g, abort
from databases.caDB import Users, CarCompany, CarModel, Orders, s, get_all_posts, get_one_user, user_add, user_redact, \
    CarActual, get_one_company, get_one_actual_car, order_create, order_history, order_finish, \
    get_one_order_by_user_and_status

user = Blueprint('user', __name__, template_folder='templates', static_folder='static')


def login_user(candidate):  # берем candidate из формы user/login.html и дальше используем никнейм из сессии
    session['user_logged'] = 1
    session["user_actual"] = candidate


def isLogged():
    return True if session.get('user_logged') else False


def logout_user():
    session.clear()


@user.route('/')
@user.route('/home')
def index():
    if not isLogged():
        return redirect(url_for('.login'))
    query = get_all_posts(CarCompany)
    return render_template('user/index.html', title='Список автомобилей', company_list=query)


@user.route('/<car_company>/')
def car_company(car_company):
    query = get_one_company(car_company)
    return render_template('user/car_company.html', title=query.company_name, car_company=query)


@user.route('/register', methods=["POST", "GET"])
def user_register():
    if request.method == 'POST':
        if str(request.form['psw']) != str(request.form['psw_again']):
            flash('Пароли не совпадают', 'error')
        else:
            res = user_add(request.form['user'], request.form['psw'])
            return redirect(url_for('.index'))

    return render_template('user/register.html', title='Регистрация пользователя',
                           user_placeholder='Username',
                           psw_placeholder='Password',
                           psw_agian_placeholder='Password confirmation')


@user.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.account'))

    if request.method == "POST":
        candidate = request.form['user']
        if request.form['psw'] == get_one_user(candidate).password:
            login_user(candidate)
            return redirect(url_for('.account'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('user/login.html', title='Вход в личный кабинет',
                           user_placeholder='Username',
                           psw_placeholder='Password')


@user.route('/account')
def account():
    if not isLogged():
        return redirect(url_for('.login'))

    tools = [
        {'url': f'{session["user_actual"]}/history', 'title': 'Order history', 'description': '',
         'button_text': 'Orders closed'},
        {'url': 'home', 'title': 'See the cars', 'description': '', 'button_text': 'Main page'},

        {'url': 'logout', 'title': 'Log out', 'description': '', 'button_text': 'Logout'},
        {'url': f'{session["user_actual"]}/case', 'title': 'Urgent orders', 'description': '',
         'button_text': 'User case'},
        {'url': f'{get_one_user(session["user_actual"])}/redact', 'title': 'Account redact', 'description': '',
         'button_text': 'Redact'},

        # {'url': 'test', 'title': 'Тестовая', 'description': '', 'button_text': 'Кнопка'},
    ]  # словарь с функционалом личного кабинета: ссылка на функцию, заголовок и описание

    return render_template('user/account.html', title='Личный кабинет',
                           tools=tools,
                           nickname=session['user_actual'])


@user.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_user()

    return redirect(url_for('.login'))


@user.route('/<username>/redact', methods=["POST", "GET"])
def user_redaction(username):
    if request.method == 'POST':
        res = user_redact(username, [request.form['user'], request.form['psw']])
        return redirect(url_for('.account'))

    return render_template('user/redact.html', title='Редактирование аккаунта',
                           user_placeholder='new Username',
                           psw_placeholder='new Password',
                           psw_agian_placeholder='Password confirmation')


@user.route('/<username>/history', methods=["POST", "GET"])
def user_history(username):
    return render_template('user/history.html', title='История заказов', nickname=session['user_actual'],
                           history=order_history(session['user_actual']))


@user.route('/<username>/case', methods=["POST", "GET"])  # актуальные заказы одного пользователя
def user_case(username):
    res = get_one_order_by_user_and_status(username, 'On action')
    try:
        case = res
        return render_template('user/case.html', title='Актуальные заказы', nickname=session['user_actual'],
                               case=case)
    except:
        case = 'No cars rented'
        return render_template('user/case.html', title='Актуальные заказы', nickname=session['user_actual'],
                               case=case)


@user.route('/<car_company>/<car_model>')  # страница модели со списком доступных машин
def car_modeler(car_company, car_model):
    try:
        car_company = s.query(CarCompany).filter_by(company_name=car_company).first()
        query = s.query(CarModel).filter_by(model_name=car_model).first()  # выбираем модель машины по адресной строке
        return render_template('user/actual_model_list.html', title=f'{query}',
                               car_company=car_company,
                               car_model=query)
    except:
        abort(404)


@user.route('/<car_company>/<car_model>/<serial_number>/rent')  # страница открытия заказа
def rent_actual_car(car_company, car_model, serial_number):
    res = order_create(session["user_actual"], serial_number)
    return redirect(url_for('.account'))


@user.route('/unrent')  # страница закрытия заказа
def end_rent_actual_car():
    order_for_finish = get_one_order_by_user_and_status(session['user_actual'], 'On action')
    res = order_finish(order_for_finish.order_id_for_show)
    return redirect(url_for('.account'))


@user.route('/<car_company>/<car_model>/<serial_number>')  # страница просмотра одной выбранной машины
def actual_model_info(car_company, car_model, serial_number):
    try:
        query = s.query(CarActual).filter_by(
            serial_number=serial_number).first()  # выбираем модель машины по адресной строке
        car_company = s.query(CarCompany).filter_by(company_name=car_company).first()
        return render_template('actual_model_info.html',
                               title=f'{query.model_name} {serial_number}',
                               car_company=car_company,
                               actual_model=query)
    except:
        abort(404)


@user.route('/test')  # страница просмотра одной выбранной машины
def tester(username):
    res = get_one_order_by_user_and_status(username, 'On action')
