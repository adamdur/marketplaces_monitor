import datetime
import redis

from helpers import db as db_helper


def main():
    db = db_helper.mysql_get_mydb()
    get_bots_average_price(db)


def get_bots_average_price(db):
    cursor = db.cursor(dictionary=True)
    query = "SELECT bot, GROUP_CONCAT(price ORDER BY date DESC LIMIT 5) price_list, IF(renewal NOT IN ('renewal', 'lifetime'), 'renewal', renewal) as renewalx " \
            "FROM sales " \
            "WHERE price != 0 " \
            "GROUP BY bot, renewalx " \
            "ORDER BY bot ASC, date DESC"

    cursor.execute(query)
    data = cursor.fetchall()

    r = redis.StrictRedis('localhost', decode_responses=True)
    for row in data:
        string = row['price_list']
        lst = string.split(',')
        map_obj = map(int, lst)

        prices = list(map_obj)
        avg = sum(prices) / len(prices)

        r.hset(
            "bots_sales_price",
            f"{row['bot']}__{row['renewalx']}",
            round(avg)
        )
    db.commit()
    db.close()

    return True


if __name__ == "__main__":
    main()
