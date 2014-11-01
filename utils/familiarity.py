import matplotlib.pyplot as plt

from . import data, utils

FILL_NAN = 0.5


@utils.memo
def load_table(group):
    group = group.upper()
    participants = getattr(data, 'GROUP_{}'.format(group))
    familiarity_columns = ['familiarity{}'.format(i) for i in participants]
    mat = (data.csv_table().loc[participants, familiarity_columns] - 1) / 4
    mat.columns = participants
    mat.index = participants
    for p in participants:
        mat.loc[p, p] = 1
    return mat


def show_map(mat, labels=None):
    plt.imshow(mat, cmap='hot', interpolation='none', vmin=0, vmax=1)
    ticks = [range(len(mat.columns)), mat.columns]
    plt.xticks(*ticks)
    plt.yticks(*ticks)
    if labels:
        plot_clusters_boundaries(labels)


def plot_clusters_boundaries(labels):
    boundaries = utils.boundaries_indices(labels)
    for b in boundaries:
        # along the x axis
        plt.plot([-0.5, len(labels) - 0.5], [b - 0.5, b - 0.5], 'b', lw=3)
        # along the y axis
        plt.plot([b - 0.5, b - 0.5], [-0.5, len(labels) - 0.5], 'b', lw=3)

@utils.memo
def p2p(from_p, to_p):
    '''
    Returns the familiarity value from participant "from_p"
    to participant "to_p".
    '''
    for mat in [load_table('A'), load_table('B')]:
        try:
            return mat.loc[from_p, to_p]
        except KeyError:
            pass
    raise KeyError(
        "Can't find familiarity from {} to {}".format(from_p, to_p)
    )
