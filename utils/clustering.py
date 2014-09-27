import collections
import itertools

from sklearn import cluster
import numpy as np

from . import data, utils, familiarity

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
    clusters_centroids is a lsit of 2d point for each frame.
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


def beacons_clustering(group, block=None):
    '''
    TODO.
    '''
    pass


def _algorithm_row_score(cents, maps, parts):
    clusters_dists = []
    for key, parts_set in maps.items():
        # per cluster, array of distances of each participant from centroid
        per_cluster_dists = [dist(parts[p], cents[key]) for p in parts_set]
        clusters_dists.append(np.mean(per_cluster_dists))
    return np.mean(clusters_dists)


def _social_row_score(cents, maps, parts):
    social_scores = []
    for _, parts_set in maps.items():
        # no social score if cluster contains less then 2 participant
        if len(parts_set) < 2:
            continue
        # list of familiarity values
        per_cluster_sociability = []
        for a, b in itertools.permutations(parts_set, 2):
            val = familiarity.p2p(a, b)
            val = val if not np.isnan(val) else familiarity.FILL_NAN
            per_cluster_sociability.append(val)
        social_scores.append(np.mean(per_cluster_sociability))
    return np.mean(social_scores)


_row_scores = {'algorithm': _algorithm_row_score, 'social': _social_row_score}


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
        score.append(f(*row))
    return score
