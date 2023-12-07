import calendar
import datetime
import os
from datetime import timedelta

import telebot
from django import setup
from django.db.models import F
from django.db.models import Q
from django.utils import timezone
from telebot import types

import logging

logging.basicConfig(level=logging.INFO)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TaskDistribution.settings")
setup()

from main.models import Task, TaskAssignment, Employee, EmployeeConfirmation, Issue, Notes

from django.db import IntegrityError

bot_token = '6686182784:AAHa9r4tVJ6IQBRSPhlykrxPw9QzeahXxB0'
bot = telebot.TeleBot(bot_token)

states = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_registration = types.KeyboardButton("Регистрация")
    item_authorization = types.KeyboardButton("Авторизация")
    markup.add(item_registration, item_authorization)

    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=markup)


# Обработчик для команды '/start'
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создание кастомной клавиатуры с опциями регистрации и авторизации
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_registration = types.KeyboardButton("Регистрация")
    item_authorization = types.KeyboardButton("Авторизация")
    markup.add(item_registration, item_authorization)

    # Отправка приветственного сообщения с кастомной клавиатурой
    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=markup)


# Обработчик для опции 'Регистрация'
@bot.message_handler(func=lambda message: message.text == "Регистрация")
def handle_registration(message):
    bot.send_message(message.chat.id, "Введите логин:")
    bot.register_next_step_handler(message, process_login)


# Функция для обработки логина пользователя в процессе регистрации
def process_login(message):
    login = message.text
    # Проверка, содержит ли логин только буквы и цифры
    if not login.isalnum():
        bot.send_message(message.chat.id, "Логин не должен содержать специальных символов. Попробуйте еще раз.")
        handle_registration(message)
        return

    # Сохранение логина в состоянии пользователя
    states[message.from_user.id] = {'login': login}

    bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(message, process_password)


# Функция для обработки пароля пользователя в процессе регистрации
def process_password(message):
    login = states[message.from_user.id]['login']
    password = message.text

    # Проверка требований к паролю
    if not (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c.isascii() and not c.isalnum() for c in password)
            and len(password) >= 8
    ):
        bot.send_message(
            message.chat.id,
            "Пароль должен содержать не менее 8 символов, включая маленькие и большие буквы, цифры и специальные "
            "символы.",
        )
        handle_registration(message)
        return

    # Отправка сообщения об успешной регистрации и сохранение пользователя в базе данных
    # bot.send_message(message.chat.id, "Ваш аккаунт ожидает подтверждения. Можете попробовать авторизироваться.")
    try:
        bot.send_message(message.chat.id, "Введите ваше имя:")
        bot.register_next_step_handler(message, process_name, login, password)
    except IntegrityError:
        print("Ошибка IntegrityError.")
        pass
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        pass


def process_name(message, login, password):
    name = message.text

    # Повторите процесс для фамилии
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, process_surname, login, password, name)


def process_surname(message, login, password, name):
    surname = message.text

    # Повторите процесс для отчества
    bot.send_message(message.chat.id, "Введите ваше отчество (если есть):")
    bot.register_next_step_handler(message, process_patronymic, login, password, name, surname)


def process_patronymic(message, login, password, name, surname):
    patronymic = message.text

    # Повторите процесс для почты
    bot.send_message(message.chat.id, "Введите вашу почту:")
    bot.register_next_step_handler(message, process_email, login, password, name, surname, patronymic)


def process_email(message, login, password, name, surname, patronymic):
    email = message.text

    # Сохранение информации в базу данных
    bot.send_message(message.chat.id, "Ваш аккаунт ожидает подтверждения. Можете попробовать авторизироваться.")

    try:
        employee, created = Employee.objects.get_or_create(
            login=login, password=password, name=name, surname=surname, patronymic=patronymic, email=email
        )
        employee.save()
    except IntegrityError:
        print("Ошибка IntegrityError.")
        pass
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        pass


# Функция для отправки уведомления конкретному сотруднику
def send_notification(employee, message):
    print(f"Уведомление для сотрудника {employee}: {message}")


# Функция для отправки уведомлений о предстоящих сроках задач
def send_deadline_notifications():
    now = timezone.now()
    deadline_alert_time = now + timedelta(days=1)
    # Фильтрация задач с предупреждением о дедлайне на следующий день
    tasks_to_notify = Task.objects.filter(deadline=deadline_alert_time.date())
    for task in tasks_to_notify:
        # Отправка уведомления для каждой задачи
        send_notification(task.employee, f"Завтра дедлайн по задаче: {task.title}")
    # Обновление поля 'notifications_sent' для задач
    tasks_to_notify.update(notifications_sent=F('notifications_sent') + 1)


# Обработчик для опции 'Авторизация'
@bot.message_handler(func=lambda message: message.text == "Авторизация")
def handle_authorization(message):
    bot.send_message(message.chat.id, "Введите логин:")
    bot.register_next_step_handler(message, process_login_authorization)
    # Отправка уведомлений о дедлайнах после обработки авторизации
    send_deadline_notifications()


# Функция для обработки логина пользователя в процессе авторизации
def process_login_authorization(message):
    login = message.text
    bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(message, process_password_authorization, login)
    # Отправка уведомлений о дедлайнах после обработки авторизации
    send_deadline_notifications()


# Функция для обработки пароля пользователя в процессе авторизации
def process_password_authorization(message, login):
    # Отправка уведомлений о дедлайнах после обработки авторизации
    send_deadline_notifications()
    password = message.text
    employee = Employee.objects.filter(login=login, password=password).first()

    if employee:
        if employee.is_blocked:
            bot.send_message(message.chat.id, "Вы заблокированы. Обратитесь к администратору.")
            return

        # Сохранение логина в состоянии пользователя
        states[message.from_user.id] = {'login': login}
        confirmation = EmployeeConfirmation.objects.filter(Q(employee=employee)).first()

        if confirmation:
            # Создание кастомной клавиатуры для авторизованных пользователей
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item_get_tasks = types.KeyboardButton("Получение задач")
            item_task_list = types.KeyboardButton("Список задач в процессе выполнения")
            item_calendar = types.KeyboardButton("Показать календарь")
            item_logout = types.KeyboardButton("Выйти из аккаунта")
            markup.add(item_get_tasks, item_task_list, item_calendar, item_logout)

            # Отправка сообщения об успешной авторизации с кастомной клавиатурой
            bot.send_message(message.chat.id, "Авторизация успешна! Выберите действие:", reply_markup=markup)
            bot.clear_step_handler(message)
        else:
            bot.send_message(message.chat.id, "Не удалось войти в аккаунт! Возможно, его еще не подтвердили...")
            handle_authorization(message)
    else:
        bot.send_message(message.chat.id, "Неверный логин или пароль. Попробуйте еще раз.")


# Обработчик для опции 'Показать календарь'
@bot.message_handler(func=lambda message: message.text == "Показать календарь")
def handle_show_calendar(message):
    show_calendar(message)


# Функция для отображения календаря для выбора даты
def show_calendar(message):
    now = datetime.datetime.now()
    markup = types.InlineKeyboardMarkup(row_width=7)

    year = now.year
    month = now.month
    cal = calendar.monthcalendar(year, month)

    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=f"day_{day}"))

        markup.add(*row)

    # Отправка сообщения для выбора дня с сгенерированным календарем
    bot.send_message(message.chat.id, f"Выберите день:", reply_markup=markup)


# Обработчик обратного вызова для выбора дня в календаре
@bot.callback_query_handler(func=lambda call: call.data.startswith("day_"))
def handle_day_selection(call):
    selected_day = int(call.data.split("_")[1])
    selected_date = datetime.datetime.now().replace(day=selected_day)

    # Запрос пользователя на напоминание для выбранной даты
    bot.send_message(call.message.chat.id,
                     f"Вы выбрали {selected_date.strftime('%Y-%m-%d')}. Какое напоминание вы хотите выставить? ")
    bot.register_next_step_handler(call.message, save_note, selected_date)


# Функция для сохранения заметки для выбранной даты
def save_note(message, selected_date):
    login = states[message.from_user.id]['login']
    current_employee = Employee.objects.filter(login=login).first()

    if current_employee:
        # Создание и сохранение объекта Notes для выбранной даты
        note = Notes(employee=current_employee, date=selected_date, note=message.text)
        note.save()

        bot.send_message(message.chat.id, "Заметка успешно сохранена.")
    else:
        bot.send_message(message.chat.id, "Не удалось определить текущего сотрудника.")


# Функция для получения задач для определенного отдела
def get_department_tasks(department):
    tasks = Task.objects.filter(department=department)
    return tasks

# Обработчик для опции 'Получение задач'
@bot.message_handler(func=lambda message: message.text == "Получение задач")
def handle_get_tasks(message):
    # Отправка уведомлений о дедлайнах перед обработкой получения задач
    send_deadline_notifications()

    try:
        # Получение login из состояния пользователя
        login = states[message.from_user.id]['login']
        logging.info(f"User login: {login}")

        # Получение всех сотрудников с указанным логином
        employees_with_login = Employee.objects.filter(login=login)

        # Проверка, что есть хотя бы один сотрудник с таким логином
        if employees_with_login.exists():
            # Выбор первого сотрудника (может потребоваться лучше определить, какую запись вы хотите выбрать)
            current_employee = employees_with_login.first()
            logging.info(f"Employee found: {current_employee}")

            if current_employee.department is None:
                bot.send_message(message.chat.id, "В данный момент нет данных о вашем отделе. Обратитесь к администратору.")
                return

            # Получение задач для отдела текущего пользователя
            department_tasks = get_department_tasks(current_employee.department)

            if department_tasks:
                markup = types.InlineKeyboardMarkup(row_width=1)

                logging.info(f"Department tasks: {department_tasks}")

                for task in department_tasks:
                    if task.status != "В процессе":
                        # Создание кнопки для каждой задачи в отделе
                        task_button = types.InlineKeyboardButton(text=task.title, callback_data=f"task_{task.id}")
                        markup.add(task_button)

                # Отправка сообщения с выбором задачи из списка
                bot.send_message(message.chat.id, "Выберите задачу из списка:", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Ваш отдел не имеет задач.")
        else:
            logging.error("No employee found with the specified login.")
            bot.send_message(message.chat.id, "Не удалось найти информацию о вас в базе данных. Обратитесь к администратору.")

    except KeyError:
        logging.error("User login not found in states.")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        bot.send_message(message.chat.id, "Произошла неожиданная ошибка.")




# Регистрация обработчика для выбора задачи
@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def process_task_selection(query):
    try:
        task_id = int(query.data.split("_")[1])
        selected_task = Task.objects.get(id=task_id)
        user_id = query.from_user.id
        login = states[user_id]['login']
        employee = Employee.objects.filter(login=login).first()

        if selected_task and employee:
            if selected_task.difficulty > employee.rating:
                bot.send_message(query.message.chat.id, "У вас недостаточный уровень для выполнения этой задачи.")
                return

            selected_task.status = "В процессе"
            selected_task.save()

            task_assignment, created = TaskAssignment.objects.get_or_create(task=selected_task)
            if created:
                task_assignment.employee = employee
                task_assignment.save()

            if created:
                bot.send_message(query.message.chat.id,
                                 f"Выбранная вами задача '{selected_task.title}' зарезервирована за вами.")
            else:
                bot.send_message(query.message.chat.id, f"Вы уже взяли задачу '{selected_task.title}'.")
        else:
            pass
    except (IndexError, ValueError, Task.DoesNotExist):
        pass


# Обработчик для опции 'Список задач в процессе выполнения'
@bot.message_handler(func=lambda message: message.text == "Список задач в процессе выполнения")
def handle_all_task_list(message):
    all_tasks = TaskAssignment.objects.all()
    # Отправка списка задач с использованием кастомной клавиатуры
    send_task_list(message, all_tasks, is_inline=True)


# Функция для отправки списка задач
def send_task_list(message, task_assignments, is_inline=False):
    # Отправка уведомлений о дедлайнах перед отправкой списка задач
    send_deadline_notifications()

    if task_assignments:
        markup = types.InlineKeyboardMarkup(row_width=1) if is_inline else types.ReplyKeyboardMarkup(
            resize_keyboard=True)

        for task_assignment in task_assignments:
            task = task_assignment.task
            task_buttons = [
                types.InlineKeyboardButton(text=task.title, callback_data=f"task_{task.id}"),
                types.InlineKeyboardButton(text="Сдвинуть срок", callback_data=f"postpone_{task.id}"),
                types.InlineKeyboardButton(text="Отказ от задачи", callback_data=f"reject_{task.id}"),
                types.InlineKeyboardButton(text="Выполнил задачу", callback_data=f"complete_{task.id}")
            ]
            markup.add(*task_buttons)

        if is_inline:
            try:
                bot.send_message(message.chat.id, "Все задачи:", reply_markup=markup)
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            bot.send_message(message.chat.id, "Выберите задачу для завершения:", reply_markup=markup)
            bot.register_next_step_handler(message, complete_task_handler)
    else:
        bot.send_message(message.chat.id, "Нет задач в процессе выполнения.")


# Обработчик обратного вызова для команды 'postpone_'
@bot.callback_query_handler(func=lambda call: 'postpone_' in call.data)
def move_deadline_handler(call):
    # Запрос причины смены срока и нового срока
    bot.send_message(call.message.chat.id, "Введите причину смены срока также срок на который хотите сдвинуть:")
    bot.register_next_step_handler(call.message, process_move_deadline, call.data)


# Обработчик обратного вызова для команды 'postpone_'
@bot.callback_query_handler(func=lambda call: 'task_' in call.data)
def move_deadline_handler():
    pass


# Функция для обработки запроса смены срока задачи
def process_move_deadline(message, callback_data):
    task_id = int(callback_data.split('_')[1])
    reason = message.text
    login = states[message.from_user.id]['login']
    current_employee = Employee.objects.filter(login=login).first()
    selected_task = Task.objects.filter(id=task_id).first()

    if selected_task and current_employee:
        # Создание и сохранение объекта Issue для запроса смены срока
        issue = Issue(task=selected_task, employee=current_employee, status=reason)
        issue.save()
        bot.send_message(message.chat.id, "запрос отправлен на обработку.")
    else:
        error_message = f"Ошибка при обработке запроса. selected_task: {selected_task}, current_employee: {current_employee}"
        bot.send_message(message.chat.id, error_message)


# Обработчик обратного вызова для команды 'reject_'
@bot.callback_query_handler(func=lambda call: 'reject_' in call.data)
def reject_task_handler(call):
    task_id = int(call.data.split('_')[1])
    login = states[call.from_user.id]['login']
    current_employee = Employee.objects.filter(login=login).first()
    selected_task = Task.objects.filter(id=task_id).first()

    if selected_task and current_employee:
        selected_task.status = 'Свободна'
        current_employee.rating -= 1
        selected_task.save()
        current_employee.save()

        task_assignment = TaskAssignment.objects.filter(task=selected_task, employee=current_employee).first()
        if task_assignment:
            task_assignment.delete()

        bot.send_message(call.message.chat.id, "Вы отказались от задачи.")
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при обработке запроса.")


# Обработчик обратного вызова для команды 'complete_'
@bot.callback_query_handler(func=lambda call: 'complete_' in call.data)
def complete_task_handler(call):
    user_id = call.from_user.id
    logging.info(f"Handling complete_task_callback for user_id: {user_id}")

    # Проверка наличия ключа 'login' в словаре states
    user_data = states.get(user_id, {})
    logging.info(f"user_data: {user_data}")

    login = user_data.get('login') if user_data else None
    logging.info(f"login: {login}")

    # Использование get в Django-запросах
    try:
        current_employee = Employee.objects.filter(login=login) if login else None
        task_id = int(call.data.split('_')[1])
        selected_task = Task.objects.get(id=task_id) if task_id else None

        if selected_task and current_employee:
            try:
                # Использование update вместо save
                Task.objects.filter(id=task_id).update(status='Выполнено')
                Employee.objects.filter(login=login).update(rating=F('rating') + 1)

                bot.send_message(call.message.chat.id, "Задача успешно выполнена.")
            except Task.DoesNotExist:
                bot.send_message(call.message.chat.id, "Не удалось найти задачу.")
            except Employee.DoesNotExist:
                bot.send_message(call.message.chat.id, "Не удалось найти сотрудника.")
        else:
            bot.send_message(call.message.chat.id, "Произошла ошибка при обработке запроса.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        bot.send_message(call.message.chat.id, "Произошла неожиданная ошибка.")



# Обработчик для опции 'Выйти из аккаунта'
@bot.message_handler(func=lambda message: message.text == "Выйти из аккаунта")
def handle_logout(message):
    # Отправка уведомлений о дедлайнах перед выходом из аккаунта
    send_deadline_notifications()
    # Удаление кастомной клавиатуры и переход в начальное состояние
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Вы успешно вышли из аккаунта.", reply_markup=markup)

    # Создание начальной клавиатуры для выбора действия
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_registration = types.KeyboardButton("Регистрация")
    item_authorization = types.KeyboardButton("Авторизация")
    markup.add(item_registration, item_authorization)

    # Отправка сообщения с начальной клавиатурой
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
