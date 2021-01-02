import os
import sys
import schedule
import time
import settings
import datetime
from multiprocessing import Process

from helpers import setup_data as setup_data_helper
from helpers import bb_api as botbroker

this = sys.modules[__name__]


def main():
    print('BB Bots updater running...')
    date = datetime.datetime.now()
    file = settings.LOGS_DIR + '/' + str(date.timestamp()) + '.txt'
    if not os.path.isfile(file):
        with open(file, mode='w') as f:
            f.write(f"{date}  Running BB bots updater")

    schedule.every(30).minutes.do(bot_api_call)
    while True:
        schedule.run_pending()
        time.sleep(1)


def bot_api_call():
    bots = botbroker.get_bots(sort_by='name', order='asc')
    if bots:
        print('[UPDATING BB BOTS]')
        setup_data_helper.save_botbroker_bots(bots)


if __name__ == "__main__":
    start = time.time()
    p1 = Process(target=main, args=())
    p1.start()
    p1.join()
    print('Finished. Total elapsed time: {}'.format(time.time() - start))
