import sqlite3
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, get_flashed_messages, g, abort
from databases.caDB import CarModel, CarCompany, CarActual, s, get_all_posts, get_one_car, car_add_post, \
    car_redact_post, \
    car_delete_post, get_one_company, company_add, company_redact_post, company_delete_post, get_all_car_names, \
    get_one_actual_car, actual_redact_post, actual_car_delete_post, actual_car_add_post, actual_car_status, \
    actual_car_set_status
from databases.validators.validators import equalazer_register

'''
Админ-панель реализована через метод blueprint для удобного расширения и дополнения функционала.
По сравнению с юзер-панелью расширен функционал до CRUD-работы со всеми записями.
'''

admin = Blueprint('admin', __name__, template_folder='templates',
                  static_folder=r'C:\Users\User\Desktop\caradvancer\static')


def isLogged():
    return True if session.get('admin_logged') else False


def login_admin():
    session['admin_logged'] = 1


def logout_admin():
    session.pop('admin_logged', None)


@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', title='Admin-panel')


@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == "admin" and equalazer_register(request.form['psw'], "12345"):
            # поставить можно любой пароль и менять только по необходимости
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash('Wrong login or password', category='error')

    return render_template('admin/login.html', title='Admin-panel')


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))


@admin.route('/posts_list')
def posts_list():
    if not isLogged():
        return redirect(url_for('.login'))
    query = get_all_posts(CarCompany)
    return render_template('admin/posts_list.html', title='Posts list', company_list=query)


# car-company panel
@admin.route('/<car_company>/')
def car_company(car_company):
    if not isLogged():
        return redirect(url_for('.login'))
    query = get_one_company(car_company)
    return render_template('admin/car_company.html', title=query.company_name, car_company=query)


@admin.route('/company_post_add', methods=['POST', 'GET'])
def company_add_post():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        res = company_add(request.form['company_name'], request.form['general_company_info'],
                          request.form['logo_img_path'])

    return render_template('admin/company_post_add.html', title='Company append')


@admin.route('/<car_company>/correction', methods=['POST', 'GET'])
def company_post_correction(car_company):
    if not isLogged():
        return redirect(url_for('.login'))
    query = get_one_company(car_company)
    if request.method == 'POST':
        res = company_redact_post(car_company,
                                  lister=[request.form['company_name'], request.form['general_company_info'],
                                          request.form['logo_img_path']])

    return render_template('admin/company_post_redact.html', company_for_redact=query,
                           title=f'Correction {car_company}')


@admin.route('/<car_company>/delete', methods=['POST', 'GET'])
def company_post_delete(car_company):
    if not isLogged():
        return redirect(url_for('.login'))
    company_delete_post(car_company)

    return redirect('/posts_list')


# car-model panel
@admin.route('/car_model_add', methods=['POST', 'GET'])
def car_model_add():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        if get_one_car(request.form['model_name']) not in get_all_car_names(CarModel):
            # проверяем, нет ли подобной модели в списке CarModel
            res = car_add_post(request.form['model_name'], request.form['price'], request.form['year_made'],
                               request.form['engine_volume'], request.form['engine_horsepower'],
                               request.form['travel_reach'],
                               request.form['general_description'],
                               request.form['logo_img_path'], request.form['mother_company_name'])

    return render_template('admin/car_model_add.html', title='Model append',
                           companies=get_all_posts(CarCompany))


@admin.route('/<car_company>/<car_model>')  # страница модели со списком доступных машин
def car_model(car_company, car_model):
    if not isLogged():
        return redirect(url_for('.login'))
    try:
        car_company = s.query(CarCompany).filter_by(company_name=car_company).first()
        query = s.query(CarModel).filter_by(model_name=car_model).first()  # выбираем модель машины по адресной строке
        return render_template('admin/actual_model_list.html', title=f'{query.mother_company_name} {query.model_name}',
                               car_company=car_company,
                               car_model=query, actual_car_status=actual_car_status)
    except:
        abort(404)


@admin.route('/<car_company>/<car_model>/correction', methods=['POST', 'GET'])  # коррекция модели
def car_post_correction(car_company, car_model):
    if not isLogged():
        return redirect(url_for('.login'))
    query = get_one_car(car_model)
    if request.method == 'POST':
        res = car_redact_post(car_model,
                              lister=[request.form['model_name'], request.form['price'], request.form['year_made'],
                                      request.form['engine_volume'], request.form['engine_horsepower'],
                                      request.form['travel_reach'], request.form['mother_company_name'],
                                      request.form['general_description'],
                                      request.form['logo_img_path']])

    return render_template('admin/car_post_redact.html', car_for_redact=query,
                           title=f'Редактирование статьи {car_model}')


@admin.route('/<car_company>/<car_model>/delete', methods=['POST', 'GET'])
def car_post_delete(car_company, car_model):
    if not isLogged():
        return redirect(url_for('.login'))
    car_delete_post(car_model)

    return redirect(f'/admin/{car_company}')


# actual-model panel
@admin.route('/<car_company>/<car_model>/<serial_number>')  # страница просмотра одной выбранной машины
def actual_model_info(car_company, car_model, serial_number):
    if not isLogged():
        return redirect(url_for('.login'))
    try:
        query = s.query(CarActual).filter_by(
            serial_number=serial_number).first()  # выбираем модель машины по адресной строке
        car_company = s.query(CarCompany).filter_by(company_name=car_company).first()
        return render_template('actual_model_info.html', title=f'{query.model_name} {serial_number}',
                               car_company=car_company,
                               actual_model=query)
    except:
        abort(404)


@admin.route('/actual_model_add', methods=['POST', 'GET'])
def actual_car_post_add():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        res = actual_car_add_post(request.form['model_name'], request.form['price'], request.form['year_made'],
                                  request.form['engine_volume'], request.form['engine_horsepower'],
                                  request.form['travel_reach'],
                                  request.form['serial_number'],
                                  request.form['logo_img_path'], request.form['mother_model_name'])

    return render_template('admin/actual_model_add.html', title='Добавление автомобиля из наличия',
                           companies=get_all_posts(CarCompany))


@admin.route('/<car_company>/<car_model>/<serial_number>/correction',
             methods=['POST', 'GET'])  # коррекция выбранной машины
def actual_model_correction(car_company, car_model, serial_number):
    if not isLogged():
        return redirect(url_for('.login'))
    query = get_one_actual_car(serial_number)
    if request.method == 'POST':
        res = actual_redact_post(serial_number,
                                 lister=[request.form['model_name'], request.form['mother_model_name'],
                                         request.form['price'], request.form['year_made'],
                                         request.form['engine_volume'], request.form['engine_horsepower'],
                                         request.form['travel_reach'], request.form['serial_number'],
                                         request.form['logo_img_path'],
                                         request.form['actual_status']
                                         ])

    return render_template('admin/actual_model_redact.html', car_for_redact=query,
                           title=f'Редактирование статьи {serial_number}')


@admin.route('/<car_company>/<car_model>/<serial_number>/delete', methods=['POST', 'GET'])
def actual_car_deleter(car_company, car_model, serial_number):
    if not isLogged():
        return redirect(url_for('.login'))
    actual_car_delete_post(serial_number)

    return redirect(f'/admin/{car_company}/{car_model}')
