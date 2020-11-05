import settings
import mysql.connector as mysql


def mysql_get_mydb():
    try:
        cnx = mysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_DATABASE,
            user=settings.DB_USER,
            password=settings.DB_PW
        )
    except mysql.Error as err:
        if err.errno == mysql.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == mysql.errorcode.ER_BAD_DV_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return cnx


def insert_post(db, data):
    cursor = db.cursor()
    insert_query = ("INSERT INTO posts (bot, type, price, marketplace, created_at, content, is_lifetime) VALUES (%s, %s, %s, %s, %s, %s, %s)")

    cursor.execute(insert_query, data)
    post = cursor.lastrowid

    db.commit()
    db.close()
    return post
