import collections
import itertools

from sklearn import cluster
import numpy as np

from . import data, utils, familiarity, beacons

dist = utils.euclidean_distance


def participants_clustering(group, block=None, *args, **kwargs):
    '''
    Using sklearn.cluster.mean_shift, cluster the participants into
    groups for each frame.

    Optional position and keyword arguments are passed as is to
    the mean_shift function.

    Returns
    =======
    (clusters_centroids, clusters_partition):
    clusters_centroids is a list of 2d point for each frame.
    clusters_partition is a map of partitions (keys are cluster index
    and values are sets of participants_numbers) for each frame.
    '''
    participants_data = data.participants_data(group, block)
    participants_nums = data.get_participants(group)
    # a list of 2d point for each frame
    clusters_centroids = []
    # a map of partitions (keys are cluster index and values
    # are sets of participants_numbers) for each frame
    clusters_partition = []
    for frame, row in participants_data.iterrows():
        pas = np.array(utils.list_to_chunks(row.values, 2))
        centroids, allocations = cluster.mean_shift(pas, *args, **kwargs)
        clusters_centroids.append(centroids)
        partition = collections.defaultdict(set)
        for participant, allocation in zip(participants_nums, allocations):
            partition[allocation].add(participant)
        clusters_partition.append(partition)

    return clusters_centroids, clusters_partition


def _bes_clustering_helper(bes, min_dist):
    # for every beacon, check if there is another beacon close to it
    for i, first in enumerate(bes):
        for second in bes[i+1:]:
            if dist(first, second) < min_dist:
                # if two like this found, remove them, create the merge
                # and call again
                bes.remove(first)
                bes.remove(second)
                bes.append(tuple(np.mean([first, second], axis=0)))
                return _bes_clustering_helper(bes, min_dist)
    return bes


def cluster_beacons_on_dance_floor(bes, min_dist=beacons.NEAR):
    '''
    Gets a list of beacons as 2d points and return centroids.
    Beacons that near each other are merged.
    '''

    # remove duplications
    as_tuples = (tuple(point) for point in bes)
    unique = set(as_tuples)
    bes = list(unique)

    return _bes_clustering_helper(bes, min_dist)


bes = [[0, 0], [0, 0]]
assert np.allclose(cluster_beacons_on_dance_floor(bes, min_dist=1),
                   [(0, 0)])

bes = [[0, 0], [1, 1]]
assert np.allclose(cluster_beacons_on_dance_floor(bes, min_dist=2),
                   [(0.5, 0.5)])

bes = [[0, 0], [1, 1], [3, 3]]
assert np.allclose(cluster_beacons_on_dance_floor(bes, min_dist=2),
                   [(3, 3), (0.5, 0.5)])


def beacons_clustering(group, block=None, min_dist=beacons.NEAR):
    '''
    TODO.
    '''

    participants_data = data.participants_data(group, block)
    beacons_data = data.beacons_data(group, block)
    participants_nums = data.get_participants(group)
    # a list of 2d point for each frame
    clusters_centroids = []
    # a map of partitions (keys are cluster index and values
    # are sets of participants_numbers) for each frame
    clusters_partition = []
    zipped = zip(participants_data.iterrows(), beacons_data.iterrows())
    filtered = ((pas, bes) for (_, pas), (_, bes) in zipped)
    f = lambda x: np.array(utils.list_to_chunks(x.values, 2))
    un_pandas = ((f(pas), f(bes)) for  pas, bes in filtered)
    for pas, bes in list(un_pandas):
        centroids = cluster_beacons_on_dance_floor(bes, min_dist)
        clusters_centroids.append(centroids)
        partition = collections.defaultdict(set)
        for p_index, p_point in enumerate(pas):
            p_num = participants_nums[p_index]
            for i, c in enumerate(centroids):
                if dist(p_point, c) < min_dist:
                    partition[i].add(p_num)
                    break  # participant belog to first centroid that match
        clusters_partition.append(partition)

    return clusters_centroids, clusters_partition


def _algorithm_row_score(cents, maps, parts):
    clusters_dists = {}  # key is part num, val is dist
    for key, parts_set in maps.items():
        for p in parts_set:
            clusters_dists[p] = dist(parts[p], cents[key])
    return clusters_dists


def _social_row_score(cents, maps, parts):
    social_scores = {}
    for _, parts_set in maps.items():
        for p in parts_set:
            # list of social familiarities of participant p
            p_socialities = []
            for q in parts_set:
                if p == q:
                    continue
                p_socialities.append(familiarity.p2p(p, q))
            p_sociality = np.mean(p_socialities)
            if not np.isnan(p_sociality):
                social_scores[p] = p_sociality
            else:
                social_scores[p] = 0
    return social_scores


_row_scores = {'algorithm': _algorithm_row_score,
               'social': _social_row_score}


def score(kind, centroids, mapings, participants):
    '''
    Calculate one of two kinds of scores: algorithm score or social
    score for participant based or beacon based clustering.
    
    Parameters
    ==========
        kind (str): 'algorithm' or 'social'.
        centroids (list): list of lists of 2d points of cluster centroids.
        mapings (list): list of dicts that map cluster number to set
                        of participants numbers.
        participants (list): list of dicts that map participant number
                             to 2d positioning point.

    Returns
    =======
    (list): a vector of scores (max length is number of frames).
    '''
    score = []
    f = _row_scores[kind]
    participants = utils.participants_as_list_of_dicts(participants)
    for row in zip(centroids, mapings, participants):
        as_dict = f(*row)
        # add 0 as the score of participants that are not in the returned dict
        parts = row[2]
        for p in parts:
            if p not in as_dict:
                as_dict[p] = 0
        score_vals = [val for key, val in sorted(as_dict.items())]
        score.append(score_vals)
    try:
        return np.mean(score, axis=0)
    except:
        score = np.array(score)
        print(score.shape, score[0])
        raise
