import collections

import numpy as np

from . import utils, data

NEAR = 1  # meter
MOVEMENT_THRESH = 0.4  # meter per frame (frame rate is 2Hz)

dist = utils.euclidean_distance


def close_to_beacon(group, block, threshold=NEAR, exclude_bench=False):
    '''
    Returns a matrix where columns are beacons and rows are timestamps.
    The content of the matrix are the count of participants near each
    beacon.

    Parameters
    ==========
        group (str)
        block (int)

    Optional parameters
    ===================
        threashold (int) (default=1)
        exclude_bench (bool) (default=False)

    Return
    ======
        (np.ndarray): Shape is (timestamps, number_of_beacons).
    '''

    participants = data.participants_data(group, block)
    beacons = data.beacons_data(group, block)

    bench = data.get_bench()

    # how many participants for each beacon (column) per timestamp (row)
    close_to = []
    # rows are participants and columns are beacons
    # indicates if a participant is close to the beacon (boolean)
    frame_mat = np.zeros((len(data.get_participants(group)), 6), dtype=bool)
    zipped = zip(participants.iterrows(), beacons.iterrows())
    for (_, ps), (_, bs) in zipped:  # _ are timestamps
        # per timestamp, fill frame_mat with distances
        for i, pa in enumerate(utils.list_to_chunks(ps.values, 2)):
            for j, be in enumerate(utils.list_to_chunks(bs.values, 2)):
                if exclude_bench and dist(pa, bench.pos) < bench.RADIUS:
                    frame_mat[i, j] = 0
                else:
                    frame_mat[i, j] = dist(pa, be) < threshold
        frame_sums = frame_mat.sum(axis=0)
        close_to.append(frame_sums)
    return np.array(close_to)


def close_to_pos(pos, candidates, radius=NEAR):
    '''
    Parameters
    ==========
        pos (tuple): (x, y).
        candidates (list): a list of (name, x, y) tuples.

    Optional parameters
    ===================
        radius (float) (default=1)

    Returns
    =======
        (set): a set of names that are inside the radius.
    '''
    return {c[0] for c in candidates if dist(pos, (c[1], c[2])) < radius}


def dataframe_zipper_chunker(table_a, table_b):
    '''
    GENERATOR!
    Takes two pd.DataFrames and return a generator over the
    rows as (first_rows, second_rows) tuple.
    Each "row" element is chunked to points in 2d.
    '''
    zipped = zip(table_a.iterrows(), table_b.iterrows())
    for (index, row_a), (index, row_b) in zipped:
        chunks_a = [x.values for x in utils.list_to_chunks(row_a, 2)]
        chunks_b = [x.values for x in utils.list_to_chunks(row_b, 2)]
        yield index, chunks_a, chunks_b


def beacon_dropouts(group, block, dist_thresh=NEAR,
                    movement_thresh=MOVEMENT_THRESH):
    '''
    Returns a dictionary where keys are timestamps
    and values are lists that contains the percentage of participants
    that have been dropped out between the last timestamps.
    Ignore beacons / frames with movement lower then movement_thresh
    and beacons with less then 2 participants close to them in the
    beginning of the movement.
    '''
    p_nums = data.get_participants(group)
    p_data = data.participants_data(group, block)
    b_data = data.beacons_data(group, block)

    gen = dataframe_zipper_chunker(p_data, b_data)
    # get first line
    _, last_participants, last_beacons = next(gen)
    # add the index of each participant to the last_participants tuples
    last_participants = [(num, x, y) for num, (x, y)
                         in zip(p_nums, last_participants)]
    dropouts = collections.defaultdict(list)  # data collected here
    for timestamp, participants, beacons in gen:
        # add the index of each participant to the participants tuples
        participants = [(num, x, y) for num, (x, y)
                        in zip(p_nums, participants)]
        for last_beacon, beacon in zip(last_beacons, beacons):
            # ignore beacons that doesn't moved enough between those frames
            if not dist(last_beacon, beacon) > movement_thresh:
                continue
            last_close = close_to_pos(last_beacon, last_participants,
                                      dist_thresh)
            # ignore beacons with less then two participants around
            if len(last_close) < 2:
                continue
            close = close_to_pos(beacon, participants, dist_thresh)
            left = last_close - close
            dropout_percentage = len(left) / len(last_close)
            dropouts[timestamp].append(dropout_percentage)

        # update last values
        last_participants = participants
        last_beacons = beacons

    return dropouts


# TESTS!
candidates = [('a', 0, 0), ('b', 0.5, 0.5), ('c', 1, 1)]
assert close_to_pos((0, 0), candidates) == {'a', 'b'}
