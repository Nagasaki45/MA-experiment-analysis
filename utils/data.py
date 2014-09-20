'''Singletons and additional data'''

import functools
import os
import json

import pandas as pd

GROUP_A = [4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
GROUP_B = [21, 22, 24, 25, 27, 28, 29, 30, 31, 34, 35, 36]

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
