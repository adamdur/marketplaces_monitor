import sys
import settings
import discord
import datetime
import asyncio
import time

from helpers import webhook as webhook_helper
from helpers import db as db_helper

this = sys.modules[__name__]
this.running = False
this.setup_data = []
this.TEST_MODE = False


async def main(argv):
    print("Everything set up... Preparing State of the market...")
    start = time.time()
    db = db_helper.mysql_get_mydb()
    sotm_bots = db_helper.get_sotm_bots(db)

    date = datetime.date.today()
    formated_data = []
    i = 0
    for sotm_bot in sotm_bots:
        print(f"{date} - {sotm_bot['bot']}")
        db = db_helper.mysql_get_mydb()
        sales = db_helper.get_sotm_bot_sales(db, sotm_bot['bot'], sotm_bot['renewal'], date)
        db2 = db_helper.mysql_get_mydb()
        demand = db_helper.get_sotm_demand(db2, sotm_bot['bot'], sotm_bot['renewal'])

        current_price = sales['current']
        prev_price = sales['prev']
        week_price = sales['prev_week']
        if current_price == 0:
            current_price = prev_price
        movement = round((current_price - prev_price) / prev_price * 100, 1)
        movement_week = round((current_price - week_price) / week_price * 100, 1)

        bot_name = f"{sotm_bot['bot'].capitalize()}{' (' + sotm_bot['display_renewal'] + ')' if sotm_bot['display_renewal'] else ''}" \
                   f"{' ' + sotm_bot['icon'] if sotm_bot['icon'] else ''}"
        price = round(current_price)
        # 0-5, 5-20, 20-30, 30+
        demand_icon = ''
        if demand <= 10:
            demand_icon = ':red_circle:'
        elif 10 < demand <= 20:
            demand_icon = ':yellow_circle:'
        elif 20 < demand <= 35:
            demand_icon = ':green_circle:'
        elif 35 < demand:
            demand_icon = ':rocket:'
        movement_str = ''
        if movement == 0:
            movement_str = ':turtle:'
        elif movement > 0:
            movement_str = f":chart_with_upwards_trend: +{movement}%"
        elif movement < 0:
            movement_str = f":chart_with_downwards_trend: {movement}%"

        movement_str_week = ''
        if movement_week == 0:
            movement_str_week = ':turtle:'
        elif movement_week > 0:
            movement_str_week = f":chart_with_upwards_trend: +{movement_week}%"
        elif movement_week < 0:
            movement_str_week = f":chart_with_downwards_trend: {movement_week}%"

        formated_data.append({
            'bot': bot_name,
            'price': 'N/A' if price == 0 else price,
            'demand': demand_icon,
            'movement': movement_str,
            'movement_week': movement_str_week
        })

    chunk_data = chunks(formated_data, 24)
    i = 1
    now = datetime.datetime.now()
    list_chunk = list(chunk_data)
    count = (len(formated_data) % 24) % 3
    if count == 0:
        blank_fields_count = 0
    else:
        blank_fields_count = 3 - ((len(formated_data) % 24) % 3)
    for chunk in list_chunk:
        if i == 1:
            embed = discord.Embed(title=f"STATE OF THE MARKET {date}", description="\u200b", color=settings.DEFAULT_EMBED_COLOR)
        else:
            embed = discord.Embed(title=f"", description="\u200b", color=settings.DEFAULT_EMBED_COLOR)
        if i == len(list(list_chunk)):
            embed.set_image(url='https://i.imgur.com/ZeHPSNA.jpg')
            embed.set_footer(text="Machete FNF", icon_url="https://pbs.twimg.com/profile_images/1348329578981421058/kGKg351L.jpg")
            embed.timestamp = now
        else:
            embed.set_image(url='https://i.ibb.co/V34vfJw/ZeHPSNA.jpg')
        for values in chunk:
            embed.add_field(
                name=f"{values['bot']}",
                value=f"**Price:** ${values['price']}\n"
                      f"**Demand:** {values['demand']}\n"
                      f"**Day:** {values['movement']}\n\u200b"
                      f"**Week:** {values['movement_week']}\n\u200b",
                inline=True
            )
        if i == len(list(list_chunk)):
            for _ in range(blank_fields_count):
                embed.add_field(name=f"\u200b", value=f"\u200b", inline=True)
        i += 1
        await send_webhook(embed)
        time.sleep(1)
    print(f"Webhook sent. Took: {time.time() - start}")

###############################################################################


async def send_webhook(embed):
    await webhook_helper.sotm_webhook(embed)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(sys.argv[1:]))
