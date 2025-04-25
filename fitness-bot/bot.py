import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    init_db,
    populate_data,
    get_trainers, 
    get_workouts,
    get_gyms,
)
import requests
from datetime import datetime, timedelta

API_TOKEN = "7906442959:AAF9zFAQrXY_j4B3LomHFbuSS2RkCe-CI0A"
FLASK_URL = "http://127.0.0.1:5000/booking"

bot = telebot.TeleBot(API_TOKEN)

init_db()
populate_data()

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Записаться на тренировку", callback_data="book"))
    markup.add(InlineKeyboardButton("Расписание тренировок", callback_data="price"))
    markup.add(InlineKeyboardButton("Залы", callback_data="branches"))
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в фитнес-бот! Выберите действие:",
        reply_markup=main_menu(),
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "book":
        show_trainers(call.message)
    elif call.data == "price":
        send_schedule(call.message)
    elif call.data == "branches":
        send_gyms(call.message)
    elif call.data.startswith("trainer_"):
        select_workout(call)
    elif call.data.startswith("workout_"):
        select_date(call)
    elif call.data.startswith("date_"):
        select_time(call)
    elif call.data.startswith("time_"):
        select_gym(call)
    elif call.data.startswith("gym_"):
        request_client_info(call)

def show_trainers(message):
    markup = InlineKeyboardMarkup()
    trainers = get_trainers() 
    for idx, (name, rating) in enumerate(trainers):
        markup.add(
            InlineKeyboardButton(
                f"{name} (Рейтинг: {rating})", callback_data=f"trainer_{idx}"
            )
        )
    bot.send_message(message.chat.id, "Выберите тренера:", reply_markup=markup)

def select_workout(call):
    trainer_id = call.data.split("trainer_")[1]
    workouts = get_workouts() 
    markup = InlineKeyboardMarkup()
    for idx, (workout, price) in enumerate(workouts):
        markup.add(
            InlineKeyboardButton(
                f"{workout} - {price} тг", callback_data=f"workout_{trainer_id}_{idx}"
            )
        )
    bot.edit_message_text(
        "Выберите тренировку:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
    )

def select_date(call):
    data = call.data.split("_")
    trainer_id, workout_id = data[1], data[2]
    markup = InlineKeyboardMarkup()
    for i in range(7):
        date = (datetime.now() + timedelta(days=i)).strftime("%d-%m-%Y")
        markup.add(
            InlineKeyboardButton(
                date, callback_data=f"date_{trainer_id}_{workout_id}_{date}"
            )
        )
    bot.edit_message_text(
        "Выберите дату:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
    )

def select_time(call):
    data = call.data.split("_")
    trainer_id, workout_id, date = data[1], data[2], data[3]
    markup = InlineKeyboardMarkup()
    for hour in range(7, 23):
        time = f"{hour}:00"
        markup.add(
            InlineKeyboardButton(
                time, callback_data=f"time_{trainer_id}_{workout_id}_{date}_{time}"
            )
        )
    bot.edit_message_text(
        "Выберите время:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
    )

def select_gym(call):
    data = call.data.split("_")
    trainer_id, workout_id, date, time = data[1], data[2], data[3], data[4]
    gyms = get_gyms() 
    markup = InlineKeyboardMarkup()
    for idx, (gym, _) in enumerate(gyms):
        markup.add(
            InlineKeyboardButton(
                gym,
                callback_data=f"gym_{trainer_id}_{workout_id}_{date}_{time}_{idx}",
            )
        )
    bot.edit_message_text(
        "Выберите зал:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
    )

def request_client_info(call):
    data = call.data.split("_")
    trainer_id, workout_id, date, time, gym_id = (
        data[1],
        data[2],
        data[3],
        data[4],
        data[5],
    )
    msg = bot.send_message(call.message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(
        msg, get_phone, trainer_id, workout_id, date, time, gym_id
    )

def get_phone(message, trainer_id, workout_id, date, time, gym_id):
    name = message.text
    msg = bot.send_message(message.chat.id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(
        msg, save_booking, trainer_id, workout_id, date, time, gym_id, name
    )

def save_booking(message, trainer_id, workout_id, date, time, gym_id, name):
    phone = message.text
    trainers = get_trainers()
    workouts = get_workouts()
    gyms = get_gyms()
    trainer = trainers[int(trainer_id)][0]
    workout = workouts[int(workout_id)][0]
    gym = gyms[int(gym_id)][0]
    # Удаляем локальное добавление заявки, оставляем только POST-запрос на Flask
    requests.post(
        FLASK_URL,
        json={
            "name": name,
            "phone": phone,
            "trainer": trainer,
            "workout": workout,
            "date": date,
            "time": time,
            "gym": gym,
        },
    )
    bot.send_message(
        message.chat.id,
        f"Запись подтверждена!\nТренер: {trainer}\nТренировка: {workout}\nДата: {date}\nВремя: {time}\nЗал: {gym}",
    )
    bot.send_message(message.chat.id, "Спасибо за запись!", reply_markup=main_menu())

def send_schedule(message):
    workouts = get_workouts()
    schedule = "\n".join([f"{workout[0]} - {workout[1]} тг" for workout in workouts])
    bot.send_message(message.chat.id, f"Наши тренировки и цены:\n\n{schedule}")

def send_gyms(message):
    gyms = get_gyms()
    gym_info = "\n".join(
        [f"{gym[0]} - [Посмотреть на карте]({gym[1]})" for gym in gyms]
    )
    bot.send_message(
        message.chat.id, f"Наши залы:\n\n{gym_info}", parse_mode="Markdown"
    )

print("Бот запущен")
bot.infinity_polling()