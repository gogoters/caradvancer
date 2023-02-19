import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response, Blueprint
from databases.caDB import CarModel, CarCompany, CarActual, s, get_all_posts, get_one_car
from admin.admin import admin
from user.user import user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'caradvancer'
app.register_blueprint(admin, url_prefix='/admin')  # регистрируем функционал админа в директории admin
app.register_blueprint(user, url_prefix='/user')  # регистрируем функционал юзера в директории user


@app.route('/')  # гостевая страница
@app.route('/index')
@app.route('/home')
def index():
    query = get_all_posts(CarCompany)
    return render_template('index.html', title='homepage', company_list=query)


@app.route('/<car_company>/')  # страница компании со списком моделей
def car_company(car_company):
    if car_company in [company.company_name for company in get_all_posts(CarCompany)]:
        query = s.query(CarCompany).filter_by(company_name=car_company).first()
        return render_template('car_company.html', title=query.company_name, car_company=query)
    else:
        abort(404)


@app.route('/<car_company>/<car_model>')  # страница модели со списком доступных машин определенной модели
def car_model(car_company, car_model):
    try:
        car_company = s.query(CarCompany).filter_by(company_name=car_company).first()
        query = s.query(CarModel).filter_by(model_name=car_model).first()  # выбираем модель машины по адресной строке
        return render_template('actual_model_list.html', title=f'{query.mother_company_name} {query.model_name}',
                               car_company=car_company,
                               car_model=query)
    except:
        abort(404)


@app.route('/<car_company>/<car_model>/<actual_model>')  # страница одной выбранной машины
def actual_model_info(car_company, car_model, actual_model):
    try:
        query = s.query(CarActual).filter_by(
            serial_number=actual_model).first()  # выбираем модель машины по адресной строке
        car_company = s.query(CarCompany).filter_by(company_name=car_company).first()
        return render_template('actual_model_info.html', title=f'TESTER',
                               car_company=car_company,
                               actual_model=query)
    except:
        abort(404)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='contacts')


@app.errorhandler(404)  # обработчик ошибки 404
def PageNotFound(error):
    return render_template('page404handler.html', title='pagenotfound')


if __name__ == '__main__':
    app.run(debug=True)
