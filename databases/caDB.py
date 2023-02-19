import random, datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from databases.googlesheets_api.googlework_recorders import google_recorder

'''
В этом разделе собраны методы работы с базами данных.
БД реализованы через sqalchemy. Сами таблицы реализованы через классы. Классы соединены с собой методом backref.
'''

# создаем соединение с БД
engine = create_engine("sqlite:///databases/blog.db", echo=False, connect_args={'check_same_thread': False})

Base = declarative_base()  # стандартный класс, его наследуют все классы, которые свяжутся с БД

actual_car_status = ['Active', 'Inactive', 'On moderation', 'Check required',
                     'Repairing',
                     'On action']  # статусы для автомобилей (возможно распространение на компании и модели)
default_car_picture = 'static/icons/no_category.png'  # ставим путь к картинке по умолчанию


class CarCompany(Base):  # таблица с моделью той или иной компании
    __tablename__ = 'car_company'

    id = Column(Integer, primary_key=True)
    company_name = Column(String(50), unique=True)
    general_company_info = Column(String(500), nullable=True)
    logo_img_path = Column(String, default=None)
    list_autos = relationship('CarModel', backref='car_company', lazy=True)


class CarModel(Base):  # таблица с моделью той или иной машины
    __tablename__ = 'car_model'

    id = Column(Integer, primary_key=True)
    model_name = Column(String(50), unique=True)
    price = Column(Integer)
    year_made = Column(Integer)
    engine_volume = Column(Integer)
    engine_horsepower = Column(Integer)
    travel_reach = Column(Integer)
    mother_company_name = Column(String(50), ForeignKey('car_company.company_name'), default='No category')
    logo_img_path = Column(String, default=None)
    list_actual = relationship('CarActual', backref='car_model', lazy=True)
    general_description = Column(String(500), default='No info yet')

    def __str__(self):
        return f'''{self.model_name}'''


class CarActual(Base):  # таблица с фактическим количеством машин той или иной модели
    __tablename__ = 'car_actual'

    id = Column(Integer, primary_key=True)
    model_name = Column(String(50), unique=False)
    price = Column(Integer)
    year_made = Column(Integer)
    engine_volume = Column(Integer)
    engine_horsepower = Column(Integer)
    travel_reach = Column(Integer)
    actual_status = Column(String(500), default='Active')
    serial_number = Column(String(50), unique=True)
    logo_img_path = Column(String, default=None)

    mother_model_name = Column(String, ForeignKey('car_model.model_name'), default='No category')
    list_rented = relationship('Users', backref='car_actual', lazy=True)
    list_orders = relationship('Orders', backref='car_actual', lazy=True)

    def __str__(self):
        return f'''"{self.model_name}" {self.serial_number} S/N. {self.year_made} year made, {self.engine_volume} L. engine volume.'''


class Users(Base):  # таблица с пользователями
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String, unique=True)
    password = Column(Text)

    user_car = Column(String, ForeignKey('car_actual.serial_number'))
    user_orders = relationship('Orders', backref='users', lazy=True)

    def __str__(self):
        return self.nickname


class Orders(Base):  # таблица с заказами
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_id_for_show = Column(String, unique=True)

    user_rented = Column(String, ForeignKey('users.nickname'))
    car_rented = Column(String, ForeignKey('car_actual.serial_number'))

    order_started = Column(DateTime)
    order_finished = Column(DateTime)
    order_duration = Column(String)
    order_price = Column(Float)
    order_summ = Column(Float)
    order_status = Column(String, default='On action')

    def __str__(self):
        return f'Order №{self.order_id_for_show}. Car: {self.car_rented}. \
        Start: {self.order_started}. Finish: {self.order_finished}. \
        Duration: {get_order_duration(self.order_id_for_show)}. Cost: {get_order_summ(self.order_id_for_show)} € in total.'


Base.metadata.create_all(engine)

# работа с сесмиями для создания запросов
session = sessionmaker(bind=engine)
s = session()


def get_all_posts(table):
    query = s.query(table).all()
    return query


def get_all_car_names(table):
    return [i.model_name for i in get_all_posts(table)]


# company-panel
def get_one_company(company_name=None):
    query = s.query(CarCompany).filter(
        CarCompany.company_name == company_name).first()  # ищем в таблице Каркомпани по фильтру company_name
    return query


def company_add(company_name, general_company_info, logo_img_path):
    new_company = CarCompany(company_name=company_name, general_company_info=general_company_info,
                             logo_img_path=logo_img_path if logo_img_path else default_car_picture)
    s.add(new_company)
    s.commit()


def company_redact_post(company_name, lister):
    company_for_redact = get_one_company(company_name)
    if lister[0]:
        # меняем названия всех моделей вслед за "материнским" заводом
        for model in company_for_redact.list_autos:
            model.mother_company_name = lister[0]
        company_for_redact.company_name = lister[0]
    if lister[1]: company_for_redact.general_company_info = lister[1]
    if lister[2]: company_for_redact.logo_img_path = lister[2]

    s.commit()


def company_delete_post(company_name):
    category_for_delete = get_one_company(company_name)
    s.delete(category_for_delete)

    s.commit()


# car-model-panel
def get_one_car(model_name=None):
    query = s.query(CarModel).filter(
        CarModel.model_name == model_name).first()  # ищем в таблице Кармодел по фильтру model_name
    return query


def car_add_post(model_name, price, year_made, engine_volume, engine_horsepower, travel_reach,
                 general_description, logo_img_path, mother_company_name):
    new_car = CarModel(model_name=model_name, price=price, year_made=year_made, engine_volume=engine_volume,
                       engine_horsepower=engine_horsepower, travel_reach=travel_reach,
                       general_description=general_description,
                       logo_img_path=logo_img_path if logo_img_path else default_car_picture,
                       mother_company_name=mother_company_name if mother_company_name else 'No category')
    s.add(new_car)
    s.commit()


def car_redact_post(model_name, lister):
    car_for_redact = get_one_car(model_name)
    if lister[0]:
        # меняем названия всех актуальных моделей вслед за "материнской" моделью
        for car in car_for_redact.list_actual:
            car.mother_model_name = lister[0]
            car.model_name = lister[0]
        car_for_redact.model_name = lister[0]
    if lister[1]: car_for_redact.price = lister[1]
    if lister[2]: car_for_redact.year_made = lister[2]
    if lister[3]: car_for_redact.engine_volume = lister[3]
    if lister[4]: car_for_redact.engine_horsepower = lister[4]
    if lister[5]: car_for_redact.travel_reach = lister[5]
    if lister[6]: car_for_redact.mother_company_name = lister[6]
    if lister[7]: car_for_redact.general_description = lister[7]
    if lister[8]: car_for_redact.logo_img_path = lister[8]

    s.commit()


def car_delete_post(model_name):
    car_for_delete = get_one_car(model_name)
    s.delete(car_for_delete)

    s.commit()


# actual-car-panel
def get_one_actual_car(serial_number=None):
    query = s.query(CarActual).filter(
        CarActual.serial_number == serial_number).first()  # ищем в таблице Караутуал по фильтру сериал намбер
    return query


def actual_redact_post(actual_model, lister):
    car_for_redact = get_one_actual_car(actual_model)
    if lister[0]: car_for_redact.model_name = lister[0]
    if lister[1]: car_for_redact.mother_model_name = lister[1]
    if lister[2]: car_for_redact.price = lister[2]
    if lister[3]: car_for_redact.year_made = lister[3]
    if lister[4]: car_for_redact.engine_volume = lister[4]
    if lister[5]: car_for_redact.engine_horsepower = lister[5]
    if lister[6]: car_for_redact.travel_reach = lister[6]
    if lister[7]: car_for_redact.serial_number = lister[7]
    if lister[8]: car_for_redact.logo_img_path = lister[8]
    if lister[9]: car_for_redact.actual_status = lister[9]

    s.commit()


def actual_car_add_post(model_name, price, year_made, engine_volume, engine_horsepower, travel_reach, mother_model_name,
                        serial_number, logo_img_path):
    new_car = CarActual(model_name=model_name, price=price, year_made=year_made, engine_volume=engine_volume,
                        engine_horsepower=engine_horsepower, travel_reach=travel_reach,
                        serial_number=serial_number,
                        logo_img_path=logo_img_path if logo_img_path else default_car_picture,
                        mother_model_name=(mother_model_name if mother_model_name else 'No name model'))
    s.add(new_car)
    s.commit()


def actual_car_delete_post(serial_number):
    car_for_delete = get_one_actual_car(serial_number)
    s.delete(car_for_delete)

    s.commit()


def actual_car_set_status(serial_number, new_status):  # обновление статуса доступного авто по серийному номеру
    car_for_status = get_one_actual_car(serial_number)
    car_for_status.actual_status = new_status
    return car_for_status


# user-panel
def user_add(name, psw):
    new_user = Users(nickname=name, password=psw)
    s.add(new_user)
    s.commit()


def get_one_user(nickname):
    query = s.query(Users).filter(
        Users.nickname == nickname).first()
    return query


def user_redact(nickname, password):
    user_for_redact = get_one_user(nickname)
    user_for_redact.password = password

    s.commit()


# order-panel
def get_one_order_by_id(order_id_for_show):  # получаем заказ по его id
    query = s.query(Orders).filter(
        Orders.order_id_for_show == order_id_for_show).first()
    return query


def get_one_order_by_user_and_status(nickname, status):  # получаем заказ по пользователю и статусу
    query = s.query(Orders).filter(Orders.user_rented == nickname,
                                   Orders.order_status == status).first()
    return query


def get_order_duration(order_id_for_show):
    order = get_one_order_by_id(order_id_for_show)
    if not order.order_finished:
        res = datetime.datetime.now() - order.order_started
        return res
    else:
        res = order.order_finished - order.order_started
        return res


def get_order_summ(order_id_for_show):
    order = get_one_order_by_id(order_id_for_show)
    time_rented = get_order_duration(order.order_id_for_show)
    res = round(float(time_rented.total_seconds() / 60) * order.order_price / 60, 2)
    return res


def order_history(user):
    query = s.query(Orders).filter(
        Orders.user_rented == user).all()
    return query


def order_create(user, car_for_rent_serial_number):
    actual_car_set_status(car_for_rent_serial_number, 'On action')  # ставим машину на прокат
    get_one_user(user).user_car = car_for_rent_serial_number

    order_id_for_show_setter = f'{car_for_rent_serial_number}{random.randint(1, 99)}{datetime.date.today()}'
    new_order = Orders(user_rented=user, car_rented=car_for_rent_serial_number, order_started=datetime.datetime.now(),
                       order_price=get_one_actual_car(car_for_rent_serial_number).price,
                       order_status='On action',
                       order_id_for_show=order_id_for_show_setter
                       )

    s.add(new_order)

    s.commit()

    # для записи в Google-API передаем id(для выбора строки в документе) и передаем список нужных столбцов)
    google_recorder(new_order.id,
                    [new_order.user_rented,
                     new_order.order_id_for_show,
                     new_order.car_rented,
                     str(new_order.order_started),
                     'Not finished yet',
                     str(get_order_duration(new_order.order_id_for_show)),
                     new_order.order_price,
                     'Not finished yet',
                     new_order.order_status
                     ])


def order_finish(order_id_for_show):
    order_for_finish = get_one_order_by_id(order_id_for_show)
    actual_car_set_status(order_for_finish.car_rented, 'Active')  # сдаем машину с проката
    get_one_user(order_for_finish.user_rented).user_car = None
    order_for_finish.order_status = 'Finished'

    order_for_finish.order_finished = datetime.datetime.now()
    order_for_finish.order_duration = str(get_order_duration(order_for_finish.order_id_for_show))
    order_for_finish.order_summ = get_order_summ(order_id_for_show)

    # для записи в Google-API передаем id(для выбора строки в документе) и передаем список нужных столбцов)
    google_recorder(order_for_finish.id,
                    [order_for_finish.user_rented,
                     order_for_finish.order_id_for_show,
                     order_for_finish.car_rented,
                     str(order_for_finish.order_started),
                     str(order_for_finish.order_finished),
                     str(get_order_duration(order_for_finish.order_id_for_show)),
                     order_for_finish.order_price,
                     get_order_summ(order_for_finish.order_id_for_show),
                     order_for_finish.order_status
                     ])

    s.commit()
