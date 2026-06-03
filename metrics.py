import numpy as np
def mae(y_true, y_pred):

    n = min(len(y_true), len(y_pred))
    return np.mean(np.abs(y_true[:n] - y_pred[:n]))

def rmse(y_true, y_pred):
    n = min(len(y_true), len(y_pred))
    return np.sqrt(np.mean((y_true[:n] - y_pred[:n])**2))
