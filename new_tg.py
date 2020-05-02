import telepot
import requests
import time
import subprocess
import os

# Костыль чтобы не падал к хуям
requests.packages.urllib3.disable_warnings()

# Переменным TOKEN необходимо присвоить Вашим собственные значения
INTERVAL = 3  # Интервал проверки наличия новых сообщений (обновлений) на сервере в секундах
URL = 'https://api.telegram.org/bot'  # Адрес HTTP Bot API
TOKEN = '1174351058:AAFX_CNL3PSm1NKNB7P6hBsZCoXNDvK9E-4'  # Ключ авторизации для Вашего бота
offset = 0  # ID последнего полученного обновления


def get_new_message():
    global offset
    data = {'offset': offset + 1, 'limit': 5, 'timeout': 0}  # Формируем параметры запроса

    try:
        request = requests.post(URL + TOKEN + '/getUpdates', data=data)  # Отправка запроса обновлений
    except:
        log_event('Error getting updates at {}'.format(time))  # Логгируем ошибку
        return False

    if not request.status_code == 200 or not request.json()['ok']: return False  # проверка целостности принятого пакета
    for update in request.json()[
        'result']:  # В result содержится список словарей словарь имеет блоки update_id, message[message_id,from,chat,date,text], смотрим каждое новое сообщение
        offset = update['update_id']  # последнее обновление с телеги
        if not 'message' in update or not 'text' in update['message']:
            log_event('Unknown update: %s' % update)  # сохраняем в лог пришедшее обновление
            continue
        try:
            name = update['message']['chat']['username']  # Извлечение username отправителя
        except:
            name = 'unknown'
        from_id = update['message']['chat']['id']  # Извлечение ID чата (отправителя)
        message = update['message']['text']  # Извлечение текста сообщения
        log_event('Message (id%s) from %s (id%s): "%s"' % (offset, name, from_id, message))

        # по принятому сообщению хуячим обработку
        run_command(offset, name, from_id, message)


def log_event(text):
    if os.path.getsize('/home/pi/raspberry/log.txt') > 10000:
        with open('/home/pi/raspberry/log.txt', 'w') as f:
            f.write(text + '\n')
    else:
        with open('log.txt', 'a') as f:
            f.write(text + '\n')


def run_command(offset, name, from_id, cmd):
    if cmd == '/ping':  # Ответ на ping
        send_text(from_id, 'pong')  # Отправка ответа

    elif cmd == '/help':  # Ответ на help
        send_text(from_id, 'in this cruel world you will not get help')  # Ответ

    elif cmd == '/start':
        send_text(from_id, "Let's Start")

    else:
        send_text(from_id, "Got it, but don't know what to do with that sh*t")  # Отправка ответа


def send_text(chat_id, text, count_try=0):
    log_event('Sending to %s: %s' % (chat_id, text))  # Запись события в лог
    data = {'chat_id': chat_id, 'text': text}  # Формирование запроса
    request = requests.post(URL + TOKEN + '/sendMessage', data=data)  # HTTP запрос
    if not request.status_code == 200:  # Проверка ответа сервера
        if count_try > 3:
            log_event('ERROR:Sending to %s: %s' % (chat_id, text))
            return False  # Возврат с неудачей
        else:
            send_text(chat_id, text, count_try + 1)
    return request.json()['ok']  # Проверка успешности обращения к API


if __name__ == "__main__":
    while True:
        try:
            get_new_message()
        except KeyboardInterrupt:
            print
            'Прервано пользователем..'
            break
