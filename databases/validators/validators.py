'''Файл предназначен для хранения всех валидаторов'''
from werkzeug.security import generate_password_hash, check_password_hash


def equalazer_register(first, second):
    '''Используем валидатор для проверки, чувствительной к регистру'''
    return first == second


def password_hasher(password):
    return generate_password_hash(password)


def password_checker(value_first, value_second):
    return check_password_hash(value_first, value_second)
