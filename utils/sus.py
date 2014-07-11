'''
SUS utilities. Based on:
http://www.usabilitynet.org/trump/documents/Suschapt.doc
'''

def fillna(data):
    '''Fill NaNs in the pandas usability table  in place as instructed.'''

    return data.fillna(value=3)


def score(l):
    '''Calculate the SUS score of a single survey.'''

    total = [item_contribution(i, v) for i, v in enumerate(l)]
    return 2.5 * sum(total)

def item_contribution(index, value):
    if index % 2 == 0:
        return value - 1
    return 5 - value

if __name__ == '__main__':
    assert score([5, 4, 2, 1, 2, 3, 2, 4, 5, 2]) == 55
