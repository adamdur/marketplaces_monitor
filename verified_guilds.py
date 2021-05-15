import datetime
import redis

from helpers import db as db_helper


def main():
    db = db_helper.mysql_get_mydb()
    get_verified_guilds(db)


def get_verified_guilds(db):
    cursor = db.cursor()
    query = "SELECT server FROM licenses WHERE active = 1"

    cursor.execute(query)
    data = cursor.fetchall()

    db.commit()
    db.close()

    guilds = list(map(lambda x: x[0], data))
    r = redis.StrictRedis('localhost', decode_responses=True)
    r.delete('verified_guilds')
    r.lpush('verified_guilds', *guilds)

    return True


if __name__ == "__main__":
    main()
