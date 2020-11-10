from price_parser import Price
import re
import settings
import math

from currency_converter import CurrencyConverter


def get_formatted_price(message):
    regexp1 = '(usd|eur|gbp|€|\$|£)(\d{1,}(?:[.,]\d{3})*(?:[.,]\d{2}))*(\d{1,4}(?:[.,]\d{3})*(?:[.,]\d{2})*(?:[.,]\d{1})*([k])?)(?:( /|/|m| m|ren| ren)?)|(\d{1,4}(?:[.,]\d{3})*(?:[.,]\d{2})*(?:[.,]\d{1})?)(usd|eur|gbp|k usd|k eur|k gbp|kusd|keur|kgbp|€|\$|£|k€|k\$|k£|k €|k \$|k £|k| k)(?:[/]?)(?:( /|/|m| m|ren| ren)?)'
    regexp2 = '(USD|EUR|€|\$|£)(\d{1,}(?:[.,]\d{3})*(?:[.,]\d{2}))*(\d{1,4}(?:[.,]\d{3})*(?:[.,]\d{2})*(?:[.,]\d{1})*([k])?)|(\d{1,4}(?:[.,]\d{3})*(?:[.,]\d{2})*(?:[.,]\d{1})?)\s?(USD|EUR|GBP|k USD|k EUR|k GBP|kUSD|kEUR|kGBP|€|\$|£|k€|k\$|k£|k €|k \$|k £|k| k|K| K|eur|euro|EURO)'

    message_content = message.content.lower()
    first_try = re.finditer(regexp1, message_content)
    match = ''
    level = 0
    if first_try:
        for ftry in first_try:
            if not any(s in ftry.group() for s in [' /', '/', 'm', ' m', 'ren', ' ren']):
                match = ftry.group()
                level = 1
                break
    if not match:
        second_try = re.search(regexp2, message_content)
        if second_try:
            match = second_try.group(0)
            level = 2
        if not second_try:
            third_try = Price.fromstring(message_content)
            if third_try:
                if third_try.amount and third_try.amount > 9:
                    if third_try.amount > 99999:
                        return False
                    if third_try.currency == 'DM':
                        third_try.currency = '$'
                    match = str(third_try.amount) + (third_try.currency if third_try.currency else '$')
                    level = 3
    return {"price": match, "level": level} if match else False


def format_decimal_price(price, delimeter):
    partials = price.split(delimeter)
    if len(partials) == 1:
        price += "000"
    if len(partials) > 1:
        num_length = len(partials[1])
        if num_length == 1:
            price += "00"
        elif num_length == 2:
            price += "0"
    final = price.replace(delimeter, '')
    return final


def get_db_price(price):
    currencies = ['€', '$', '£', 'eur', 'euro', 'usd', 'dollar', 'gbp']
    if ',' in price:
        price = price.replace(',', '.')

    numeric_value = re.search('\d*\.?\d+', price.replace(' ', '')).group()
    if not numeric_value:
        print('NO NUMERIC VALUE')
        return False

    if '.' in numeric_value:
        final_value = format_decimal_price(numeric_value, '.')
    elif ',' in numeric_value:
        final_value = format_decimal_price(numeric_value, ',')
    elif 'k' in price.lower():
        final_value = numeric_value + "000"
    else:
        final_value = numeric_value.replace(' ', '')

    matched_currency = ""
    for curr in currencies:
        if curr in price.lower():
            matched_currency = curr
    if not matched_currency:
        matched_currency = "$"

    converter = CurrencyConverter()
    if any(c in matched_currency.lower() for c in ['€', 'eur', 'euro']):
        final_value = converter.convert(float(final_value), 'EUR', 'USD')
    if any(c in matched_currency.lower() for c in ['£', 'gbp', 'euro']):
        final_value = converter.convert(float(final_value), 'GBP', 'USD')

    if float(final_value) > settings.PRICE_CAP:
        return False

    return math.ceil(float(final_value))


def price_level(level):
    switcher = {
        0: '',
        1: '(lvl 1.)',
        2: '(lvl 2.)',
    }
    return switcher.get(level, "Invalid level")


def get_channel_types(channel_name, message_content):
    types = []
    if any(s in channel_name for s in ['wtro', 'wtr', 'rental', 'rent', 'rental-sell']):
        if 'wtr ' in message_content.lower():
            types.append('wtr')
        if 'wtro' in message_content.lower():
            types.append('wtro')
        if not any(c in message_content.lower() for c in ['wtr ', 'wtro']):
            types.append('wtro')
    if not types:
        if any(w in channel_name for w in ['wts', 'sell']):
            types.append('wts')
        if any(a in channel_name for a in ['wtb', 'buy', 'wtt', 'trade']):
            if 'wtt' in message_content.lower():
                types.append('wtt')
            if 'wtb' in message_content.lower():
                types.append('wtb')
            if not any(n in message_content.lower() for n in ['wtt', 'wtb']):
                types.append('wtb')
        if not types:
            return []

    return types


def get_bot_from_channel(channel_name):
    final_bot = ''
    for bot in settings.ALLOWED_BOTS:
        aliases = settings.ALLOWED_BOTS[bot]
        if any(alias in channel_name for alias in aliases):
            final_bot = bot
            break
    if not final_bot:
        return False
    return final_bot
