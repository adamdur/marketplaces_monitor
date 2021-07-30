import redis


def get_bot_avg_price(key):
    r = redis.StrictRedis('localhost', decode_responses=True)
    return r.hget('bots_avg_price', key)


def get_bot_sales_price(key):
    r = redis.StrictRedis('localhost', decode_responses=True)
    return r.hget('bots_sales_price', key)


def get_verified_guilds():
    r = redis.StrictRedis('localhost', decode_responses=True)
    return r.lrange('verified_guilds', 0, -1)

def get_spammers():
    r = redis.StrictRedis('localhost', decode_responses=True)
    return r.lrange('spammers', 0, -1)


