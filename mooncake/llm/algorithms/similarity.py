
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cosine_similarity_vec(vec_x, vec_y):
    """
    vec_x and vec_y are numeric arrays
    calculate cosine similarity
    with some safety checks
    """
    # in case dimensions aren't in required form
    vec_x = np.array(vec_x)
    vec_y = np.array(vec_y)

    def reshape_dim(vec):
        # 1d array to 2d array eg [1,2] -> [[1,2]]
        if vec.ndim == 1:
            vec = vec.reshape(1, -1)
        return vec

    vec_x = reshape_dim(vec_x)
    vec_y = reshape_dim(vec_y)
    res = cosine_similarity(vec_x, vec_y)

    return res
