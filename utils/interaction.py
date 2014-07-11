def score(row, block_number):
    '''Calculate the social interaction score of a single survey.'''

    q1 = row['block{}1'.format(block_number)]
    q2 = row['block{}2'.format(block_number)]
    total = (q1 - 1) + (q2 - 1)
    return 12.5 * total
