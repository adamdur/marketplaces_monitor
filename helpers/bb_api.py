import requests
import requests_async
import settings


def api_call(endpoint, params, headers=None):
    if headers is None:
        headers = {}
    headers['x-api-key'] = settings.BB_SECRET
    url = settings.BB_BASE_API_URL + "/" + endpoint

    try:
        data = requests.get(url, params=params, headers=headers, timeout=settings.BB_API_TIMEOUT)
        if data.status_code == 200:
            return data
        else:
            return None
    except Exception as e:
        print(e)


async def async_api_call(endpoint, params, headers=None, message=None):
    if headers is None:
        headers = {}
    headers['x-api-key'] = settings.BB_SECRET
    url = settings.BB_BASE_API_URL + "/" + endpoint

    try:
        data = await requests_async.get(url, params=params, headers=headers, timeout=settings.BB_API_TIMEOUT)
        return data
    except requests_async.exceptions.Timeout:
        if message:
            await message.edit(content=":exclamation: Connection timed out. Try again later...")
        return None
    except:
        if message:
            await message.edit(content=":exclamation: Something went wrong. Try again later...")
        return None


def get_bots(page=None, sort_by=None, order=None, bots=None):
    if bots is None:
        bots = {}

    params = {}
    if not page:
        page = 1
    if page:
        params['page'] = page
    if sort_by:
        params['sort_by'] = sort_by
    if order:
        params['order'] = order

    response = api_call('bots', params)
    data = response.json()
    bots[page] = data['bots']

    if data['pagination']['next'] is not None:
        page += 1
        return get_bots(page=page, bots=bots)
    else:
        bots['pagination'] = data['pagination']
        return bots


async def get_asks(bot_id, message, page=1, sort_by='price', order='asc', key_type='renewal'):
    params = {}
    if page:
        params['page'] = page
    if sort_by:
        params['sort_by'] = sort_by
    if order:
        params['order'] = order
    if key_type:
        params['key_type'] = key_type

    response = await async_api_call('asks?product_id={}'.format(bot_id), params, message=message)
    if not response:
        return {
            'data': None,
            'total_count': None
        }
    data = response.json()

    return {
        'data': data['asks'],
        'total_count': data['pagination']['total_count']
    }


async def get_lowest_ask(bot_id, key_type='renewal'):
    params = {'page': 1, 'sort_by': 'price', 'order': 'asc', 'key_type': key_type}

    response = await async_api_call('asks?product_id={}'.format(bot_id), params)
    if not response:
        return False
    data = response.json()
    try:
        return data['asks'][0]
    except:
        return False


async def get_highest_bid(bot_id, key_type='renewal'):
    params = {'page': 1, 'sort_by': 'price', 'order': 'desc', 'key_type': key_type}

    response = await async_api_call('bids?product_id={}'.format(bot_id), params)
    if not response:
        return False
    data = response.json()
    try:
        return data['asks'][0]
    except:
        return False


async def get_bids(bot_id, message, page=1, sort_by='price', order='desc', key_type='renewal'):
    params = {}
    if page:
        params['page'] = page
    if sort_by:
        params['sort_by'] = sort_by
    if order:
        params['order'] = order
    if key_type:
        params['key_type'] = key_type

    response = await async_api_call('bids?product_id={}'.format(bot_id), params, message=message)
    if not response:
        return {
            'data': None,
            'total_count': None
        }
    data = response.json()

    return {
        'data': data['asks'],
        'total_count': data['pagination']['total_count']
    }


async def get_sales(bot_id, message, page=1, sort_by='matched_at', order='desc', key_type='renewal'):
    params = {}
    if page:
        params['page'] = page
    if sort_by:
        params['sort_by'] = sort_by
    if order:
        params['order'] = order
    if key_type:
        params['key_type'] = key_type

    response = await async_api_call('sales?product_id={}'.format(bot_id), params, message=message)
    if not response:
        return {
            'data': None,
            'total_count': None
        }
    data = response.json()

    return {
        'data': data['asks'],
        'total_count': data['pagination']['total_count']
    }


async def get_bot_data(bot, renewal, message):
    asks_data = await get_asks(bot['id'], message, key_type=renewal)
    bids_data = await get_bids(bot['id'], message, key_type=renewal)
    sales_data = await get_sales(bot['id'], message, key_type=renewal)

    return {
        'asks': asks_data,
        'bids': bids_data,
        'sales': sales_data
    }
