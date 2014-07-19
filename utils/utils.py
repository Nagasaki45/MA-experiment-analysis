'''
Some utility functions.
'''

from collections import Iterable

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

GROUP_A = [4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
GROUP_B = [21, 22, 24, 25, 27, 28, 29, 30, 31, 34, 35, 36]


def to_groups(l):
    return l.loc[GROUP_A], l.loc[GROUP_B]


def flatten(items, ignored_types=(str, bytes)):
    '''From the cookbook, p.135.'''
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignored_types):
            yield from flatten(x, ignored_types)
        else:
            yield x


def list_to_chunks(l, size):
    return [l[i:i + size] for i in range(0, len(l), size)]


def divide_apply_unpack(data, function, dimension=2, args=(), index=None):
    '''Divide x into list of n-dimensional vectors, apply the function
    on each of them, unpack (flatten) and return.
    '''
    chunks = list_to_chunks(data, dimension)
    applied = [function(x, *args) for x in chunks]
    flat = list(flatten(applied))
    if len(flat) == len(data):
        return flat
    return pd.Series(flat, index=index)


def independent_one_sided_ttest_summary(a, b, **kwargs):
    '''Print statistics about ttests between a and b.'''
    # two-sided result everywhere
    # more info regarding conversion to one-sided here:
    # http://stackoverflow.com/a/15984310/1224456
    means = [np.mean(array) for array in (a, b)]
    stds = [np.std(array) for array in (a, b)]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    p = p / 2  # from two-sided to one-sided t-test
    # standard error of means
    # http://en.wikipedia.org/wiki/Standard_error#Standard_error_of_the_mean
    yerr = [np.std(array) / len(array) for array in (a, b)]
    print('mean (a vs b): {}\t{}'.format(*means))
    print('std  (a vs b): {}\t{}'.format(*stds))
    print('t: {}\tp: {}'.format(t, p))

    plt.bar([0, 1], means, align='center', width=0.5, yerr=yerr,
        ecolor='black', capsize=10)
    plt.xticks([0, 1], ['Control', 'Interactive'])
    plt.xlim((-0.5, 1.5))
    for method, value in kwargs.items():
        getattr(plt, method)(value)


# TESTS!
# list_to_chunks
assert list_to_chunks([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]