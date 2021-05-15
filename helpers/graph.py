import time
import settings
import numbers

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import operator as o

BG_COLOR = '#2e3236'
TEXT_COLOR = '#b9c3cc'
GRID_COLOR = '#454b51'
RED_COLOR = '#e36b6b'
GREEN_COLOR = '#5fd79a'
OTHER_COLORS = [
    '#e36b6b',
    '#5fd79a',
    '#6a7cff',
    '#e3d421',
    '#972b2b',
    '#e36b6b',
    '#5fd79a',
    '#d165f4',
    '#6ef465'
]


def create_line_graph_pricing(data, bot='', sales=False):
    xlabels = data['xlabels']
    wts = data['wts']
    wtb = data['wtb']
    xs = np.arange(len(xlabels))
    series1 = np.array(wts).astype(np.double)
    s1mask = np.isfinite(series1)
    series2 = np.array(wtb).astype(np.double)
    s2mask = np.isfinite(series2)

    fig, ax = plt.subplots(figsize=(15, 10))
    title_obj = plt.title('Marketplaces pricing stats{}'.format(' for ' + bot.capitalize() if bot else ''), fontsize=20)
    plt.setp(title_obj, color=TEXT_COLOR)

    ax.plot(xs[s1mask], series1[s1mask], linestyle='-', marker='o', linewidth=3, label='wts', color=RED_COLOR)
    ax.plot(xs[s2mask], series2[s2mask], linestyle='-', marker='o', linewidth=3, label='wtb', color=GREEN_COLOR)
    if sales:
        i = 0
        for key, value in sales.items():
            series = np.array(sales[key]).astype(np.double)
            mask = np.isfinite(series)
            label = key
            if key not in ['renewal', 'lifetime']:
                label = f"{key} renewal"
            ax.plot(xs[mask], series[mask], linestyle=':', marker='o', linewidth=3, label=f"{label} sales", color=OTHER_COLORS[i])
            i += 1

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

    label = 'Average Price ($)'
    ax.set(ylabel=label)
    ax.grid(color=GRID_COLOR)
    ax.set_facecolor(BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    timestamp = int(round(time.time() * 1000))
    filename = 'graph{}.png'.format(timestamp)
    filepath = settings.BASE_DIR + '/tmp/{}'.format(filename)
    fig.savefig(filepath, bbox_inches='tight')
    return filepath


def create_line_graph_sales(sales, bot=''):
    xlabels = sales['xlabels']
    xs = np.arange(len(xlabels))

    fig, ax = plt.subplots(figsize=(15, 10))
    title_obj = plt.title('Sales stats{}'.format(' for ' + bot.capitalize() if bot else ''), fontsize=20)
    plt.setp(title_obj, color=TEXT_COLOR)

    if sales['data']:
        i = 0
        sales_data = sales['data']
        for key, value in sales_data.items():
            series = np.array(sales_data[key]).astype(np.double)
            mask = np.isfinite(series)
            label = key
            if key not in ['renewal', 'lifetime']:
                label = f"{key} renewal"
            ax.plot(xs[mask], series[mask], linestyle='-', marker='o', linewidth=3, label=f"{label} sales", color=OTHER_COLORS[i])
            i += 1

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

    label = 'Average Price ($)'
    ax.set(ylabel=label)
    ax.grid(color=GRID_COLOR)
    ax.set_facecolor(BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    timestamp = int(round(time.time() * 1000))
    filename = 'graph{}.png'.format(timestamp)
    filepath = settings.BASE_DIR + '/tmp/{}'.format(filename)
    fig.savefig(filepath, bbox_inches='tight')
    return filepath


def create_line_graph_demand(data, bot='', type='price'):
    xlabels = data['xlabels']
    wts = data['wts']
    wtb = data['wtb']
    wts_users = data['wts_users']
    wtb_users = data['wtb_users']

    xs = np.arange(len(xlabels))
    series1 = np.array(wts).astype(np.double)
    s1mask = np.isfinite(series1)
    series2 = np.array(wtb).astype(np.double)
    s2mask = np.isfinite(series2)
    series3 = np.array(wts_users).astype(np.double)
    s3mask = np.isfinite(series3)
    series4 = np.array(wtb_users).astype(np.double)
    s4mask = np.isfinite(series4)

    fig, (axs) = plt.subplots(2, sharex=True, figsize=(15, 10))
    fig.suptitle(f"Marketplaces demand stats for {bot.capitalize()}", fontsize=20, color=TEXT_COLOR)

    y = np.array(range(1, len(xlabels)+1))
    x = np.arange(y.shape[0])
    my_xticks = np.array(xlabels)
    frequency = round(len(xlabels)/10)

    axs[0].set_title('Demand based on unfiltered number of posts', {
        'fontsize': 14,
        'color': TEXT_COLOR
    })
    axs[0].plot(xs[s1mask], series1[s1mask], linestyle='-', marker='o', linewidth=3, label='wts', color=RED_COLOR)
    axs[0].plot(xs[s2mask], series2[s2mask], linestyle='-', marker='o', linewidth=3, label='wtb', color=GREEN_COLOR)
    axs[0].set_xticks(x[::frequency])
    axs[0].set_ylabel('Number of unfiltered posts', color=TEXT_COLOR)

    axs[1].set_title('Demand based on number of posts by unique users', {
        'fontsize': 14,
        'color': TEXT_COLOR
    })
    axs[1].plot(xs[s3mask], series3[s3mask], linestyle='-', marker='o', linewidth=3, label='wts_unique_users', color=RED_COLOR)
    axs[1].plot(xs[s4mask], series4[s4mask], linestyle='-', marker='o', linewidth=3, label='wtb_unique_users', color=GREEN_COLOR)
    axs[1].set_xticks(x[::frequency])
    axs[1].set_xticklabels(my_xticks[::frequency])
    axs[1].set_ylabel('Number of posts by unique users', color=TEXT_COLOR)

    for ax in axs:
        ax.tick_params(axis='y', labelsize=14, length=10, color=GRID_COLOR, labelcolor=TEXT_COLOR)
        ax.tick_params(axis='x', labelsize=14, length=10, color=GRID_COLOR, labelcolor=TEXT_COLOR, labelrotation=30)
        ax.set_facecolor(BG_COLOR)
        ax.grid(color=GRID_COLOR)
        ax.legend()
        ax.spines['bottom'].set_color(TEXT_COLOR)
        ax.spines['top'].set_color(TEXT_COLOR)
        ax.spines['left'].set_color(TEXT_COLOR)
        ax.spines['right'].set_color(TEXT_COLOR)

    fig.patch.set_facecolor(BG_COLOR)
    timestamp = int(round(time.time() * 1000))
    filename = 'graph{}.png'.format(timestamp)
    filepath = settings.BASE_DIR + '/tmp/{}'.format(filename)
    fig.savefig(filepath, bbox_inches='tight')
    return filepath


def get_list_average(lst):
    lst = [x for x in lst if isinstance(x, numbers.Number)]
    try:
        return sum(lst) / len(lst)
    except ZeroDivisionError:
        return 0


def create_bar_chart_demand(data, bot):
    dpoints = np.array(data)

    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    fig, ax = plt.subplots(figsize=(30, 10))
    title_obj = plt.title('Marketplaces pricing stats{}'.format(' for ' + bot.capitalize() if bot else ''), fontsize=20)
    plt.setp(title_obj, color=TEXT_COLOR)

    '''
    Create a barchart for data across different categories with
    multiple conditions for each category.

    @param ax: The plotting axes from matplotlib.
    @param dpoints: The data set as an (n, 3) numpy array
    '''

    # Aggregate the conditions and the categories according to their
    # mean values
    conditions = [(c, np.mean(dpoints[dpoints[:, 0] == c][:, 2].astype(float))) for c in np.unique(dpoints[:, 0])]
    categories = [(c, np.mean(dpoints[dpoints[:, 1] == c][:, 2].astype(float))) for c in np.unique(dpoints[:, 1])]
    conditions = [c[0] for c in conditions]
    categories = [c[0] for c in categories]

    dpoints = np.array(sorted(dpoints, key=lambda x: categories.index(x[1])))

    # the space between each set of bars
    space = 0.3
    n = len(conditions)
    width = (1 - space) / (len(conditions))

    rects = []
    # Create a set of bars at each position
    for i, cond in enumerate(conditions):
        print(i)
        print(cond)
        indeces = range(1, len(categories)+1)
        vals = dpoints[dpoints[:, 0] == cond][:, 2].astype(np.float)
        pos = [j - (1 - space) / 4 + i * width for j in indeces]
        # pos = [j - space * width for j in indeces]
        bar = ax.bar(pos, vals, width=width, label=cond, color=RED_COLOR if cond == 'wts' else GREEN_COLOR)
        rects.append(bar)

    for rectsarr in rects:
        for rect in rectsarr:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height + 0.1, '%d' % int(height), ha='center', va='bottom', color=TEXT_COLOR)

    y = np.array(range(1, len(indeces)+1))
    x = np.arange(y.shape[0])
    frequency = round(len(indeces)/10)
    # Set the x-axis tick labels to be equal to the categories
    ax.set_xticks(indeces)
    # ax.set_xticks(x[::frequency])
    # ax.set_xticklabels(categories[::frequency])
    ax.set_xticklabels(categories)
    plt.setp(plt.xticks()[1], rotation=90)

    # Add the axis labels
    ax.set_ylabel("RMSD")
    ax.set_xlabel("Structure")
    ax.tick_params(axis='y', labelsize=14, length=10, color=GRID_COLOR, labelcolor=TEXT_COLOR)
    ax.tick_params(axis='x', labelsize=14, length=10, color=GRID_COLOR, labelcolor=TEXT_COLOR, labelrotation=65)
    ax.set_facecolor(BG_COLOR)
    ax.grid(color=GRID_COLOR)
    ax.legend()
    ax.spines['bottom'].set_color(TEXT_COLOR)
    ax.spines['top'].set_color(TEXT_COLOR)
    ax.spines['left'].set_color(TEXT_COLOR)
    ax.spines['right'].set_color(TEXT_COLOR)

    # Add a legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper left')
    fig.patch.set_facecolor(BG_COLOR)
    timestamp = int(round(time.time() * 1000))
    filename = 'graph{}.png'.format(timestamp)
    filepath = settings.BASE_DIR + '/tmp/{}'.format(filename)
    fig.savefig(filepath, bbox_inches='tight')
    return filepath