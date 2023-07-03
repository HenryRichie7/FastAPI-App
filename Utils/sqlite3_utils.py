import sqlite3
def get_creds(username,password):
    CONNECTION = "creds.db"
    connection = sqlite3.connect(CONNECTION)

    cursor = connection.cursor()
    result = cursor.execute(f"SELECT * FROM creds WHERE username = '{username}' and password = '{password}'")
    result = [x for x in result]

    if result:
        return True
    else:
        return False