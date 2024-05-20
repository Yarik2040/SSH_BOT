import paramiko
import logging
import re
import os
import psycopg2


from dotenv import load_dotenv
from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()

TOKEN = os.getenv('TOKEN')
buff = list()

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет, {user.full_name}! Вводи /help, чтобы увидеть список команд')


def helpCommand(update: Update, context):
    msg = [
        'Блок работы с текстом',
        '/find_email - Поиск Email адресов в тексте',
        '/find_phone_number - Поиск телефонных номеров в тексте',
        '',
        'Блок проверки паролей',
        '/verify_password - Проверка сложности пароля',
        '',
        'Блок мониторинга Linux-системы',
        '/get_release - Информация о релизе',
        '/get_uname - Информация об архитектуры процессора, имени хоста системы и версии ядра',
        '/get_uptime - Время работы',
        '/get_df - Состояние файловой системы ',
        '/get_free - Состояние оперативной памяти',
        '/get_mpstat - Производительности системы',
        '/get_w - Работающие в данной системе пользователи',
        '/get_auths - Последние 10 входов в систему',
        '/get_critical - Последние 5 критических события',
        '/get_ps - Запущенные процессы',
        '/get_ss - Используемые порты',
        '/get_apt_list - Установленные пакеты',
        '/get_services - Запущенные сервисы',
        '',
        'Блок работы с базой данных',
        '/get_repl_logs - Логи репликации',
        '/get_emails - Таблица Email адресов',
        '/get_phone_numbers - Таблца номеров телефонов'
    ]

    update.message.reply_text("\n".join(msg))

# ========== Find Email ==========

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email адресов: ')
    logging.info(f'Find_Email: trigered by: @{update.effective_user.username}')

    return 'find_email'

def findEmails(update: Update, context):
    global buff
    buff = list()

    user_input = update.message.text 
    strings_input = list(user_input.split('\n')) # Ввод по строчкам

    emailList = list()
    # r'\b[a-zA-Z0-9._%+-]+(?<!\.\.)@[a-zA-Z0-9.-]+(?<!\.)\.[a-zA-Z]{2,}\b'
    emailRegex = re.compile(r"[\w\-+.]+@[\w\-+.]+\.[A-Za-z]+") 
    
    for string in strings_input:
        foundEmails = emailRegex.findall(string)
        emailList += foundEmails # Добавляем к списку с найденными email список новых Email оператором +
        for email in foundEmails:
            logging.debug(f'Found Email {email}')
    
    if not emailList:
        update.message.reply_text('Email адреса не найдены')
        logging.info('Find_Email: stoped. No Emails found')
        return ConversationHandler.END

    response = 'Найденные Email адреса: \n'
    for i in range(len(emailList)):
        buff.append(emailList[i])
        response += f'{i + 1}. {emailList[i]} \n'

    update.message.reply_text(response)
    logging.info(f'Find_Email: stoped. Found {len(emailList)} Emails')
    update.message.reply_text('Хотите ли вы добавить эти адреса в базу данных? (да/нет)')
    return 'insert_email'

def insertEmail(update: Update, context):
    logging.info(f'insertEmail triggered by @{update.effective_user.username}')
    global buff
    user_input = update.message.text
    if user_input.lower() == 'нет':
        update.message.reply_text("В базу не было внесено изменений")
        logging.info(f'insertEmail: stoped. Without chanhing DB')
        buff = list()
        return ConversationHandler.END
    elif user_input.lower() == 'да':
        table = 'emails (Email)'
        values = ''
        for elem in buff:
            values += f"('{elem}'), "
        values = values[:-2] # Убираем лишний пробел и запятую
        Insert_status = SQLInsert(table, values)
        if not Insert_status:
            logging.error(f'insertEmail: Changing DB was failed')
            update.message.reply_text('Ошибка записи в базу данных')
            logging.info(f'insertEmail: stoped with error')
            buff = list()
            return ConversationHandler.END
        else:
            update.message.reply_text('Запись в базу данных прошла успешно')
            logging.info(f'insertEmail: stoped with succes. Added {len(buff)} Emails')
            buff = list()
            return ConversationHandler.END
        
    else:
        update.message.reply_text("Пожалуйста введите да или нет")
        logging.error(f'insertEmail error Bad Input by @{update.effective_user.username}')
        return 'insert_email'



# ========== Find Phone Numbers ==========

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    logging.info(f'Find_Phone_Numbers: trigered by: @{update.effective_user.username}')

    return 'find_phone_number'

def findPhoneNumbers (update: Update, context):
    global buff
    buff = list()

    user_input = update.message.text 
    strings_input = list(user_input.split('\n'))

    phoneNumRegex = re.compile(r'(^|\s)(\+7|8)[\s-]?\(?(\d{3})\)?[\s-]?(\d{3})[\s-]?(\d{2})[\s-]?(\d{2})($|\s)') 

    phoneNumberList = list()
    for string in strings_input:
        foundPhoneNumbers = phoneNumRegex.findall(string)
        phoneNumberList += foundPhoneNumbers 
        for phoneNumber in foundPhoneNumbers:
            logging.debug(f'Found phoneNumber {phoneNumber}')

    if not phoneNumberList: 
        update.message.reply_text('Телефонные номера не найдены')
        logging.info('Find_Phone_Numbers: stoped. No Phone Numbers found')
        return ConversationHandler.END
    
    phoneNumbers = 'Найденные номера телефонов:\n' 
    for i in range(len(phoneNumberList)):
        var = "".join(phoneNumberList[i])
        buff.append(var)
        humanOutput = f'{var}'
        phoneNumbers += f'{i+1}. {humanOutput}\n' 
    
    update.message.reply_text(phoneNumbers) 
    update.message.reply_text('Хотите ли вы добавить эти номера в базу данных? (да/нет)')
    logging.info(f'Find_Phone_Numbers: stoped. {len(phoneNumberList)} Phone Numbers found')
    return 'insert_phone_number' 

def insertPhoneNumber(update: Update, context):
    logging.info(f'insertPhoneNumber triggered by @{update.effective_user.username}')
    global buff
    user_input = update.message.text
    if user_input.lower() == 'нет':
        update.message.reply_text("В базу не было внесено изменений")
        logging.info(f'insertPhoneNumber: stoped. Without chanhing DB')
        buff = list()
        return ConversationHandler.END
    elif user_input.lower() == 'да':
        table = 'phonenumbers (PhoneNumber)'
        values = ''
        for elem in buff:
            values += f"('{elem}'), "
        values = values[:-2] # Убираем лишний пробел и запятую
        Insert_status = SQLInsert(table, values)
        if not Insert_status:
            logging.error(f'insertPhoneNumber: Changing DB was failed')
            update.message.reply_text('Ошибка записи в базу данных')
            logging.info(f'insertPhoneNumber: stoped with error')
            buff = list()
            return ConversationHandler.END
        else:
            update.message.reply_text('Запись в базу данных прошла успешно')
            logging.info(f'insertPhoneNumber: stoped with succes. Added {len(buff)} Emails')
            buff = list()
            return ConversationHandler.END
        
    else:
        update.message.reply_text("Пожалуйста введите да или нет")
        logging.error(f'insertPhoneNumber error Bad Input by @{update.effective_user.username}')
        return 'insert_phone_number'


# ========== Verify Password ==========

def findVerifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки на сложность: ')
    logging.info(f'Verify_Password: trigered by: @{update.effective_user.username}')

    return 'verify_password'

def VerifyPassword(update: Update, context):
    user_input = update.message.text
    passwordRegex = re.compile(r'(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*()])[0-9a-zA-Z!@#$%^&*()]{8,}')
    if passwordRegex.search(user_input):
        update.message.reply_text('Пароль сложный')
        logging.info(f'Verify_Password: stoped. Good password')
        return ConversationHandler.END 
    else:
        update.message.reply_text('Пароль простой')
        logging.info(f'Verify_Password: stoped. Bad password')
        return ConversationHandler.END 

# ========== Monitoring ==========
def CommandExecutor(command):

    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    logging.debug(f'CommadExecutor: stoped. Command: {command}, Answer: {data}')

    return data

def getRelease(update: Update, context):
    logging.info(f'getRelease triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('cat /etc/os-release')
    update.message.reply_text(f'Информация о релизе: {data}')

def getUname(update: Update, context):
    logging.info(f'getUname triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('uname --all')
    update.message.reply_text(f'Информация об архитектуры процессора, имени хоста системы и версии ядра: {data}')

def getUptime(update: Update, context):
    logging.info(f'getUptime triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('uptime')
    update.message.reply_text(f'Информация о времени работы: {data}')
            
def getDf(update: Update, context):
    logging.info(f'getDf triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('df -h')
    update.message.reply_text(f'Информация о состоянии файловой системы: {data}')

def getFree(update: Update, context):
    logging.info(f'getFree triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('free')
    update.message.reply_text(f'Информация о состоянии оперативной памяти: {data}')
    
def getMpstat(update: Update, context):
    logging.info(f'getMpstat triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('mpstat')
    update.message.reply_text(f'Информация о производительности системы: {data}')
    
def getW(update: Update, context):
    logging.info(f'getW triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('w')
    update.message.reply_text(f'Информация о работающих в данной системе пользователях: {data}')
    
def getAuths(update: Update, context):
    logging.info(f'getAuths triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('last -10') 
    update.message.reply_text(f'Последние 10 входов в систему: {data}')
    
def getCritical(update: Update, context):
    logging.info(f'getCritical triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('journalctl -r -p crit -n 5') # -r - Сначала новые, -p crit критические ошибки, -n 5 - количество ошибок
    update.message.reply_text(f'Последние 5 критических события: {data}')

def getPs(update: Update, context):
    logging.info(f'getPs triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('ps')
    update.message.reply_text(f'Информация о запущенных процессах: {data}')

def getSs(update: Update, context):
    logging.info(f'getSs triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('ss -l -n -t -u') 
    update.message.reply_text(f'Информация об используемых портах: {data}')
    
def getServices(update: Update, context):
    logging.info(f'getServices triggered by @{update.effective_user.username}')
    # Вывожу head -30, чтобы избежать ошибки с переполнением сообщения telegram
    data = "\n" + CommandExecutor('systemctl list-units --type=service | head -30') 
    update.message.reply_text(f'Информация о запущенных сервисах: {data}')

def getReplLogs(update: Update, context):
    logging.info(f'getReplLogs triggered by @{update.effective_user.username}')
    data = "\n" + CommandExecutor('cat /var/log/postgresql/* | grep -i "repl" | tail -20')
    update.message.reply_text(f'Логи репликации: {data}')

def findGetAptListCommand(update: Update, context):
    logging.info(f'getAptList trigered by @{update.effective_user.username}')
    # Для удобства разделил сообщение на строчки
    msg = 'Данная команда предполагает 2 режима \n'
    msg += '1) Вывод всех пакетов \n'
    msg += '2) Поиск информации о конкретном пакете \n'
    msg += 'Пожалуйста, выберите режим\n'
    msg += '(Введите 1 или 2)'
    update.message.reply_text(msg)
    
    return 'get_apt_first_mode'

def getAptFirstMode(update: Update, context):
    user_input = update.message.text
    if user_input.strip() == "1":
        data = "\n" + CommandExecutor('apt list --installed | head -30') # Ввёл ограничение, чтобы избежать ошибки слишком большого сообщения
        update.message.reply_text(f'Информация об установленных пакетах: {data}')
        logging.info('getAptList: stoped. First mode')
        return ConversationHandler.END
    elif user_input.strip() == "2":
        update.message.reply_text('Введите название пакета: ')
        return 'get_apt_second_mode'
    else:
        logging.error(f'getAptList: Bad input!')
        update.message.reply_text('Пожалуйста, введите 1 или 2')
        return 'get_apt_first_mode'

def getAptSecondMode(update: Update, context):
    user_input = update.message.text
    data = "\n" + CommandExecutor(f"apt-cache show {user_input.strip()}")
    update.message.reply_text(f"Информация о запрошенном пакете: {data}")
    logging.info('getAptList: stoped. Second mode')
    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

#========== DataBase ==========
def SQLInsert(table, values):
    connection = None

    try:
        connection = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'), 
            database=os.getenv('DB_DATABASE')
        )

        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {table} VALUES {values};")
        connection.commit()
        logging.info("Команда успешно выполнена")
        succes = True
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        succes = False
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")
            return succes
            

def SQLExecutor(command):
    connection = None
    try:
        connection = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'), 
            database=os.getenv('DB_DATABASE')
        )

        cursor = connection.cursor()
        cursor.execute(command)
        data = cursor.fetchall()
        logging.info("Команда успешно выполнена")
        return data

    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def getEmails(update: Update, context):
    raw_data = SQLExecutor("SELECT * FROM Emails;")
    data = 'База электронных адресов:'
    for string in raw_data:
        data += "\n" + str(string[0]) + ". " + str(string[1])
    logging.info(f'getEmails triggered by @{update.effective_user.username}')
    update.message.reply_text(data)

def getPhoneNumbers(update: Update, context):
    raw_data = SQLExecutor("SELECT * FROM PhoneNumbers;")
    data = 'База номеров телефонов:'
    for string in raw_data:
        data += "\n" + str(string[0]) + ". " + str(string[1])
    logging.info(f'getPhoneNumbers triggered by @{update.effective_user.username}')
    update.message.reply_text(data)

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'insert_email': [MessageHandler(Filters.text & ~Filters.command, insertEmail)]
        },
        fallbacks=[]
    )

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'insert_phone_number': [MessageHandler(Filters.text & ~Filters.command, insertPhoneNumber)]
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', findVerifyPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, VerifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', findGetAptListCommand)],
        states={
            'get_apt_first_mode': [MessageHandler(Filters.text & ~Filters.command, getAptFirstMode)],
            'get_apt_second_mode': [MessageHandler(Filters.text & ~Filters.command, getAptSecondMode)]
        },
        fallbacks=[]
    )
		
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerGetAptList)

    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(CommandHandler("get_services", getServices))

    dp.add_handler(CommandHandler("get_repl_logs", getReplLogs))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbers))
    dp.add_handler(CommandHandler("get_emails", getEmails))
		
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
