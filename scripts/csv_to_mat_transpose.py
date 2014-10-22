'''
Takes all cooked csv file of the format:

    group, session, value

and create csv matrices from them for spss analysis.
'''

import os
import pandas as pd
import numpy as np

COOKED_DIR = os.path.join('..', 'cooked')
OUTPUT_DIR = os.path.join('..', 'spss_ready')


def _group_row(original, group_name):
    unique_session_values = np.unique(original['session'])
    g_data = original[original['group'] == group_name]
    sessions = (g_data[g_data['session'] == s] for s in unique_session_values)
    s_values = (s.val.values for s in sessions)
    as_columns = (s[:, np.newaxis] for s in s_values)
    horizontal = np.hstack(as_columns)
    columns = ['group'] + ['s{}'.format(i) for i in unique_session_values]
    new = pd.DataFrame(horizontal, columns=columns[1:])
    new['group'] = group_name
    return new[columns]


def to_spss_mat(original):
    rows = (_group_row(original, group) for group in ('A', 'B'))
    new = pd.concat(rows, ignore_index=True)
    new.index.name = 'part'
    return new


def main():
    for filename in os.listdir(COOKED_DIR):
        # dont even try to work on cooked video data
        if filename.startswith('video'):
            continue
        print('Working on {}...'.format(filename))
        path = os.path.join(COOKED_DIR, filename)
        original = pd.read_csv(path, names=['group', 'session', 'val'])
        new = to_spss_mat(original)
        new.to_csv(os.path.join(OUTPUT_DIR, filename))
    

if __name__ == '__main__':
    main()