'''
SUS utilities. Based on:
http://www.usabilitynet.org/trump/documents/Suschapt.doc
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from . import data

questions = [
    'I think that I would like to use this system frequently',
    'I found the system unnecessarily complex',
    'I thought the system was easy to use',
    'I think that I would need the support of a technical person to be able to use this system',
    'I found the various functions in this system were well integrated',
    'I thought there was too much inconsistency in this system',
    'I would imagine that most people would learn to use this system very quickly',
    'I found the system very cumbersome to use',
    'I felt very confident using the system',
    'I needed to learn a lot of things before I could get going with this system',
]


def load_table():
    return data.csv_table()[['usability{}'.format(i) for i in range(1, 11)]]


def fillna(table):
    return table.fillna(value=3)  # SUS specs


def score(l):
    '''Calculate the SUS score of a single survey.'''

    total = [item_contribution(i, v) for i, v in enumerate(l)]
    return 2.5 * sum(total)


def item_contribution(index, value):
    if index % 2 == 0:
        return value - 1
    return 5 - value


def break_lines(s, max_letters=60, indent=6):
    if len(s) < max_letters:
        return s
    next_space_index = s.find(' ', max_letters)
    if next_space_index > 0:
        new_string = '{}\n{}{}'.format(
            s[:next_space_index],
            ' ' * indent,
            break_lines(s[next_space_index + 1:]),
        )
    else:
        new_string = s
    return new_string


def per_question_plot(a, b):
    '''
    10 questions, ttest for each of them.
    '''
    df = pd.DataFrame({
        'c': a.mean(axis=0).values,
        'i': b.mean(axis=0).values,
        'c_err': a.var(axis=0).values / 10 ** 0.5,
        'i_err': b.var(axis=0).values / 10 ** 0.5,
    })

    ind = np.arange(len(df))
    w = 0.4

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_axes([0.05, 0.05, 0.4, 0.9])
    ax.barh(ind + w, df.c, w, color='blue', label='Control',
            xerr=df.c_err, ecolor='black')
    ax.barh(ind, df.i, w, color='yellow', label='Interactive',
            xerr=df.i_err, ecolor='black')

    ts, ps = stats.ttest_ind(b, a)
    ylabels = ['{}) {}\n        (t: {:.2f}, p: {:.2f})'.format(i, break_lines(q), t, p)
               for i, (q, t, p) in enumerate(zip(questions, ts, ps), start=1)]

    ax.set(yticks=ind + w, yticklabels=ylabels,
           ylim=[2 * w - 1, len(df)], xlim=[1, 5])
    ax.yaxis.set_ticks_position('right')
    for label in ax.get_yticklabels():
        label.set_fontsize(13)
    ax.yaxis.grid()
    ax.legend()


if __name__ == '__main__':
    assert score([5, 4, 2, 1, 2, 3, 2, 4, 5, 2]) == 55
