import os
import sqlite3

DB_NAME = os.path.join(os.path.dirname(__file__), "fitness_bot.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rating REAL
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS gyms (
            id INTEGER PRIMARY KEY,
            name TEXT,
            url_map TEXT
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            trainer TEXT,
            workout TEXT,
            date TEXT,
            time TEXT,
            gym TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def populate_data():
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        """
        INSERT OR IGNORE INTO trainers (id, name, rating) VALUES 
        (1, 'Андрей', 4.6), 
        (2, 'Виктория', 4.8), 
        (3, 'Бейбарыс', 4.5)
    """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO workouts (id, name, price) VALUES 
        (1, 'Обычная тренировка', 5000), 
        (2, 'Групповая тренировка', 3000), 
        (3, 'Индивидуальная тренировка', 7000)
    """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO gyms (id, name, url_map) VALUES 
        (1, 'Абай 52', 'https://2gis.kz/almaty/search/%D0%90%D0%B1%D0%B0%D1%8F%2052/geo/9430047375009170/76.91341%2C43.23982'), 
        (2, 'Сатпаева 66', 'https://2gis.kz/almaty/geo/9430047375103401?m=77.066627%2C43.309279%2F16')
    """
    )
    conn.commit()
    conn.close()


def get_trainers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, rating FROM trainers")
    trainers = cursor.fetchall()
    conn.close()
    return trainers


def get_workouts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM workouts")
    workouts = cursor.fetchall()
    conn.close()
    return workouts


def get_gyms():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, url_map FROM gyms")
    gyms = cursor.fetchall()
    conn.close()
    return gyms


def add_booking(name, phone, trainer, workout, date, time, gym):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (name, phone, trainer, workout, date, time, gym) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, phone, trainer, workout, date, time, gym),
    )
    conn.commit()
    conn.close()


def get_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, phone, trainer, workout, date, time, gym FROM bookings"
    )
    bookings = cursor.fetchall()
    conn.close()
    return bookings


def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()