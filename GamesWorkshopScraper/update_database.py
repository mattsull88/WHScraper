import sqlite3
from sqlite3 import Error
from datetime import date


def update_database(data, database, item_avail_key, item_name_key, item_url_key):
    today = date.today()
    today = today.strftime("%d/%m/%Y")

    instock_items = []
    not_instock_items = []
    new_instock_items = []
    new_not_instock_items = []
    old_items = []
    items_to_message = []

    # Seperate items to instock and out of stock
    for item in data:
        if item[item_avail_key] == 'inStock':
            instock_items.append(item)
        else:
            not_instock_items.append(item)

    conn = create_connection("sqlite/db/" + database)
    with conn:
        table = select_all_items(conn)


    # Finds new items that do not already exist in database
    for instock_item in instock_items:
        found = False
        for item in table:
            if not found:
                if instock_item[item_name_key] in item[1]:
                    old_items.append(instock_item)
                    found = True
        if not found:
            new_instock_items.append(instock_item)
            print("New instock item found")
            print(instock_item[item_name_key])

    for not_instock_item in not_instock_items:
        found = False
        for item in table:
            if not found:
                if not_instock_item[item_name_key] in item[1]:
                    old_items.append(not_instock_item)
                    found = True
        if not found:
            new_not_instock_items.append(not_instock_item)
            print("New not instock item found")
            print(not_instock_item)

    num_of_ids = len(table)
    print("Updating database")
    with conn:
        # Adds new items that are not in stock
        for new_item in new_not_instock_items:
            num_of_ids += 1
            item = (
                num_of_ids, new_item[item_name_key], "Not In Stock", new_item[item_url_key], "NA", "NA", today, "Never")
            create_item(conn, item)
            print("Not Instock item Added to table: " + new_item[item_name_key])

        # Adds new items that are in stock and adds them to the telegram message
        for new_item in new_instock_items:
            num_of_ids += 1
            item = (num_of_ids, new_item[item_name_key], "In Stock", new_item[item_url_key], "NA", "NA", today, "Never")
            create_item(conn, item)
            print("Instock item Added to table: " + new_item[item_name_key])
            items_to_message.append(new_item)

        # Checks in stock items to see if they were out of stock, adds to telegram message
        print("Checking stock changes")
        for instock_item in instock_items:
            db_item_tuple = select_item_by_name(conn, instock_item[item_name_key])
            for db_item_list in db_item_tuple:
                if db_item_list[2] == "Not In Stock":
                    item = ("In Stock", today, db_item_list[1])

                    # Confirm new instock items are actually instock by srapping the
                    # item webapge if database=database1 (GamesWorkshop)
                    if database == 'database.db':
                        true_instock_item = instock_item
                        if true_instock_item:
                            update_instock_item(conn, item)
                            print("Item now in stock: " + true_instock_item[item_name_key])
                            items_to_message.append(true_instock_item)
                        else:
                            not_instock_items.append(instock_item)
                    else:
                        update_instock_item(conn, item)
                        print("Item now in stock: " + instock_item[item_name_key])
                        items_to_message.append(instock_item)

        # Updates now out of stock items
        for not_instock_item in not_instock_items:
            db_item_tuple = select_item_by_name(conn, not_instock_item[item_name_key])
            for db_item_list in db_item_tuple:
                if db_item_list[2] == "In Stock":
                    item = ("Not In Stock", today, db_item_list[1])
                    update_instock_item(conn, item)

    # Updates all items last checked time
    print("Updating times")
    for instock_item in instock_items:
        item = (today, instock_item[item_name_key])
        update_item_time(conn, item)

    for not_instock_item in not_instock_items:
        item = (today, not_instock_item[item_name_key])
        update_item_time(conn, item)

    return items_to_message


def create_item(conn, item):
    """
    Create a new project into the projects table
    :param conn:
    :param item:
    :return: project id
    """
    sql = ''' INSERT INTO items(id,name,is_in_stock,url,image,price,last_checked,last_in_stock)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()
    return cur.lastrowid


def update_instock_item(conn, item):
    """
    :param conn:
    :param item:
    :return: project id
    """
    sql = ''' UPDATE items
              SET is_in_stock = ? ,
                  last_in_stock = ?
              WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def update_not_instock_item(conn, item):
    """
    :param conn:
    :param item:
    :return: project id
    """
    sql = ''' UPDATE items
              SET is_in_stock = ? ,
              WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def update_item_time(conn, item):
    """
    :param conn:
    :param item:
    :return: project id
    """
    sql = ''' UPDATE items
              SET last_checked = ?
              WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def select_all_items(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")

    rows = cur.fetchall()

    return rows


def select_item_by_name(conn, name):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE name =?", (name,))

    rows = cur.fetchall()

    return rows


def create_connection(db_file):
    """ create a database connection to the sqlite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn
