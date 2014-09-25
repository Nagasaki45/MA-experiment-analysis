'''Singletons and additional data'''

import functools
import os
import json

import pandas as pd

from . import utils

GROUP_A = [4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
GROUP_B = [21, 22, 24, 25, 27, 28, 29, 30, 31, 34, 35, 36]

block_mod = {'A': 0, 'B': 4}  # converts blocks 4 - 7 of group B to 1 - 3


def to_groups(l):
    return l.loc[GROUP_A], l.loc[GROUP_B]


def get_participants(group):
    return {'A': GROUP_A, 'B': GROUP_B}[group.upper()]


def memo(f):
    memory = []
    @functools.wraps(f)
    def wrapper():
        if not memory:
            memory.append(f())
        return memory[0]
    return wrapper


@memo
def csv_table():
    '''Returns the main survey data as pandas DataFrame.'''
    return pd.read_csv('raw_surveys_data.csv', index_col='id')


@memo
def video_metadata():
    metadata_path = os.path.join('raw_pos', 'METADATA.json')
    with open(metadata_path) as f:
        return json.load(f)


def _block_frames(group, block):
    block_string = 'block {}'.format(block + block_mod[group])
    block_metadata = video_metadata()[block_string]
    start = block_metadata['start']
    end = block_metadata['end']
    return list(utils.f_range(start, end, 0.5))


def participants_data(group, block=None):
    group = group.upper()
    d = groups[group]
    # filter participants only
    participants = get_participants(group)
    d = d[['participant{}{}'.format(n, axis) for n in participants
                                             for axis in ['x', 'y']]]
    if block is None:
        return d
    return d.loc[_block_frames(group, block)]


def beacons_data(group, block=None):
    group = group.upper()
    d = groups[group]
    # filter beacons only
    beacons = range(1, 7)
    d = d[['beacon{}{}'.format(n, axis) for n in beacons
                                        for axis in ['x', 'y']]]
    if block is None:
        return d
    return d.loc[_block_frames(group, block)]


def get_bench():
    '''Returns the bench singleton.'''
    return Bench.get()


def create_bench(pos):
    '''Set the bench singleton.'''
    try:
        return Bench(pos)
    except SingletonError:
        return get_bench()


class SingletonError(RuntimeError):
    pass


class Bench:
    COLOR = (1, 0, 0, 0.5)
    RADIUS = 2  # meters
    singleton = []

    @classmethod
    def get(cls):
        if cls.singleton:
            return cls.singleton[0]
        return None

    def __init__(self, pos):
        if self.singleton:
            raise SingletonError('Bench is a singleton')
        self.pos = pos
        self.singleton.append(self)


# boundaries of the dance floor
lower = None
upper = None

# groups video data
groups = None
