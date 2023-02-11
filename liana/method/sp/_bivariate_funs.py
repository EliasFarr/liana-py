import numba as nb
import numpy as np
from scipy.stats import rankdata



@nb.njit(nb.float32(nb.float32[:], nb.float32[:], nb.float32[:], nb.float32, nb.boolean), cache=True)
def _wcorr(x, y, w, wsum, rank):
    
    if rank:
        x = np.argsort(x).argsort().astype(nb.float32)
        y = np.argsort(y).argsort().astype(nb.float32)
    
    wx = w * x
    wy = w * y
    
    numerator = wsum * sum(wx * y) - sum(wx) * sum(wy)
    
    denominator_x = wsum * sum(w * (x**2)) - sum(wx)**2
    denominator_y = wsum * sum(w * (y**2)) - sum(wy)**2
    denominator = (denominator_x * denominator_y)
    
    if (denominator == 0) or (numerator == 0):
        return 0
    
    return numerator / (denominator**0.5) ## TODO numba rounding issue?


@nb.njit(nb.float32(nb.float32[:], nb.float32[:], nb.float32[:], nb.float32, nb.int8), cache=True)
def _wcoex(x, y, w, wsum, method):
        if method == 0: # pearson
            c = _wcorr(x, y, w, wsum, False)
        elif method == 1: # spearman
            c = _wcorr(x, y, w, wsum, True)
            ## Any other method
        else: 
            raise ValueError("method not supported")
        return c


# 0 = pearson, 1 = spearman
@nb.njit(nb.float32[:,:](nb.float32[:,:], nb.float32[:,:], nb.float32[:,:], nb.float32, nb.int8), parallel=True, cache=True)
def _masked_coexpressions(x_mat, y_mat, weight, weight_thr, method):
    spot_n = x_mat.shape[0]
    xy_n = x_mat.shape[1]
    
    local_correlations = np.zeros((spot_n, xy_n), dtype=nb.float32)
    
    for i in nb.prange(spot_n):
        w = weight[i, :]
        msk = w > weight_thr
        wsum = sum(w[msk])
        
        for j in range(xy_n):
            x = x_mat[:, j][msk]
            y = y_mat[:, j][msk]
            
            local_correlations[i, j] = _wcoex(x, y, w[msk], wsum, method)
    
    return local_correlations



def _vectorized_correlations(x_mat, y_mat, dist, method="pearson"):
    """
    Vectorized implementation of weighted correlations.
    
    Note: due to the imprecision of np.sum and np.dot, the function is accurate to 5 decimal places.
    
    """
    if method not in ["pearson", "spearman"]:
        raise ValueError("method must be one of 'pearson', 'spearman'")
    
    # transpose
    x_mat, y_mat = x_mat.T, y_mat.T
    
    weight = dist.A.T
    weight_sums = np.sum(weight, axis = 0).flatten()
        
    if method=="spearman":
        x_mat = rankdata(x_mat, axis=1)
        y_mat = rankdata(y_mat, axis=1)
    
    # standard pearson
    n1 = (((x_mat * y_mat).dot(weight)) * weight_sums)
    n2 = (x_mat.dot(weight)) * (y_mat.dot(weight))
    numerator = n1 - n2
    
    denominator_x = (weight_sums * (x_mat ** 2).dot(weight)) - (x_mat.dot(weight))**2
    denominator_y = (weight_sums * (y_mat ** 2).dot(weight)) - (y_mat.dot(weight))**2
    denominator = (denominator_x * denominator_y)
    
    # numpy sum is unstable below 1e-6?
    denominator[denominator < 1e-6] = 0
    denominator = denominator ** 0.5
    
    zeros = np.zeros(numerator.shape)
    local_corrs = np.divide(numerator, denominator, out=zeros, where=denominator!=0)
    
    # fix numpy imprecision TODO related to numba rounding issue?
    local_corrs = np.clip(local_corrs, -1, 1, out=local_corrs)
    
    return local_corrs


def _vectorized_wcosine(x_mat, y_mat, dist):
    x_mat, y_mat = x_mat.T, y_mat.T    
    weight = dist.A.T
    
    xy_dot = (x_mat * y_mat).dot(weight)
    x_dot = (x_mat ** 2).dot(weight.T)
    y_dot = (y_mat ** 2).dot(weight.T)
    denominator = (x_dot * y_dot) + np.finfo(np.float32).eps
    
    return xy_dot / (denominator**0.5)


def _vectorized_jaccard(x_mat, y_mat, dist):
    # binarize
    x_mat, y_mat = x_mat > 0, y_mat > 0 ## TODO, only positive?
    # transpose
    x_mat, y_mat = x_mat.T, y_mat.T    
    weight = dist.A.T
    
    # intersect and union
    numerator = np.dot(np.minimum(x_mat, y_mat), weight)
    denominator = np.dot(np.maximum(x_mat, y_mat), weight) + np.finfo(np.float32).eps
    
    return numerator / denominator