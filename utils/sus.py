'''
SUS utilities. Based on:
http://www.usabilitynet.org/trump/documents/Suschapt.doc
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

def numbered_questions():
    return ['{}) {}'.format(i, q) for i, q in enumerate(questions, start=1)]


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

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(ind + w, df.c, w, color='blue', label='Control',
            xerr=df.c_err, ecolor='black')
    ax.barh(ind, df.i, w, color='yellow', label='Interactive',
            xerr=df.i_err, ecolor='black')

    ax.set(yticks=ind + w, yticklabels=numbered_questions(),
           ylim=[2 * w - 1, len(df)], xlim=[1, 5])
    ax.yaxis.set_ticks_position('right')
    ax.yaxis.grid()
    ax.legend()


if __name__ == '__main__':
    assert score([5, 4, 2, 1, 2, 3, 2, 4, 5, 2]) == 55
