import numpy as np

from . import utils, data

NEAR = 1  # meter

metadata = data.video_metadata()
block_mod = {'A': 0, 'B': 4}

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

    block_metadata = metadata['block {}'.format(block + block_mod[group])]
    start = block_metadata['start']
    end = block_metadata['end']
    frames = list(utils.f_range(start, end, 0.5))

    participants = data.participants_data(group).loc[frames]
    beacons = data.beacons_data(group).loc[frames]

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
