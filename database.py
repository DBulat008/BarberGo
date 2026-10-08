import sqlite3


def create_database():
    connection = sqlite3.connect("barber.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            master TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()
def save_booking(
        service,
        master,
        date,
        time,
        name,
        phone
):
    connection = sqlite3.connect("barber.db")
    cursor=connection.cursor()
    cursor.execute(
        """
        INSERT INTO bookings (
            service,
            master,
            date,
            time,
            name,
            phone
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
           service,
            master,
            date,
            time,
            name,
            phone
        )  
    )
    connection.commit()
    connection.close()
def is_time_available(master, date, time):
    connection = sqlite3.connect("barber.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM bookings
        WHERE master = ?
          AND date = ?
          AND time = ?
        LIMIT 1
        """,
        (master, date, time)
    )

    result = cursor.fetchone()

    connection.close()

    return result is None