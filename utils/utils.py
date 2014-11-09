'''
Some utility functions.
'''

from collections import Iterable, defaultdict
import functools

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols


def memo(f):
    memory = {}
    @functools.wraps(f)
    def wrapper(*args):
        if args not in memory:
            memory[args] = f(*args)
        return memory[args]
    return wrapper


def flatten(items, ignored_types=(str, bytes)):
    '''From the cookbook, p.135.'''
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignored_types):
            for inner in flatten(x, ignored_types):
                yield inner
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
    # standard error of means
    # http://en.wikipedia.org/wiki/Standard_error#Standard_error_of_the_mean
    stderrs = [np.std(array) / np.sqrt(len(array)) for array in (a, b)]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    p = p / 2  # from two-sided to one-sided t-test
    print('mean (a vs b): {:.3f}\t{:.3f}'.format(*means))
    print('stderr  (a vs b): {:.3f}\t{:.3f}'.format(*stderrs))
    print('t: {}\tp: {}\tdf: {}'.format(t, p, len(a) + len(b) - 2))

    plt.bar([0, 1], means, align='center', width=0.5, yerr=stderrs,
        ecolor='black', capsize=10)
    plt.xticks([0, 1], ['Control', 'Interactive'])
    plt.xlim((-0.5, 1.5))
    for method, value in kwargs.items():
        getattr(plt, method)(value)


def euclidean_distance(a, b):
    array = np.array([a, b])
    return sum((array[1] - array[0]) ** 2) ** 0.5


def f_range(start, stop, step):
    current = start
    while current < stop:
        yield current
        current += step


def two_groups_three_bars(data_dict, title=None, **kwargs):
    full_template = '{}/{} -- mean: {:.03}, stderr: {:.03}'
    non_error_template = '{}/{} -- mean: {:.03}'
    means = defaultdict(list)
    errs = defaultdict(list)
    for (group, block), vec in sorted(data_dict.items()):
        if isinstance(vec, Iterable):
            mean = np.nanmean(vec)
            err = np.nanstd(vec) / np.sqrt(len(vec))
            print(full_template.format(group, block, mean, err))
        else:
            mean = vec
            err=0
            print(non_error_template.format(group, block, mean))
        means[group].append(mean)
        errs[group].append(err)

    pad = 0.1
    ind = np.arange(3) + pad
    w = (1 - 2 * pad) / 2

    ax = plt.gca()
    if title:
        ax.set_title(title)
    ax.bar(ind, means['A'], w, color='blue', label='Control',
           yerr=errs['A'], ecolor='black')
    ax.bar(ind + w, means['B'], w, color='yellow', label='Interactive',
           yerr=errs['B'], ecolor='black')
    ax.set(xticks=ind + w,
           xticklabels=['Session {}'.format(x) for x in [1, 2, 3]],
           **kwargs)
    ax.grid(axis='y')
    ax.legend(loc='best')


def nums_from_data(participants_data):
    # find participants nums from columns
    names = participants_data.columns.values
    # for every (x, y) the first is enough
    names = [x[0] for x in list_to_chunks(names, 2)]
    nums_strings = [name[len('participant'):-1] for name in names]
    return [int(n_s) for n_s in nums_strings]


def participants_as_list_of_dicts(participants_data):
    l = []
    p_nums = nums_from_data(participants_data)
    for _, row in participants_data.iterrows():
        chunks = list_to_chunks(row, 2)
        l.append({num: list(chunk) for num, chunk in zip(p_nums, chunks)})
    return l


def two_groups_three_plots(data_dict, title=None, **kwargs):
    fig = plt.figure(figsize=(14, 6))
    if title:
        fig.suptitle(title)
    enumeration = enumerate(sorted(data_dict.items()), start=1)
    for i, ((group, block), vec) in enumeration:
        ax = plt.subplot(2, 3, i)
        ax.plot(vec)
        ax.set(title='Group {} session {}'.format(group, block),
               **kwargs)
        ax.grid(axis='y')


def to_model_matrix(d, columns=None):
    '''
    Gets a dict of (group, block): vec and returns a pandas
    model matrix.
    '''
    l = []
    for (group, block), vec in sorted(d.items()):
        for val in vec:
            l.append((group, block, val))
    return pd.DataFrame(l, columns=columns)


def anova(d):
    mat = to_model_matrix(d, columns=['group', 'block', 'score'])
    linear_model = ols('score ~ C(group) + C(block) + C(group)*C(block)',
                       data=mat).fit()
    return sm.stats.anova_lm(linear_model)


def lines_to_floats(path):
    with open(path) as f:
        return [float(i.strip()) for i in f.readlines()]


def letter_to_name(x):
    x = x.upper()
    return {'A': 'Control group', 'B': 'Interactive group'}[x]


def boundaries_indices(array):
    '''
    For an array of repeated values, find in which indices the values changes.
    '''
    indices = []
    x0 = array[0]
    for i, x in enumerate(array[1:], start=1):
        if x != x0:
            indices.append(i)
        x0 = x
    return indices


# TESTS!
# list_to_chunks
assert list_to_chunks([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

# euclidean_distance
assert euclidean_distance([0, 3], [4, 0]) == 5

# to_model_matrix
d = {
    ('A', 1): [1, 2],
    ('A', 2): [3, 4],
    ('B', 1): [5, 6],
    ('B', 2): [7, 8],
}
expected = pd.DataFrame([
    ['A', 1, 1],
    ['A', 1, 2],
    ['A', 2, 3],
    ['A', 2, 4],
    ['B', 1, 5],
    ['B', 1, 6],
    ['B', 2, 7],
    ['B', 2, 8],
])
from pandas.util.testing import assert_frame_equal
assert_frame_equal(to_model_matrix(d), expected)

# test with columns
columns = ['group', 'block', 'value']
expected.columns = columns
assert_frame_equal(to_model_matrix(d, columns), expected)

# test boundaries_indices
array = [0, 0, 0, 1, 2, 2, 3]
assert boundaries_indices(array) == [3, 4, 6]
