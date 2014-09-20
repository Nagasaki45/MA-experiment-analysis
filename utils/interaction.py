from . import data


def load_tables():
    return data.csv_table()[['block{}{}'.format(i, j) for i in range(1, 9)
                                                      for j in range(1, 3)]]

def score(row, block_number):
    '''Calculate the social interaction score of a single survey.'''

    q1 = row['block{}1'.format(block_number)]
    q2 = row['block{}2'.format(block_number)]
    total = (q1 - 1) + (q2 - 1)
    return 12.5 * total
