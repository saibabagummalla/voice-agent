import sqlite3
import datetime as dt

DB = "bookings.db"
SLOTS = [f"{h:02d}:00" for h in range(10, 18)]  # 10:00 to 17:00


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            UNIQUE(date, time))""")


def _check_date(date):
    try:
        d = dt.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."
    if d < dt.date.today():
        return "That date is in the past."
    if d.weekday() == 6:
        return "The clinic is closed on Sundays."
    return None


def check_availability(date):
    err = _check_date(date)
    if err:
        return {"error": err}
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT time FROM bookings WHERE date=?", (date,))
        taken = {r[0] for r in rows}
    return {"date": date, "free_slots": [s for s in SLOTS if s not in taken]}


def book_appointment(name, date, time):
    err = _check_date(date)
    if err:
        return {"error": err}
    if time not in SLOTS:
        return {"error": "Time must be on the hour between 10:00 and 17:00."}
    try:
        with sqlite3.connect(DB) as con:
            con.execute("INSERT INTO bookings (name, date, time) VALUES (?, ?, ?)",
                        (name, date, time))
    except sqlite3.IntegrityError:
        return {"error": "That slot is already taken."}
    return {"status": "confirmed", "name": name, "date": date, "time": time}


TOOLS = [
    {"type": "function", "function": {
        "name": "check_availability",
        "description": "Get the free appointment slots for a date.",
        "parameters": {"type": "object",
                       "properties": {"date": {"type": "string",
                                               "description": "Date as YYYY-MM-DD"}},
                       "required": ["date"]}}},
    {"type": "function", "function": {
        "name": "book_appointment",
        "description": "Book an appointment. Call only after the caller confirmed name, date and time.",
        "parameters": {"type": "object",
                       "properties": {
                           "name": {"type": "string", "description": "Caller's full name"},
                           "date": {"type": "string", "description": "Date as YYYY-MM-DD"},
                           "time": {"type": "string", "description": "24-hour HH:MM, on the hour, e.g. 14:00"}},
                       "required": ["name", "date", "time"]}}},
]

FUNCTIONS = {"check_availability": check_availability,
             "book_appointment": book_appointment}