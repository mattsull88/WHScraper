from sqlite3 import Error
from connect_database import create_connection


def define_table():
    database = r"db\database3.db"

    sql_create_items_table = """ CREATE TABLE IF NOT EXISTS items (
                                        id INTEGER,
                                        name text NOT NULL,
                                        is_in_stock text,
                                        url text,
                                        image text,
                                        price text,
                                        last_checked text,
                                        last_in_stock text
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_items_table)


    else:
        print("Error! cannot create the database connection.")


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table created")
    except Error as e:
        print(e)


define_table()