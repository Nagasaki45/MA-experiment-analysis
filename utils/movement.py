from . import data as data_module
from . import utils


def point_distance(diffs):
    x_diff, y_diff = diffs
    return (x_diff ** 2 + y_diff ** 2) ** 0.5


def distance(group, block):
    '''
    Returns a DataFrame with the distance each participant passed during the block,
    divided by the length of the block in seconds.
    '''

    data = data_module.participants_data(group, block)
    participants_nums = data_module.get_participants(group)
    columns = ['participant{}'.format(p) for p in participants_nums]
    block_duration = data_module.get_block_duration(group, block)
    # get diffs between rows, dropna (first row)
    diffed = data.diff().dropna()
    # apply the point_distance function to chunked data
    # send the new columns names
    dist_values = diffed.apply(utils.divide_apply_unpack, axis=1,
                               args=(point_distance, 2, (), columns))
    return dist_values.sum(axis=0) / block_duration
