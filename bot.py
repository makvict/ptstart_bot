import paramiko
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import re
import logging
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os

logging.basicConfig(
    filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

connection = None

load_dotenv()

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
PACKAGE = False
EmailList = []
phoneNumberList = []
commands_dict = {
    '/get_release': 'lsb_release -a',
    '/get_uname': 'uname -a',
    '/get_uptime': 'uptime',
    '/get_df': 'df -h',
    '/get_free': 'free -h',
    '/get_mpstat': 'mpstat',
    '/get_w': 'w',
    '/get_auths': 'last -n 10',
    '/get_critical': 'tail -n 5 /var/log/syslog | grep "CRITICAL" | head -n 20',
    '/get_ps': 'ps aux | head -n 20',
    '/get_ss': 'netstat -tuln',
    '/get_apt_list': 'dpkg -l',
    '/get_services': 'systemctl list-units --type=service | head -n 20'
}


TOKEN = '7011253439:AAE3gBikcpStmwP_w8oHkq41TnfOALsCFWI'


def command(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username,
                   password=password, port=port)
    stdin, stdout, stderr = client.exec_command(
        commands_dict[update.message.text])
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)


def log(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=os.getenv('RM_HOST'), username='root', password=os.getenv('RM_PASSWORD'), port=os.getenv('RM_PORT'))
    stdin, stdout, stderr = client.exec_command('cat /var/log/postgresql/postgresql-14-main.log | tail -n 5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)


# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def get_apt_list(update, context):

    reply_markup = {"keyboard": [["Показать все пакеты"], ["Поиск пакета"]]}

    update.message.reply_text(
        "Хотите вывести все пакеты или выполнить поиск информации о конкретном пакете?", reply_markup=reply_markup)


def handle_reply(update, context):
    global PACKAGE
    user_reply = update.message.text

    if user_reply == "Показать все пакеты":
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username,
                       password=password, port=port)
        stdin, stdout, stderr = client.exec_command(
            '''dpkg -l | tail -n +6 | head -n 20 | awk '{print $1 "\t" $2 "\t" $3}' ''')
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
    elif user_reply == "Поиск пакета":
        update.message.reply_text("Введите название пакета для поиска:")
        PACKAGE = True
    else:
        if PACKAGE:
            package_name = update.message.text
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=username,
                           password=password, port=port)
            com = 'dpkg -l ' + package_name

            stdin, stdout, stderr = client.exec_command(com)
            data = stdout.read() + stderr.read()
            client.close()
            data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

            update.message.reply_text(data)
            context.user_data['state'] = None


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('''
Список команд
Поиск
а) Email-адреса.

Команда: `/find_email`

б) Номера телефонов.

Команда: `/find_phone_number`

Проверка пароля

Команда: /verify_password
3.1.1 О релизе.

Команда: `/get_release`

3.1.2 Об архитектуры процессора, имени хоста системы и версии ядра.

Команда: `/get_uname`

3.1.3 О времени работы.

Команда: `/get_uptime`

3.2 Сбор информации о состоянии файловой системы.

Команда: `/get_df`

3.3 Сбор информации о состоянии оперативной памяти.

Команда: `/get_free`

3.4 Сбор информации о производительности системы.

Команда: `/get_mpstat`

3.5 Сбор информации о работающих в данной системе пользователях.

Команда: `/get_w`

3.6 Сбор логов

3.6.1 Последние 10 входов в систему.

Команда: `/get_auths`

3.6.2 Последние 5 критических события.

Команда: `/get_critical`

3.7 Сбор информации о запущенных процессах.

Команда: `/get_ps`

3.8 Сбор информации об используемых портах.

Команда: `/get_ss`

3.9 Сбор информации об установленных пакетах.

Команда: `/get_apt_list`

<aside>
❗ Стоит учесть два варианта взаимодействия с этой командой:

1. Вывод всех пакетов;
2. Поиск информации о пакете, название которого будет запрошено у пользователя.
</aside>

3.10 Сбор информации о запущенных сервисах.

Команда: `/get_services`
''')


def find_emails(update: Update, context):
    connection = None
    try:
        dbuser = os.getenv('DB_USER')
        dbpass = os.getenv('DB_PASSWORD')
        dbhost = os.getenv('DB_HOST')
        dbport = os.getenv('DB_PORT')
        dbname = os.getenv('DB_DATABASE')
        connection = psycopg2.connect(user=dbuser,
                                      password=dbpass,
                                      host=dbhost,
                                      port=dbport,
                                      database=dbname)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        list = []
        for i in data:
            list.append(i)
        update.message.reply_text(list)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        print('error')
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()


def find_phones(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                      password=os.getenv('DB_PASSWORD'),
                                      host=os.getenv('DB_HOST'),
                                      port=os.getenv('DB_PORT'),
                                      database=os.getenv('DB_DATABASE'))
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phones;")
        data = cursor.fetchall()
        update.message.reply_text(data)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        update.message.reply_text('jopa')
        print('error')
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()


def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки ')
    return 'verify_password'


def verify_password(update: Update, context):
    user_input = update.message.text

    passRegex = re.compile(
        r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()]).{8,}$')

    if re.match(passRegex, user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END


def findEmailCommand(update: Update, context):
    update.message.reply_text(
        'Введите текст для поиска адресов электронных почт: ')

    return 'find_email'


def find_email(update: Update, context: CallbackContext):
    user_input = update.message.text

    EmailRegex = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
    global EmailList
    EmailList = EmailRegex.findall(user_input)

    if not EmailList:
        update.message.reply_text('Электронные почты не найдены')
        return

    Email = ''
    for i in range(len(EmailList)):
        Email += f'{i+1}. {EmailList[i]}\n'

    update.message.reply_text(Email)
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data='email'),
            InlineKeyboardButton("Нет", callback_data='db_no')
        ]
    ]
    reply = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Хотите записать найденные адреса в базу данных?', reply_markup=reply)
    return ConversationHandler.END


def response(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'email':
        #global connection
        try:

            connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                      password=os.getenv('DB_PASSWORD'),
                                      host=os.getenv('DB_HOST'),
                                      port=os.getenv('DB_PORT'),
                                      database=os.getenv('DB_DATABASE'))
            cursor = connection.cursor()
            connection.autocommit = True
            for i in EmailList:
                print(i)
                cursor.execute("INSERT INTO emails(email) VALUES (%s);", (i,))

            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            print('error')
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
        query.answer("Адреса успешно записаны в базу данных.")
    elif query.data == 'phone':
        #global connection
        try:

            connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                      password=os.getenv('DB_PASSWORD'),
                                      host=os.getenv('DB_HOST'),
                                      port=os.getenv('DB_PORT'),
                                      database=os.getenv('DB_DATABASE'))
            cursor = connection.cursor()
            connection.autocommit = True
            for i in phoneNumberList:
                print(i)
                cursor.execute("INSERT INTO phones(phone) VALUES (%s);", (i,))

            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            print('error')
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
        query.answer("Адреса успешно записаны в базу данных.")
    else:
        query.answer("Произошла ошибка")

    return ConversationHandler.END


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'


def find_phone_number(update: Update, context):
    # Получаем текст, содержащий(или нет) номера телефонов
    user_input = update.message.text

    # формат 8 (000) 000-00-00
    phoneNumRegex = re.compile(
        r'(?:\+7|8)(?:[\- ]?\d{3}){2}[\- ]?\d{2}[\- ]?\d{2}')
    global phoneNumberList
    phoneNumberList = phoneNumRegex.findall(
        user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        # Записываем очередной номер
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n'

    # Отправляем сообщение пользователю
    update.message.reply_text(phoneNumbers)
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data='phone'),
            InlineKeyboardButton("Нет", callback_data='db_no')
        ]
    ]
    reply = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Хотите записать найденные номера в базу данных?', reply_markup=reply)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler(
            'find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
        },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
        },
        fallbacks=[]
    )

    convHandlerpass = ConversationHandler(
        entry_points=[CommandHandler(
            'verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", command))
    dp.add_handler(CommandHandler("get_uptime", command))
    dp.add_handler(CommandHandler("get_uname", command))
    dp.add_handler(CommandHandler("get_df", command))
    dp.add_handler(CommandHandler("get_free", command))
    dp.add_handler(CommandHandler("get_mpstat", command))
    dp.add_handler(CommandHandler("get_w", command))
    dp.add_handler(CommandHandler("get_auths", command))
    dp.add_handler(CommandHandler("get_critical", command))
    dp.add_handler(CommandHandler("get_ps", command))
    dp.add_handler(CommandHandler("get_ss", command))
    dp.add_handler(CommandHandler("get_services", command))
    dp.add_handler(CommandHandler("get_emails", find_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", find_phones))
    dp.add_handler(CommandHandler("get_repl_logs", log))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerpass)

    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CallbackQueryHandler(response))
    dp.add_handler(MessageHandler(Filters.text & ~
                   Filters.command, handle_reply))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
