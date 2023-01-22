import requests, json, os
from os.path import join, dirname
from dotenv import load_dotenv
from yookassa import Configuration, Payment
from flask import request

"""
Файл для работы с телеграм-ботом,
который доставляет клиенту кнопку для оплаты заказа.
Оплата реализована через модуль yookassa, 
который также используется в модуле user для оплаты заказов  
"""


# работаем с телеграм-токеном
def get_from_env(key):
    dotenv_path = join(dirname(r'C:\Users\User\Desktop\caradvancer'), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)  # возвращаем секретный токен


def send_message(chat_id, text):
    method = "sendMessage"
    token = get_from_env('TELEGRAM_BOT_TOKEN')
    url = f'https://api.telegram.org/bot{token}/{method}'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)


# работа с yookassa, создаем платежку. По умолчанию клиент платит 100 рублей и переносится в личный кабинет.
def yookassa_create_invoice(chat_id=None, value=100.00, currency='RUB', redirect_url='http://127.0.0.1:5000/user/account',
                            description='No description'):
    Configuration.account_id = get_from_env('SHOP_ID')
    Configuration.secret_key = get_from_env('PAYMENT_TOKEN')
    payment = Payment.create({
        "amount": {
            "value": f"{value}",
            "currency": f"{currency}"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{redirect_url}"
        },
        "capture": True,
        "description": f"{description}",
        "metadata": {'chat_id': chat_id}  # любые данные, которые мы хотим получить после оплаты
    })

    return payment.confirmation.confirmation_url


def send_pay_button(chat_id, text):
    invoice_url = yookassa_create_invoice(chat_id)

    method = "sendMessage"
    token = get_from_env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"

    data = {"chat_id": chat_id, "text": text, "reply_markup": json.dumps({"inline_keyboard": [[{
        "text": "Оплатить!",
        "url": f"{invoice_url}"
    }]]})}

    requests.post(url, data=data)


def check_if_successful_payment(request):
    try:
        if request.json['event'] == 'payment.succeeded':
            return True
    except KeyError:
        return False

    return False


def telegram():
    if check_if_successful_payment(request):
        # обработка запроса от юкассы
        chat_id = request.json['object']['metadata']['chat_id']
        send_message(chat_id, 'Оплата прошла успешно!')
    else:
        # обработка запроса от телеграм
        chat_id = request.json['message']['chat']['id']
        send_pay_button(chat_id=chat_id, text='Тестовая оплата')
    return {'ok': True}
