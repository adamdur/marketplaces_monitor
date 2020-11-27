import time
import settings
import numbers

import matplotlib.pyplot as plt
import numpy as np

BG_COLOR = '#2e3236'
TEXT_COLOR = '#b9c3cc'
GRID_COLOR = '#454b51'


def create_line_graph(data, bot='', type='price'):
    xlabels = data['xlabels']
    wts = data['wts']
    wtb = data['wtb']
    xs = np.arange(len(xlabels))
    series1 = np.array(wts).astype(np.double)
    s1mask = np.isfinite(series1)
    series2 = np.array(wtb).astype(np.double)
    s2mask = np.isfinite(series2)

    fig, ax = plt.subplots(figsize=(15, 10))
    if type == 'price':
        title_label = 'pricing'
    elif type == 'demand':
        title_label = 'demand'
    title_obj = plt.title('Marketplaces {} stats{}'.format(title_label, ' for ' + bot.capitalize() if bot else ''), fontsize=20)
    plt.setp(title_obj, color=TEXT_COLOR)

    ax.plot(xs[s1mask], series1[s1mask], linestyle='-', marker='o', linewidth=3, label='wts')
    ax.plot(xs[s2mask], series2[s2mask], linestyle='-', marker='o', linewidth=3, label='wtb')

    y = np.array(range(1, len(xlabels)+1))
    x = np.arange(y.shape[0])
    my_xticks = np.array(xlabels)
    frequency = 3
    plt.xticks(x[::frequency], my_xticks[::frequency], rotation=30, fontsize=16, fontweight='bold')
    plt.yticks(fontsize=20, fontweight='bold')
    plt.legend()

    for t in ax.xaxis.get_ticklabels():
        t.set_color(TEXT_COLOR)
    for t in ax.yaxis.get_ticklabels():
        t.set_color(TEXT_COLOR)
    ax.spines['bottom'].set_color(TEXT_COLOR)
    ax.spines['top'].set_color(TEXT_COLOR)
    ax.spines['left'].set_color(TEXT_COLOR)
    ax.spines['right'].set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.tick_params(axis='x', colors=TEXT_COLOR)
    ax.tick_params(axis='y', colors=TEXT_COLOR)

    if type == 'price':
        label = 'Average Price ($)'
    elif type == 'demand':
        label = 'Number of posts per day'
    ax.set(ylabel=label)
    ax.grid(color=GRID_COLOR)
    ax.set_facecolor(BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    timestamp = int(round(time.time() * 1000))
    filename = 'graph{}.png'.format(timestamp)
    filepath = settings.BASE_DIR + '/tmp/{}'.format(filename)
    fig.savefig(filepath, bbox_inches='tight')
    return filepath


def get_list_average(lst):
    lst = [x for x in lst if isinstance(x, numbers.Number)]
    return sum(lst) / len(lst)
