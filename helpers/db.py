import settings
import mysql.connector as mysql
import datetime


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
    insert_query = (
        "INSERT INTO posts (bot, type, price, marketplace, created_at, content, is_lifetime, user, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

    cursor.execute(insert_query, data)
    post = cursor.lastrowid

    db.commit()
    db.close()
    return post


def log_command(db, data):
    cursor = db.cursor()
    insert_query = (
        "INSERT INTO logs_usage (command, params, server_name, server_id, user_name, user_id, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    cursor.execute(insert_query, data)
    log = cursor.lastrowid

    db.commit()
    db.close()
    return log


def get_activity_from(db, bot, type, days):
    cursor = db.cursor(dictionary=True)
    end_query = ("SELECT AVG(price) AS average, COUNT(*) AS count, is_lifetime FROM posts "
                 "WHERE bot = %s "
                 "AND type = %s "
                 "AND created_at > %s "
                 "AND created_at < %s"
                 "GROUP BY is_lifetime")
    last_day_query = ("SELECT AVG(price) AS average, COUNT(*) AS count, is_lifetime FROM posts "
                      "WHERE bot = %s "
                      "AND type = %s "
                      "AND created_at > %s "
                      "AND created_at < %s"
                      "GROUP BY is_lifetime")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)
    end = last_day - datetime.timedelta(days=int(days))

    cursor.execute(end_query, (bot, type, end, last_day))
    end_data = cursor.fetchall()
    cursor.execute(last_day_query, (bot, type, last_day, now))
    last_day_data = cursor.fetchall()

    db.commit()
    db.close()

    full_data = {
        'renewal': {},
        'lifetime': {}
    }
    for data in end_data:
        if data['is_lifetime'] == 0:
            full_data['renewal']['end_day'] = data['average']
            full_data['renewal']['end_day_count'] = data['count']
        elif data['is_lifetime'] == 1:
            full_data['lifetime']['end_day'] = data['average']
            full_data['lifetime']['end_day_count'] = data['count']
    for data in last_day_data:
        if data['is_lifetime'] == 0:
            full_data['renewal']['last_day'] = data['average']
            full_data['renewal']['last_day_count'] = data['count']
        elif data['is_lifetime'] == 1:
            full_data['lifetime']['last_day'] = data['average']
            full_data['lifetime']['last_day_count'] = data['count']
    return full_data


def get_activity_stats(db, renewal, type, days):
    cursor = db.cursor(dictionary=True)
    end_query = ("SELECT bot, AVG(price) AS average, COUNT(*) AS count FROM posts "
                 "WHERE is_lifetime = %s "
                 "AND type = %s "
                 "AND created_at > %s "
                 "AND created_at < %s "
                 "GROUP BY bot "
                 "ORDER BY average DESC ")
    last_day_query = ("SELECT bot, AVG(price) AS average, COUNT(*) AS count FROM posts "
                      "WHERE is_lifetime = %s "
                      "AND type = %s "
                      "AND created_at > %s "
                      "AND created_at < %s "
                      "GROUP BY bot "
                      "ORDER BY average DESC ")
    average_count = ("SELECT COUNT(bot) / COUNT(DISTINCT(bot)) AS average_count FROM posts "
                     "WHERE is_lifetime = %s "
                     "AND type = %s "
                     "AND created_at > %s "
                     "AND created_at < %s ")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)
    end = last_day - datetime.timedelta(days=int(days))

    cursor.execute(end_query, (renewal, type, end, last_day))
    end_data = cursor.fetchall()
    cursor.execute(last_day_query, (renewal, type, last_day, now))
    last_day_data = cursor.fetchall()
    cursor.execute(average_count, (renewal, type, last_day, now))
    average_count_data = cursor.fetchone()

    stats = []
    for today in last_day_data:
        if today['bot'] and today['count'] > (float(average_count_data['average_count']) * 0.5):
            period = next((period for period in end_data if period['bot'] == today['bot']), None)
            if period:
                percentage = (today['average'] - period['average']) / period['average'] * 100
                percentage_count = (today['count'] - period['count'] / int(days)) / period['count'] / int(days) * 100
                stats.append(
                    {'bot': today['bot'], 'average_price': today['average'], 'average_price_percentage': percentage,
                     'count': today['count'], 'count_percentage': percentage_count})

    price_list = sorted(stats, key=lambda k: k['average_price_percentage'], reverse=True)
    count_list = sorted(stats, key=lambda k: k['count_percentage'], reverse=True)
    db.commit()
    db.close()

    return {
        'price_list': price_list,
        'count_list': count_list
    }


def get_posts_stats(db, type, days):
    cursor = db.cursor(dictionary=True)
    query = ("SELECT bot, COUNT(*) AS count, COUNT(DISTINCT user) unique_users "
             "FROM posts "
             "WHERE bot != '0' "
             "AND type = %s "
             "AND created_at > %s "
             "AND created_at < %s "
             "GROUP BY bot "
             "ORDER BY count DESC ")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=int(days))

    cursor.execute(query, (type, last_day, now))
    data = cursor.fetchall()
    db.commit()
    db.close()

    return data


def get_pricing(db, type, days, renewal):
    cursor = db.cursor(dictionary=True)
    query = ("SELECT bot, AVG(price) AS price FROM posts "
             "WHERE bot != '0' "
             "AND type = %s "
             "AND created_at > %s "
             "AND created_at < %s "
             "AND is_lifetime = %s "
             "GROUP BY bot "
             "ORDER BY price DESC ")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=int(days))

    cursor.execute(query, (type, last_day, now, renewal))
    data = cursor.fetchall()
    db.commit()
    db.close()

    return data


def get_average_price_by_bot(db, bot, type, renewal):
    cursor = db.cursor(dictionary=True)
    query = ("SELECT AVG(price) AS price FROM posts "
             "WHERE bot = %s "
             "AND type = %s "
             "AND is_lifetime = %s "
             "AND created_at > %s "
             "AND created_at < %s "
             "LIMIT 1")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)

    cursor.execute(query, (bot, type, renewal, last_day, now))
    data = cursor.fetchone()
    db.commit()
    db.close()

    return data['price']


def get_pricing_stats(db, days, renewal):
    cursor = db.cursor(dictionary=True)
    query = ("SELECT bot, type, AVG(price) AS price FROM posts "
             "WHERE bot != '0' "
             "AND type IN ('wts', 'wtb') "
             "AND is_lifetime = %s "
             "AND created_at > %s "
             "AND created_at < %s "
             "GROUP BY bot, type "
             "HAVING price > 0 "
             "ORDER BY bot")
    query2 = ("SELECT bot, type, AVG(price) AS price FROM posts "
              "WHERE bot != '0' "
              "AND type IN ('wts', 'wtb') "
              "AND is_lifetime = %s "
              "AND created_at > %s "
              "AND created_at < %s "
              "GROUP BY bot, type "
              "HAVING price > 0 "
              "ORDER BY bot")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=int(1))
    end_day = last_day - datetime.timedelta(days=int(days))

    cursor.execute(query, (renewal, last_day, now))
    data = cursor.fetchall()
    cursor.execute(query2, (renewal, end_day, last_day))
    data_past = cursor.fetchall()
    db.commit()
    db.close()

    full_data = {}
    for row in data:
        if row['bot'] != '0':
            if row['bot'] in full_data:
                full_data[row['bot']].update({row['type']: row['price']})
            else:
                full_data[row['bot']] = {row['type']: row['price']}
    for row in data_past:
        if row['bot'] != '0':
            if row['bot'] in full_data:
                full_data[row['bot']].update({row['type'] + "_past": row['price']})

    return full_data


def get_graph_data_pricing(db, bot, renewal):
    cursor = db.cursor(dictionary=True)
    query_graph = ("SELECT type, AVG(price) AS price, DATE(created_at) AS date FROM posts "
                   "WHERE bot = %s "
                   "AND type IN ('wts', 'wtb') "
                   "AND is_lifetime = %s "
                   "AND created_at > %s "
                   "AND created_at < %s "
                   "GROUP BY type, date "
                   "HAVING price > 0 "
                   "ORDER BY date ASC")
    query = ("SELECT type, AVG(price) AS price FROM posts "
             "WHERE bot = %s "
             "AND type IN ('wts', 'wtb') "
             "AND is_lifetime = %s "
             "AND created_at > %s "
             "AND created_at < %s "
             "GROUP BY type "
             "HAVING price > 0 ")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=int(1))
    start = now - datetime.timedelta(days=int(settings.GRAPH_DATA_DAYS))

    graph_start = start.replace(hour=00, minute=00, second=00)
    graph_end = last_day.replace(hour=23, minute=59, second=59)

    cursor.execute(query_graph, (bot, renewal, graph_start, graph_end))
    data_graph = cursor.fetchall()
    cursor.execute(query, (bot, renewal, last_day, now))
    data_day = cursor.fetchall()
    db.commit()
    db.close()

    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(settings.GRAPH_DATA_DAYS)]
    date_list.reverse()

    xlabels = []
    wts = []
    wts_day = None
    wtb = []
    wtb_day = None
    for date in date_list:
        wts_value = None
        wtb_value = None
        for row in data_graph:
            if row['date'] == date.date():
                if row['type'] == 'wts':
                    wts_value = round(row['price'])
                elif row['type'] == 'wtb':
                    wtb_value = round(row['price'])
        wts.append(wts_value)
        wtb.append(wtb_value)
        xlabels.append(date.strftime("%Y/%m/%d"))

    for row in data_day:
        if row['type'] == 'wts':
            wts_day = row['price']
        elif row['type'] == 'wtb':
            wtb_day = row['price']

    return {
        'xlabels': xlabels,
        'wts': wts,
        'wtb': wtb,
        'wts_day': wts_day,
        'wtb_day': wtb_day
    }


def get_graph_data_demand(db, bot, renewal):
    cursor = db.cursor(dictionary=True)
    query_graph = ("SELECT type, COUNT(*) AS count, DATE(created_at) AS date FROM posts "
                   "WHERE bot = %s "
                   "AND type IN ('wts', 'wtb') "
                   "AND is_lifetime = %s "
                   "AND created_at > %s "
                   "AND created_at < %s "
                   "GROUP BY type, date "
                   "HAVING count > 0 "
                   "ORDER BY date ASC")
    query = ("SELECT type, COUNT(*) AS count FROM posts "
             "WHERE bot = %s "
             "AND type IN ('wts', 'wtb') "
             "AND is_lifetime = %s "
             "AND created_at > %s "
             "AND created_at < %s "
             "GROUP BY type "
             "HAVING count > 0 ")
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=int(1))
    start = now - datetime.timedelta(days=int(settings.GRAPH_DATA_DAYS))

    graph_start = start.replace(hour=00, minute=00, second=00)
    graph_end = last_day.replace(hour=23, minute=59, second=59)

    cursor.execute(query_graph, (bot, renewal, graph_start, graph_end))
    data_graph = cursor.fetchall()
    cursor.execute(query, (bot, renewal, last_day, now))
    data_day = cursor.fetchall()
    db.commit()
    db.close()

    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(settings.GRAPH_DATA_DAYS)]
    date_list.reverse()

    xlabels = []
    wts = []
    wts_day = None
    wtb = []
    wtb_day = None
    for date in date_list:
        wts_value = None
        wtb_value = None
        for row in data_graph:
            if row['date'] == date.date():
                if row['type'] == 'wts':
                    wts_value = round(row['count'])
                elif row['type'] == 'wtb':
                    wtb_value = round(row['count'])
        wts.append(wts_value)
        wtb.append(wtb_value)
        xlabels.append(date.strftime("%Y/%m/%d"))

    for row in data_day:
        if row['type'] == 'wts':
            wts_day = row['count']
        elif row['type'] == 'wtb':
            wtb_day = row['count']

    return {
        'xlabels': xlabels,
        'wts': wts,
        'wtb': wtb,
        'wts_day': wts_day,
        'wtb_day': wtb_day
    }
