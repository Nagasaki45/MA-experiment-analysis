import matplotlib.pyplot as plt
import numpy as np
from numpy import linalg

from .video import BENCH_RADIUS
from .animations import BENCH_COLOR
from . import utils
from . import data as d_module

boundaries = [-6, 17]
CLUSTER_RADIUS = 2
CLUSTER_PADDING = 0.5
CLUSTER_COLOR = (0.9, 0.9, 0, 0.4)


def plot_frame(group, block, timestamp, title=True, legend=True, b_size=300):

    ax = plt.gca()

    # Plot the bench as circle to the plot first
    bench = d_module.get_bench()
    bench_area = plt.Circle(bench, BENCH_RADIUS, color=BENCH_COLOR)
    ax.add_artist(bench_area)

    # Participants and beacons points
    participants = d_module.get_participants(group)
    p_points = utils.list_to_chunks(
        d_module.participants_data(group, block).loc[timestamp],
        size=2,
    )
    b_points = utils.list_to_chunks(
        d_module.beacons_data(group, block).loc[timestamp],
        size=2,
    )
    ax.scatter([p[0] for p in p_points], [p[1] for p in p_points])
    b_scat = ax.scatter([p[0] for p in b_points], [p[1] for p in b_points],
                         color='green', s=b_size, alpha=0.5)

    # Texts
    for participant, point in zip(participants, p_points):
        ax.text(point[0], point[1], participant)
    for beacon, point in enumerate(b_points, start=1):
        ax.text(point[0], point[1], 'b{}'.format(beacon))

    # modify plot properties
    ax.set_aspect(1)
    ax.axis(boundaries * 2)
    ax.invert_yaxis()
    ax.set_xlabel('timestamp: {}'.format(timestamp))
    if title:
        group_name = utils.letter_to_name(group)
        ax.set_title('{} session {}'.format(group_name, block))
    if legend:
        ax.legend([bench_area, b_scat], ['bench area', 'beacons'])


def plot_cluster(pos):
    cluster = plt.Circle(pos, CLUSTER_RADIUS, color=CLUSTER_COLOR)
    plt.gca().add_artist(cluster)


def plot_arrow(src, dst, padding=True):
    '''
    Padding can be True to calculate padding based on clusters
    radius dynamically, a float number that represent padding percentage
    or anything else for no padding
    '''
    # dst should be outside of the clusters
    dist = utils.euclidean_distance(src, dst)
    if padding is True:
        len_percantage = 1 - (CLUSTER_RADIUS + CLUSTER_PADDING) / dist
    elif isinstance(padding, float):
        len_percantage = 1 - padding
    else:
        len_percantage = 1
    dx, dy = len_percantage * (np.array(dst) - np.array(src))
    plt.arrow(src[0], src[1], dx, dy,
              head_width=0.2, head_length=0.2, fc='k', ec='k')


def plot_clusters(*poss, title_pos=None):
    for pos in poss:
        plot_cluster(pos)
        plot_arrow(title_pos, pos)

    plt.text(title_pos[0], title_pos[1] + 1, 'Clusters', size=14,
             ha='center')


def movement(last_loc, loc):
    dist = utils.euclidean_distance(last_loc, loc)
    x, y = loc[0], loc[1] - CLUSTER_RADIUS - CLUSTER_PADDING - 1.5
    plt.text(x, y, '{:.2} m/s'.format(dist), ha='center')

    # ploting direction arrow
    vec = np.array(loc) - np.array(last_loc)
    vec = vec / linalg.norm(vec)
    plt.arrow(x, y + 0.5, vec[0], vec[1],
              head_width=0.2, head_length=0.2, fc='k', ec='k')