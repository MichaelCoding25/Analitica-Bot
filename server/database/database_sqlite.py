# Handles the database
import sqlite3
from start import CURRENT_DIR as CD

MEMBERS_DATABASE_DIRECTORY = CD + '/server/database/members.db'


def create_members_info_table():
    """
    Creates the members_info table if one does not exist in the db file and inputs all needed columns.
    :return:
    """
    conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS members_info (
                        mem_id      TEXT    NOT NULL,
                        date_time    INTEGER NOT NULL,
                        status_id   INTEGER,
                        activity_id INTEGER
                    );
        """)
        conn.commit()
    except:
        print("Was unable to create the members_info table in the Database.")
    conn.close()


def create_activities_table():
    """
    Creates the activities table if one does not exist in the db file and inputs all needed columns.
    :return:
    """
    conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS activities (
                        id       INTEGER PRIMARY KEY AUTOINCREMENT,
                        act_name TEXT    NOT NULL
                    );
        """)
        conn.commit()
    except:
        print("Was unable to create the activities table in the Database.")
    conn.close()


def create_statuses_table():
    """
    Creates the statuses table if one does not exist in the db file and inputs all needed columns and values.
    :return:
    """
    conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS statuses (
                        id      INTEGER PRIMARY KEY AUTOINCREMENT,
                        st_name TEXT    NOT NULL
                    );         
        """)
        conn.commit()
        c.execute("SELECT id FROM statuses")
        if len(c.fetchall()) == 0:
            c.execute("""INSERT INTO statuses (id, st_name)
                         VALUES 
                         (1 , 'offline'),
                         (2 , 'online'),
                         (3 , 'idle'),
                         (4 , 'dnd');
            """)
            conn.commit()
    except:
        print("Was unable to create the statuses table in the Database.")
    conn.close()


def create_perms_tables():
    """
    Creates a permission table if one does not exist in the db file and inputs all needed columns and default values.
    (For future permissions system implementation)
    """
    conn = sqlite3.connect(MEMBERS_DATABASE_DIRECTORY)
    c = conn.cursor()
    try:
        c.execute(f"""CREATE TABLE IF NOT EXISTS role_perms (
                    d_role            TEXT    UNIQUE
                                              NOT NULL,
                    d_can_view_self   BOOLEAN NOT NULL,
                    d_can_view_others BOOLEAN NOT NULL,
                    d_can_view_server BOOLEAN NOT NULL,
                    d_can_view_roles  BOOLEAN NOT NULL,
                    d_can_view_perms  BOOLEAN NOT NULL
                );
        """)
        conn.commit()
        c.execute("""INSERT INTO role_perms
                     VALUES 
                     ('d_owner', 1, 1, 1, 1, 1),
                     ('d_admin', 1, 1, 0, 1, 1),
                     ('d_mod', 1, 1, 0, 1, 0),
                     ('d_mem', 1, 0, 0, 0, 0);
        """)
    except:
        print("Was unable to create the role_perms table in the Database.")
    conn.commit()
    conn.close()


def handle_database_overdraft():
    conn = sqlite3.connect()
    cursor = conn.cursor()
    days_string = f'-20 days'
    cursor.execute("DELETE FROM members_info WHERE date_time <"
                   "strftime('%s',datetime('now',?))", days_string)
    conn.commit()
    conn.close()
