'''Singletons and additional data'''

import functools
import os
import json

import pandas as pd

from . import utils

GROUP_A = [4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
GROUP_B = [21, 22, 24, 25, 27, 28, 29, 30, 31, 34, 35, 36]

block_mod = {'A': 0, 'B': 4}  # converts blocks 4 - 7 of group B to 1 - 3


# dataset for comparing my sus results.
# Aaron Bangor, Philip T. Kortum & James T. Miller (2008)
# An Empirical Evaluation of the System Usability Scale,
# International Journal of Human-Computer Interaction, 24:6, 574-594
sus_dataset = pd.DataFrame(
    [[2324 , 206  ],
     [70.14, 69.69],
     [75.00, 70.91],
     [21.71, 11.87]],
    columns=['individual_surveys', 'multisurvey_studies'],
    index=['count', 'mean', 'median', 'std'],
)


def to_groups(l):
    return l.loc[GROUP_A], l.loc[GROUP_B]


def get_participants(group):
    return {'A': GROUP_A, 'B': GROUP_B}[group.upper()]


@utils.memo
def csv_table():
    '''Returns the main survey data as pandas DataFrame.'''
    return pd.read_csv('raw_surveys_data.csv', index_col='id')


@utils.memo
def video_metadata():
    metadata_path = os.path.join('raw_pos', 'METADATA.json')
    with open(metadata_path) as f:
        return json.load(f)


@utils.memo
def _block_frames(group, block):
    block_string = 'block {}'.format(block + block_mod[group])
    block_metadata = video_metadata()[block_string]
    start = block_metadata['start']
    end = block_metadata['end']
    return list(utils.f_range(start, end, 0.5))


@utils.memo
def video_data(group):
    low = group.lower()
    path = os.path.join('cooked', 'video_group_{}.csv'.format(low))
    return pd.read_csv(path, index_col='frame')


@utils.memo
def participants_data(group, block):
    d = video_data(group)
    # filter participants only
    participants = get_participants(group)
    d = d[['participant{}{}'.format(n, axis) for n in participants
                                             for axis in ['x', 'y']]]
    return d.loc[_block_frames(group, block)]


@utils.memo
def beacons_data(group, block):
    d = video_data(group)
    # filter beacons only
    beacons = range(1, 7)
    d = d[['beacon{}{}'.format(n, axis) for n in beacons
                                        for axis in ['x', 'y']]]
    return d.loc[_block_frames(group, block)]


@utils.memo
def get_bench():
    path = os.path.join('cooked', 'video_bench_pos.csv')
    return utils.lines_to_floats(path)


@utils.memo
def get_boundaries():
    path = os.path.join('cooked', 'video_boundaries.csv')
    return utils.lines_to_floats(path)


def get_block_duration(group, block):
    metadata = video_metadata()
    block_metadata = metadata['block {}'.format(block + block_mod[group])]
    return block_metadata['end'] - block_metadata['start']


def save_to_cooked(d, csv_name):
    mat = utils.to_model_matrix(d)
    path = os.path.join('cooked', '{}.csv'.format(csv_name))
    mat.to_csv(path, index=False, float_format='%0.4f')
