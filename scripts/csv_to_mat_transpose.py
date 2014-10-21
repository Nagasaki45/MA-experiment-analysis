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
    columns = ['group', 's1', 's2', 's3']
    g_data = original[original['group'] == group_name]
    sessions = (g_data[g_data['session'] == s] for s in (1, 2, 3))
    s_values = (s.val.values for s in sessions)
    as_columns = (s[:, np.newaxis] for s in s_values)
    horizontal = np.hstack(as_columns)
    new = pd.DataFrame(horizontal, columns=columns[1:])
    new['group'] = group_name
    return new[columns]


def to_spss_mat(original):
    new = pd.concat((_group_row(original, group) for group in ('A', 'B')),
                    ignore_index=True)
    new.index.name = 'part'
    return new


def main():
    for filename in os.listdir(COOKED_DIR):
        # dont even try to work on cooked video data
        if filename.startswith('video'):
            continue
        path = os.path.join(COOKED_DIR, filename)
        original = pd.read_csv(path, names=['group', 'session', 'val'])
        new = to_spss_mat(original)
        new.to_csv(os.path.join(OUTPUT_DIR, filename))
    

if __name__ == '__main__':
    main()