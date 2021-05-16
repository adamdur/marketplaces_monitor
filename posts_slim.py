import datetime
from datetime import date
import os
import sys
from helpers import db as db_helper

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def main():

    db = db_helper.mysql_get_mydb()
    cursor = db.cursor()
    today = date.today()

    delete_query = (
        "DELETE FROM posts_slim "
        "WHERE date = %s"
    )
    cursor.execute(delete_query, (today,))

    query = (
        "SELECT bot, type, AVG(price) avg_price, COUNT(id) posts_count, COUNT(DISTINCT user_id) users_count, is_lifetime lifetime, DATE(created_at) date "
        "FROM posts "
        "WHERE bot != '0' "
        # "AND created_at > '2021-04-15 00:00:00' "  # START
        # "AND created_at < '2021-05-16 00:00:00' "  # END
        "AND DATE(created_at) = %s "  # END
        "GROUP BY bot, type, is_lifetime, date "
        "ORDER BY date DESC"
    )

    cursor.execute(query, (today,))
    data = cursor.fetchall()

    insert_query = (
        "INSERT INTO posts_slim (bot, type, avg_price, posts_count, users_count, lifetime, date) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE "
        "timestamp = NOW()"
    )
    cursor.executemany(insert_query, data)
    db.commit()
    db.close()
    return


if __name__ == "__main__":
    main()
