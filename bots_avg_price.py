import datetime
import redis

from helpers import db as db_helper


def main():
    db = db_helper.mysql_get_mydb()
    get_bots_average_price(db)


def get_bots_average_price(db):
    cursor = db.cursor(dictionary=True)
    query = ("SELECT bot, type, is_lifetime, AVG(price) AS price FROM posts "
             "WHERE type IN ('wtb', 'wts') "
             "AND created_at > %s "
             "AND created_at < %s "
             "GROUP BY bot, is_lifetime, type "
             "ORDER BY bot")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)

    cursor.execute(query, (last_day, now))
    data = cursor.fetchall()

    r = redis.StrictRedis('localhost', decode_responses=True)
    for row in data:
        r.hset(
            "bots_avg_price",
            f"{row['bot']}__{row['type']}__{'lt' if row['is_lifetime'] else 'ren'}",
            int(row['price'])
        )
    db.commit()
    db.close()

    return True


if __name__ == "__main__":
    main()
