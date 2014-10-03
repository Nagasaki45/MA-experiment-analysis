import concurrent.futures

from matplotlib import animation
import matplotlib.pyplot as plt

from . import data as d_module
from . import utils
from . import video


def get_points(data, timestamp, num_of_participants):
    '''
    Extract and return the participants and beacons 2d points.
    '''
    points = utils.list_to_chunks(data.loc[timestamp], size=2)
    return points[:num_of_participants], points[num_of_participants:]


def update_scatter(timestamp, data, p_scat, b_scat, texts, xlabel,
                   num_of_participants):
    p_points, b_points = get_points(data, timestamp, num_of_participants)
    p_scat.set_offsets(p_points)
    b_scat.set_offsets(b_points)
    for point, text in zip(p_points + b_points, texts):
        text.set_position([point[0], point[1]])
    xlabel.set_text('timestamp: {}'.format(timestamp))

        
def animate(group, block, length=None, offset=None):
    # arrange the data for the animation
    block_num = block + 4 if group == 'B' else block
    metadata = d_module.video_metadata()
    start = metadata['block {}'.format(block_num)]['start']
    if offset:
        start += offset
    if length:
        end = start + length
    else:
        end = metadata['block {}'.format(block_num)]['end']
    frames = list(utils.f_range(start, end, 0.5))
    data = d_module.groups[group].loc[frames]
    
    # plot init
    fig = plt.figure(figsize=(5, 5))

    # add bench as circle to the plot
    bench = d_module.get_bench()
    bench_area = plt.Circle(bench.pos, bench.RADIUS, color=bench.COLOR)
    fig.gca().add_artist(bench_area)

    # animation init
    participants = d_module.get_participants(group)
    p_points, b_points = get_points(data, start, len(participants))
    texts = []
    for participant, point in zip(participants, p_points):
        texts.append(plt.text(point[0], point[1], participant))
    for beacon, point in enumerate(b_points, start=1):
        texts.append(plt.text(point[0], point[1], 'b{}'.format(beacon)))
    p_scat = plt.scatter([p[0] for p in p_points], [p[1] for p in p_points])
    b_scat = plt.scatter([p[0] for p in b_points], [p[1] for p in b_points],
                         color='green', s=100, alpha=0.2)
    xlabel = plt.xlabel('')
    
    # modify plot properties
    plt.title('Group {} block {}'.format(group, block))
    plt.axis([d_module.lower, d_module.upper] * 2)
    plt.gca().invert_yaxis()
    plt.legend([bench_area], ['bench area'])

    return animation.FuncAnimation(
        fig,
        update_scatter,
        frames=frames,
        fargs=(data, p_scat, b_scat, texts, xlabel, len(participants))
    )
