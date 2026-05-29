"""
Handles interaction between the bot and the database.
Important: All database actions should go through this class. No SQL in other files!
"""
import logging
import sqlite3
import sys

logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - %(message)s",
                    handlers=[
                        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
                              logging.StreamHandler(stream=sys.stdout)
                    ])

class DatabaseManager:
    def __init__(self):
        """
        Sets up the sqlite3 database connection.
        """
        self.conn = sqlite3.connect("data/db.sqlite")
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """
        Creates the tables in the database if they don't yet exist.
        """
        users_table = """
        CREATE TABLE IF NOT EXISTS users
        (
            id                 INTEGER PRIMARY KEY,
            nr_events_attended INTEGER DEFAULT 0
        );
        """

        events_table = """
        CREATE TABLE IF NOT EXISTS events
        (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            division    TEXT,
            type        TEXT,
            host_id     INTEGER,
            timestamp   TEXT,
            channel_id  INTEGER,
            msg_id      INTEGER,
            FOREIGN KEY (host_id) REFERENCES users (id)
        );
        """

        participants_table = """
        CREATE TABLE IF NOT EXISTS event_participants
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_id  INTEGER,
            FOREIGN KEY (event_id) REFERENCES events (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """

        try:
            self.cursor.execute(users_table)
            self.cursor.execute(events_table)
            self.cursor.execute(participants_table)
            self.conn.commit()
            return 1
        except Exception as e:
            logger.error(e)
            return -1

    def add_user(self, user_id: int):
        """
        Adds a user using its id.
        """
        query = "INSERT INTO users VALUES (?, 0)"

        try:
            self.cursor.execute(query, (user_id,))
            self.conn.commit()
            return 1
        except Exception as e:
            logger.error(e)
            return -1

    def add_event_participants(self, event_id, participants):
        """
        Adds a list of participants to the event_participants table using their ids.
        If a user isn't yet known, it will also be added here.
        """
        try:
            for p_id in participants:
                if not self.get_user(p_id):
                    self.add_user(p_id)

                query = "INSERT INTO event_participants(event_id, user_id) VALUES (?, ?)"
                self.cursor.execute(query, (event_id, p_id))
                query = "UPDATE users SET nr_events_attended = nr_events_attended + 1 WHERE id = ?"
                self.cursor.execute(query, (p_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            return -1

    def get_event_participants(self, event_id: int):
        """
        Get a list of participants from the event_participants table using the event id.
        """
        query = "SELECT user_id FROM event_participants WHERE event_id = ?"

        try:
            self.cursor.execute(query, (event_id,))
            participants = self.cursor.fetchall()
            return participants
        except Exception as e:
            logger.error(e)
            return -1

    def add_event(self, event):
        """
        Adds an event to the events table.
        This function also calls the add_event_participants function.
        Expected format for the event dict:
        {
        "division": string,
        "type": string,
        "host_id": int,
        "participants": list of integers,
        "timestamp": datetime,
        "msg_id": int,
        }
        """
        query = "INSERT INTO events(division, type, host_id, timestamp, channel_id, msg_id) VALUES (?, ?, ?, ?, ?, ?)"
        try:
            self.cursor.execute(query, (event["division"], event["type"], event["host_id"],
                                        event["timestamp"].isoformat(), event["channel_id"], event["msg_id"]))

            query = "SELECT id FROM events"
            res = self.cursor.execute(query)
            event_id = res.fetchall()[-1][0]

            self.add_event_participants(event_id, event["participants"])
            self.conn.commit()
            return 1
        except Exception as e:
            logger.error(e)
            return -1

    def update_event_type(self, event_id, event_type):
        """
        Update the event's type
        """
        query = "UPDATE events SET type = ?  WHERE id = ?"

        try:
            self.cursor.execute(query, (event_type, event_id))
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            return -1

    def get_user(self, user_id: int):
        """
        Get a user's database entry from its id.
        """
        query = "SELECT * FROM users WHERE id = ?"

        try:
            self.cursor.execute(query, (user_id,))
            user = self.cursor.fetchone()
            return user
        except Exception as e:
            logger.error(e)
            return -1

    def get_event(self, event_id: int):
        """
        Get an event's database entry from its id.
        """
        query = "SELECT * FROM events WHERE id = ?"

        try:
            self.cursor.execute(query, (event_id,))
            event = self.cursor.fetchone()
            return event
        except Exception as e:
            logger.error(e)
            return -1

    def get_event_by_msg_id(self, msg_id: int):
        """
        Get an event's database entry from its message id.
        """
        query = "SELECT * FROM events WHERE msg_id = ?"

        try:
            self.cursor.execute(query, (msg_id,))
            event = self.cursor.fetchone()
            return event
        except Exception as e:
            logger.error(e)
            return -1

    def get_events_by_user(self, user_id: int):
        """
        Get all events by a user's id.
        """
        query = "SELECT * FROM event_participants WHERE user_id = ?"

        try:
            self.cursor.execute(query, (user_id,))
            events = self.cursor.fetchall()
            return events
        except Exception as e:
            logger.error(e)
            return -1

    def get_events_by_division(self, division: str):
        """
        Get all events from a division.
        """
        query = "SELECT * FROM events WHERE division = ?"
        try:
            self.cursor.execute(query, (division,))
            events = self.cursor.fetchall()
            return events
        except Exception as e:
            logger.error(e)
            return -1
