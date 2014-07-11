'''
Some utility functions.
'''

from scipy import stats
import numpy as np

GROUP_A = [4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
GROUP_B = [21, 22, 24, 25, 27, 28, 29, 30, 31, 34, 35, 36]


def to_groups(l):
    return l.loc[GROUP_A], l.loc[GROUP_B]

def ttest_summary(a, b, independent=True, equal_var=False, one_sided=True):
    '''
    Print statistics about ttests between a and b.
    '''

    # two-sided result everywhere
    # more info regarding conversion to one-sided here:
    # http://stackoverflow.com/a/15984310/1224456
    if independent:
        print('mean (a vs b): {}\t{}'.format(np.mean(a), np.mean(b)))
        print('std  (a vs b): {}\t{}'.format(np.std(a), np.std(b)))
        t, p = stats.ttest_ind(a, b, equal_var=False)
    else:
        print('mean diff: {}'.format(np.mean(a - b)))
        print('std  diff: {}'.format(np.std(a - b)))
        t, p = stats.ttest_rel(a, b)
    if one_sided:
        p = p / 2
    print('t: {}\tp: {}'.format(t, p))