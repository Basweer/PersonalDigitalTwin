import sqlite3

DATABASE = "digital_twin.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():

    connection = get_db_connection()

    # Student table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            course TEXT,
            skills TEXT,
            goals TEXT
        )
    """)

    # Activity table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            activity_name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            activity_date TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES student(id)
        )
    """)

    # Goals table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            goal_name TEXT NOT NULL,
            target TEXT,
            progress INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES student(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")