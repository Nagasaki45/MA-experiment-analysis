import numpy as np
from scipy import linalg


def append_one_and_stack(vecs):
    m = np.array(vecs).transpose()
    return np.vstack([m, np.ones(shape=[1, m.shape[1]])])


def list_to_chunks(l, size):
    return [l[i:i + size] for i in range(0, len(l), size)]


def solve_affine_transformation(Xs, Ys):
    '''Returns the affine transformation as A and b vector.
    Xs and Ys should be equal length lists of X and Y vectors of the same
    dimension.

    Additional info:
    http://stackoverflow.com/a/2756165/1224456
    http://en.wikipedia.org/wiki/Affine_transformation
    '''
    X = append_one_and_stack(Xs)
    Y = append_one_and_stack(Ys)
    aug_matrix = np.dot(Y, linalg.inv(X))
    A = aug_matrix[:-1, :-1]
    b = aug_matrix[:-1, -1]
    return A, b


def transform(x, A, b):
    '''Transform the x vector using the affine transformation described
    by the matrix A and the translation vector b.
    '''
    return np.dot(A, x) + b


def transform_all(x, A, b, dimension=2):
    '''Divide x into list of n-dimensional vector, apply the affine
    transformation for each of them, concatenate and return.
    '''
    Xs = list_to_chunks(x, dimension)
    Ys = [transform(x, A, b) for x in Xs]
    return [num for vec in Ys for num in vec]  # flatten


# TESTS!
# append_one_and_stack
assert np.all(append_one_and_stack([(1, 2), (3, 4)]) == \
              np.array([[1, 3], [2, 4], [1, 1]])
             )

# list_to_chunks
assert list_to_chunks([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

# solve_affine_transformation and transform
Ys = [(0, 0), (9.8, 0), (9.8, 6.3)]
a_Xs = [(77, 254), (414, 247), (598, 275)]
b_Xs = [(13, 322), (358, 321), (545, 353)]
for Xs in [a_Xs, b_Xs]:
    A, b = solve_affine_transformation(Xs, Ys)
    for x, y in zip(Xs, Ys):
        assert np.allclose(transform(x, A, b), y)

# transform_all
y = [num for vec in Ys for num in vec]  # flatten
for Xs in [a_Xs, b_Xs]:
    A, b = solve_affine_transformation(Xs, Ys)
    x = [num for vec in Xs for num in vec]  # flatten
    assert np.allclose(transform_all(x, A, b), y)
