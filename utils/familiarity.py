import matplotlib.pyplot as plt

from . import data


def load_table(group):
    group = group.upper()
    participants = getattr(data, 'GROUP_{}'.format(group))
    familiarity_columns = ['familiarity{}'.format(i) for i in participants]
    mat = (data.csv_table().loc[participants, familiarity_columns] - 1) / 4
    mat.columns = participants
    mat.index = participants
    for p in participants:
        mat.loc[p, p] = 1
    return mat


def show_map(mat):
    plt.imshow(mat, cmap='hot', interpolation='none', vmin=0, vmax=1)
    ticks = [range(len(mat.columns)), mat.columns]
    plt.xticks(*ticks)
    plt.yticks(*ticks)
