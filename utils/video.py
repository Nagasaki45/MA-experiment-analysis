import os

import numpy as np
from scipy import linalg
import pandas as pd

from . import data
from . import utils


DATA_DIR = 'raw_pos'


def _load_tables(participants, beacons_group):
    for p in participants:
        path = os.path.join(DATA_DIR, 'participant{:02}.csv'.format(p))
        frame = pd.read_csv(path, index_col='time')
        frame.columns = ['participant{}{}'.format(p, axis)
                         for axis in ['x', 'y']]
        yield frame
    for b in range(1, 7):
        path = os.path.join(DATA_DIR,
                            'beacon{}{}.csv'.format(beacons_group, b))
        frame = pd.read_csv(path, index_col='time')
        frame.columns = ['beacon{}{}'.format(b, axis)
                         for axis in ['x', 'y']]
        yield frame


def load_table(group):
    group = group.upper()
    participants = getattr(data, 'GROUP_{}'.format(group))
    return pd.concat(_load_tables(participants, group), axis=1)


def load_metadata():
    return data.video_metadata()


def transform(data, knwon_xs, known_ys):
    A, b = solve_affine_transformation(knwon_xs, known_ys)
    return data.apply(utils.divide_apply_unpack, axis=1,
                      args=(transform_vec, 2, (A, b)))


def append_one_and_stack(vecs):
    m = np.array(vecs).transpose()
    return np.vstack([m, np.ones(shape=[1, m.shape[1]])])


def solve_affine_transformation(knwon_xs, known_ys):
    '''Returns the affine transformation as A and b vector.
    knwon_xs and known_ys should be equal length lists of X and Y
    vectors of the same dimension.

    Additional info:
    http://stackoverflow.com/a/2756165/1224456
    http://en.wikipedia.org/wiki/Affine_transformation
    '''
    X = append_one_and_stack(knwon_xs)
    Y = append_one_and_stack(known_ys)
    aug_matrix = np.dot(Y, linalg.inv(X))
    A = aug_matrix[:-1, :-1]
    b = aug_matrix[:-1, -1]
    return A, b


def transform_vec(x, A, b):
    '''Transform the x vector using the affine transformation described
    by the matrix A and the translation vector b.
    '''
    return np.dot(A, x) + b


def participants_data(group):
    group = group.upper()
    d = data.groups[group]
    # filter participants only
    participants = data.get_participants(group)
    return d[['participant{}{}'.format(n, axis) for axis in ['x', 'y']
                                                for n in participants]]


# TESTS!
# append_one_and_stack
assert np.all(append_one_and_stack([(1, 2), (3, 4)]) == \
              np.array([[1, 3], [2, 4], [1, 1]])
             )

# solve_affine_transformation and transform
known_ys = [(0, 0), (9.8, 0), (9.8, 6.3)]
a_known_xs = [(77, 254), (414, 247), (598, 275)]
b_known_xs = [(13, 322), (358, 321), (545, 353)]
for known_xs in [a_known_xs, b_known_xs]:
    A, b = solve_affine_transformation(known_xs, known_ys)
    for x, y in zip(known_xs, known_ys):
        assert np.allclose(transform_vec(x, A, b), y)
