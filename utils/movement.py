from . import data
from . import video
from . import utils


def point_distance(diffs):
    x_diff, y_diff = diffs
    return (x_diff ** 2 + y_diff ** 2) ** 0.5


def distance(block):
    '''
    Returns a DataFrame with the distance each participant passed during the block,
    divided by the length of the block in seconds.
    Block should be 1, 2, 3. The block number for group B will adjust automatically.
    '''
    
    groups = data.groups
    metadata = data.video_metadata()
    
    block_mod = {'A': 0, 'B': 4}
    results = []
    for name in sorted(groups):
        block_metadata = metadata['block {}'.format(block + block_mod[name])]
        start = block_metadata['start']
        end = block_metadata['end']
        duration = end - start
        # data, filtered by metadata
        d = video.participants_data(name).loc[utils.f_range(start, end, 0.5)]
        # get diffs between rows, dropna (first row)
        diffed = d.diff().dropna()
        # columns napes from utils GROUP_A / GROUP_B
        columns = ['participant{}'.format(p) for p in data.get_participants(name)]
        # apply the point_distance function to chunked data, send the new columns names
        dist_values = diffed.apply(utils.divide_apply_unpack, axis=1, args=(point_distance, 2, (), columns))
        results.append(dist_values.sum(axis=0) / duration)
    return results
