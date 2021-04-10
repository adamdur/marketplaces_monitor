import settings
import mysql.connector as mysql
import datetime
from decimal import Decimal

from helpers import common as common_helper


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
        "INSERT INTO posts (bot, type, price, marketplace, created_at, content, is_lifetime, user, user_id, url) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    cursor.execute(insert_query, data)
    post = cursor.lastrowid

    db.commit()
    db.close()
    return post


def insert_post_ticket(db, data):
    cursor = db.cursor()
    insert_query = (
        "INSERT INTO tickets (params, guild_id, guild_name, content, user, user_id, url, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

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


def get_trading_activity(db, bot=None, is_lifetime=0):
    cursor = db.cursor(dictionary=True)
    query_str = "SELECT COUNT(DISTINCT user_id) AS count, AVG(price) AS price, type FROM posts "
    query_str += "WHERE created_at > %s " \
                 "AND created_at < %s " \
                 "AND type IN ('wts', 'wtb') "
    query_str += f"{'AND bot = %s ' if bot else ''}"
    query_str += f"{'AND is_lifetime = %s ' if bot else ''}"
    query_str += "GROUP BY type"

    query_str2 = "SELECT COUNT(DISTINCT user_id) AS count, AVG(price) AS price, type FROM posts "
    query_str2 += "WHERE created_at > %s " \
                  "AND created_at < %s " \
                  "AND type IN ('wts', 'wtb') "
    query_str2 += f"{'AND bot = %s ' if bot else ''}"
    query_str2 += f"{'AND is_lifetime = %s ' if bot else ''}"
    query_str2 += "GROUP BY type"

    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=1)
    end = start - datetime.timedelta(days=1)

    query_args = (start, now)
    query_args2 = (end, start)
    if bot:
        query_args = query_args + (bot,) + (is_lifetime,)
        query_args2 = query_args2 + (bot,) + (is_lifetime,)
    cursor.execute(query_str, query_args)
    data_current = cursor.fetchall()
    cursor.execute(query_str2, query_args2)
    data_prev = cursor.fetchall()

    db.commit()
    db.close()

    return {
        'current': data_current,
        'prev': data_prev
    }


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
    query = ("SELECT bot, COUNT(*) AS count, COUNT(DISTINCT user_id) unique_users "
             "FROM posts "
             "WHERE bot != '0' "
             "AND type = %s "
             "AND created_at > %s "
             "AND created_at < %s "
             "GROUP BY bot "
             "ORDER BY unique_users DESC ")
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


def get_graph_sales(db, bot):
    if bot == 'mek':
        bot = 'mekpreme'
    cursor = db.cursor(dictionary=True)
    query = "SELECT AVG(price) average, renewal, date FROM sales " \
            "WHERE bot LIKE %s " \
            "AND price != 0 " \
            "AND date >= %s " \
            "AND date <= %s " \
            "GROUP BY date, renewal " \
            "HAVING average > 0 " \
            "ORDER BY date ASC"

    now = datetime.datetime.now()
    last_day = now
    start = now - datetime.timedelta(days=int(settings.GRAPH_DATA_DAYS))

    cursor.execute(query, (f"%{bot}%", start, last_day))
    data = cursor.fetchall()

    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(settings.GRAPH_DATA_DAYS)]
    date_list.reverse()

    formatted_data = {}
    xlabels = []
    for xdate in date_list:
        formatted_data[f"{xdate.strftime('%Y/%m/%d')}"] = {}
        formatted_data[f"{xdate.strftime('%Y/%m/%d')}"]['lifetime'] = []
        formatted_data[f"{xdate.strftime('%Y/%m/%d')}"]['renewal'] = []
        xlabels.append(xdate.strftime("%Y/%m/%d"))

    for row in data:
        if 'lifetime' in row['renewal']:
            row_renewal = 'lifetime'
        else:
            row_renewal = 'renewal'
        try:
            formatted_data[row['date'].strftime("%Y/%m/%d")][row_renewal].append(row['average'])
        except:
            formatted_data[row['date'].strftime("%Y/%m/%d")][row_renewal] = []
            formatted_data[row['date'].strftime("%Y/%m/%d")][row_renewal].append(row['average'])

    final_data = {}
    for key, value in formatted_data.items():
        for ren, price in value.items():
            count = len(price)
            avg_price = sum(price) / count if count > 0 else None
            try:
                final_data[ren].append(avg_price)
            except KeyError:
                final_data[ren] = []
                final_data[ren].append(avg_price)

    db.commit()
    db.close()
    return {
        'xlabels': xlabels,
        'data': final_data
    }


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
    query_graph = ("SELECT type, COUNT(*) AS count, COUNT(DISTINCT user) count_users, DATE(created_at) AS date FROM posts "
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
    wts_users = []
    wts_day = None
    wtb = []
    wtb_users = []
    wtb_day = None
    for date in date_list:
        wts_value = None
        wts_value_users = None
        wtb_value = None
        wtb_value_users = None
        for row in data_graph:
            if row['date'] == date.date():
                if row['type'] == 'wts':
                    wts_value = round(row['count'])
                    wts_value_users = round(row['count_users'])
                elif row['type'] == 'wtb':
                    wtb_value = round(row['count'])
                    wtb_value_users = round(row['count_users'])
        wts.append(wts_value)
        wts_users.append(wts_value_users)
        wtb.append(wtb_value)
        wtb_users.append(wtb_value_users)
        xlabels.append(date.strftime("%Y/%m/%d"))

    for row in data_day:
        if row['type'] == 'wts':
            wts_day = row['count']
        elif row['type'] == 'wtb':
            wtb_day = row['count']

    return {
        'xlabels': xlabels,
        'wts': wts,
        'wts_users': wts_users,
        'wtb': wtb,
        'wtb_users': wtb_users,
        'wts_day': wts_day,
        'wtb_day': wtb_day
    }


def log_event(db, dict):
    cursor = db.cursor()
    insert_query = (
        "INSERT INTO events (type, date, bot, description, logged_by) "
        "VALUES (%s, %s, %s, %s, %s)")

    try:
        data = (
            dict['event'],
            dict['date'],
            dict['bot'],
            dict['description'],
            dict['logged_by']
        )
    except IndexError:
        return False

    cursor.execute(insert_query, data)
    log = cursor.lastrowid

    db.commit()
    db.close()
    return log


def get_event_logs(db, date):
    cursor = db.cursor(dictionary=True)
    query = (
        "SELECT type, bot, description, logged_by, date FROM events "
        "WHERE date = %s "
        "ORDER BY type"
    )

    cursor.execute(query, (date,))
    data = cursor.fetchall()

    db.commit()
    db.close()
    return data


def get_gainers(db, timeframe, type, renewal):
    cursor = db.cursor(dictionary=True)
    query_str = "SELECT COUNT(DISTINCT user_id) AS count, AVG(price) AS price, type, bot FROM posts "
    query_str += "WHERE created_at > %s " \
                 "AND created_at < %s " \
                 "AND type IN ('wts', 'wtb') " \
                 "AND bot != '0' "
    query_str += "AND is_lifetime = %s "
    query_str += "GROUP BY bot, type"

    query_str2 = "SELECT COUNT(DISTINCT user_id) AS count, AVG(price) AS price, type, bot FROM posts "
    query_str2 += "WHERE created_at > %s " \
                  "AND created_at < %s " \
                  "AND type IN ('wts', 'wtb') " \
                  "AND bot != '0' "
    query_str2 += "AND is_lifetime = %s "
    query_str2 += "GROUP BY bot, type"

    query_str3 = "SELECT COUNT(DISTINCT user_id) AS count, AVG(price) AS price, type, bot, DATE(created_at) date FROM posts "
    query_str3 += "WHERE created_at > %s " \
                  "AND created_at < %s " \
                  "AND type IN ('wts', 'wtb') " \
                  "AND bot != '0' "
    query_str3 += "AND is_lifetime = %s "
    query_str3 += "GROUP BY bot, type, date"

    timeframe_days = common_helper.get_timeframe_days(timeframe)

    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=1)
    end = start - datetime.timedelta(days=timeframe_days)

    query_args = (start, now, renewal)
    query_args2 = (end, start, renewal)

    cursor.execute(query_str, query_args)
    data_current = cursor.fetchall()
    cursor.execute(query_str2, query_args2)
    data_prev = cursor.fetchall()

    if timeframe_days > 1:
        cursor.execute(query_str3, query_args2)
        data_prev_new = cursor.fetchall()
        new_data_prev = {}
        for new_prev in data_prev_new:
            try:
                new_data_prev[f"{new_prev['bot']}_{new_prev['type']}"] = new_data_prev[f"{new_prev['bot']}_{new_prev['type']}"] + new_prev['count']
            except KeyError:
                new_data_prev[f"{new_prev['bot']}_{new_prev['type']}"] = new_prev['count']
        i = 0
        for prev in data_prev:
            data_prev[i]['count'] = round(new_data_prev[f"{prev['bot']}_{prev['type']}"] / timeframe_days)
            i += 1
    db.commit()
    db.close()

    return {
        'current': data_current,
        'prev': data_prev
    }


def get_info_bots(db, bot):
    cursor = db.cursor(dictionary=True)
    query = "SELECT bot, message_id, channel_id FROM bot_info"
    if bot:
        query += " WHERE bot = %s"
    query += " ORDER BY bot"
    if bot:
        cursor.execute(query, (bot,))
    else:
        cursor.execute(query)
    if bot:
        data = cursor.fetchone()
    else:
        data = cursor.fetchall()

    db.commit()
    db.close()
    return data


def add_info(db, bot, message_id, channel_id=False):
    if not bot or not message_id:
        return False
    if not channel_id:
        channel_id = settings.MACHETE_SERVER_GUIDES_CHANNEL
    cursor = db.cursor()
    insert_query = (
        "INSERT INTO bot_info (bot, message_id, channel_id) "
        "VALUES (%s, %s, %s)")

    cursor.execute(insert_query, (bot, message_id, channel_id))
    info = cursor.lastrowid

    db.commit()
    db.close()
    return info


def create_ticket_monitor(db, marketplace, guild_id, channel_id):
    cursor = db.cursor(dictionary=True)
    query = "SELECT id FROM ticket_monitors " \
            "WHERE marketplace = %s " \
            "AND guild_id = %s " \
            "AND channel_id = %s "
    cursor.execute(query, (marketplace, guild_id, channel_id))
    exists = cursor.fetchone()

    if exists:
        return False

    insert_query = (
        "INSERT INTO ticket_monitors (marketplace, guild_id, channel_id) "
        "VALUES (%s, %s, %s)")
    cursor.execute(insert_query, (marketplace, guild_id, channel_id))
    inserted = cursor.lastrowid

    db.commit()
    db.close()
    return inserted


def get_ticket_monitors(db, marketplace):
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM ticket_monitors " \
            "WHERE marketplace = %s "
    cursor.execute(query, (marketplace,))
    data = cursor.fetchall()

    db.commit()
    db.close()
    return data


def destroy_ticket_monitor(db, guild_id, channel_id):
    cursor = db.cursor(dictionary=True)
    query = "SELECT id FROM ticket_monitors " \
            "WHERE guild_id = %s " \
            "AND channel_id = %s "
    cursor.execute(query, (guild_id, channel_id))
    monitors = cursor.fetchall()

    if not monitors:
        return False

    ids = []
    for monitor in monitors:
        ids.append(str(monitor['id']))

    query_string = f"DELETE FROM ticket_monitors WHERE id IN ({','.join(['%s'] * (len(ids)))})"
    cursor.execute(query_string, ids)

    deleted = cursor.rowcount

    db.commit()
    db.close()
    return deleted


def get_sotm_commands(db):
    cursor = db.cursor(dictionary=True)
    query = "SELECT bot, commands, botbroker, renewal FROM market_state "
    cursor.execute(query)
    commands = cursor.fetchall()
    db.commit()
    db.close()
    return commands


def get_sotm_bots(db):
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM market_state " \
            "WHERE active = 1 "
    cursor.execute(query)
    commands = cursor.fetchall()
    db.commit()
    db.close()
    return commands


def get_sotm_bot_sales(db, bot, renewal, date):
    prev_date = date - datetime.timedelta(days=1)
    cursor = db.cursor(dictionary=True)
    query = "SELECT AVG(price) average FROM sales " \
            "WHERE bot LIKE %s " \
            "AND price != 0 " \
            "AND renewal IN (" + ','.join(f"'{ren}'" for ren in renewal.split(',')) + ") " \
            "AND date = %s"

    cursor.execute(query, (f"%{bot}%", date))
    current = cursor.fetchall()

    cursor.execute(query, (f"%{bot}%", prev_date))
    prev = cursor.fetchall()

    if not prev[0]['average']:
        new_query = "SELECT AVG(price) average FROM sales " \
                    "WHERE bot LIKE %s " \
                    "AND price != 0 " \
                    "AND renewal IN (" + ','.join(f"'{ren}'" for ren in renewal.split(',')) + ") " \
                    "AND date < %s " \
                    "GROUP BY date " \
                    "HAVING AVG(price) > 0 " \
                    "ORDER BY date DESC " \
                    "LIMIT 1"
        cursor.execute(new_query, (f"%{bot}%", date))
        prev = cursor.fetchall()

    db.commit()
    db.close()
    return {
        'current': current[0]['average'] if current[0]['average'] else 0,
        'prev': prev[0]['average'] if prev[0]['average'] else 0
    }


def get_sotm_demand(db, bot, renewal):
    if 'lifetime' in renewal:
        renewal = '1'
    else:
        renewal = '0'
    if bot == 'mekpreme':
        bot = 'mek'
    elif bot == 'splashforce':
        bot = 'sf'
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)
    cursor = db.cursor(dictionary=True)
    query = ("SELECT COUNT(DISTINCT user_id) unique_users "
             "FROM posts "
             "WHERE bot = %s "
             "AND is_lifetime = %s "
             "AND type = 'wtb' "
             "AND created_at > %s "
             "AND created_at < %s ")
    cursor.execute(query, (bot, renewal, last_day, now))
    data = cursor.fetchall()
    db.commit()
    db.close()
    return data[0]['unique_users']


def log_sale(db, data):
    date = datetime.date.today()
    for log in data:
        if log['bot'] == 'projectdestroyer':
            log['bot'] = 'pd'
        if log['bot'] == 'cybersole':
            log['bot'] = 'cyber'
        cursor = db.cursor(dictionary=True)
        query = "INSERT INTO sales (server, bot, renewal, price, date) " \
                "VALUES (%s, %s, %s, %s, %s)"
        renewal = renewal_helper(log['renewal'])
        price = '0' if log['price'] == 'n/a' else log['price']
        cursor.execute(query, (log['server'], log['bot'], renewal, Decimal(price.replace(',', '.')), date))

    db.commit()
    db.close()
    return True


def insert_channel(db, data):
    cursor = db.cursor(dictionary=True)
    get_query = "SELECT id FROM channels " \
                "WHERE bot = %s " \
                "AND type = %s " \
                "AND guild_id = %s"
    cursor.execute(get_query, (data['bot'], data['type'], data['guild_id']))
    existing_channel = cursor.fetchone()
    if existing_channel:
        query = "UPDATE channels " \
                "SET guild_name= %s, guild_icon = %s, url= %s " \
                "WHERE id = %s"
        cursor.execute(query, (data['guild_name'], data['guild_icon'], data['url'], existing_channel['id']))
    else:
        query = "INSERT INTO channels (bot, type, guild_id, guild_name, guild_icon, channel_name, url) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (data['bot'], data['type'], data['guild_id'], data['guild_name'], data['guild_icon'], data['channel_name'], data['url']))

    db.commit()
    db.close()
    return True


def get_channels(db, bot, type=False):
    cursor = db.cursor(dictionary=True)
    get_query = "SELECT * FROM channels " \
                "WHERE bot = %s "
    if type:
        get_query += "AND type = %s "

    get_query += "GROUP BY type, guild_id"

    if type:
        cursor.execute(get_query, (bot, type))
    else:
        cursor.execute(get_query, (bot,))
    data = cursor.fetchall()

    db.commit()
    db.close()
    return data


def renewal_helper(renewal):
    if renewal in ['renewal', 'lifetime', 'monthly']:
        return renewal
    elif renewal.startswith('renewal '):
        return renewal.replace('renewal ', '')
    elif 'for' in renewal:
        return renewal.split('for')[0].replace('$', '').replace('€', '').replace('£', '').strip()
    elif '/' in renewal:
        return renewal.split('/')[0].replace('$', '').replace('€', '').replace('£', '').strip()
    else:
        return renewal


def get_verified_guilds(db):
    cursor = db.cursor()
    query = "SELECT server FROM licenses WHERE active = 1"

    cursor.execute(query)
    data = cursor.fetchall()

    db.commit()
    db.close()
    return list(map(lambda x: x[0], data))


def get_licenses(db, active=False):
    cursor = db.cursor()
    query = "SELECT * FROM licenses WHERE active = %s"

    cursor.execute(query, active)
    data = cursor.fetchall()

    db.commit()
    db.close()
    return data


def get_license(db, license_key):
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM licenses WHERE license = %s"

    cursor.execute(query, (license_key,))
    data = cursor.fetchone()

    db.commit()
    db.close()
    return data


def insert_license(db, data):
    cursor = db.cursor(dictionary=True)
    insert_query = (
        "INSERT INTO licenses (license, server, user_name, user_id, active, created_at, updated_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    now = datetime.datetime.now()
    data.extend([now, now])
    cursor.execute(insert_query, data)
    post = cursor.lastrowid

    db.commit()
    db.close()
    return post
