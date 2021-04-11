import redis


def get_bot_avg_price(key):
    r = redis.StrictRedis('localhost', decode_responses=True)
    return r.hget('bots_avg_price', key)


def get_verified_guilds():
    r = redis.StrictRedis('localhost', decode_responses=True)
    return r.lrange('verified_guilds', 0, -1)


