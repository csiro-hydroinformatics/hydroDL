
import numpy as np
import scipy


class statError(object):
    def __init__(self, *, pred, target):
        ngrid, nt = pred.shape
        # RMSE
        self.RMSE = np.sqrt(np.nanmean((pred-target)**2, axis=1))
        # ubRMSE
        predMean = np.tile(np.nanmean(pred, axis=1), (nt, 1)).transpose()
        targetMean = np.tile(np.nanmean(target, axis=1), (nt, 1)).transpose()
        predAnom = pred-predMean
        targetAnom = target-targetMean
        self.ubRMSE = np.sqrt(np.nanmean((predAnom-targetAnom)**2, axis=1))
        # rho
        rho = np.full(ngrid, np.nan)
        for k in range(0, ngrid):
            x = pred[k, :]
            y = target[k, :]
            ind = np.where(np.logical_and(~np.isnan(x), ~np.isnan(y)))[0]
            if ind.shape[0]>0:
                xx = x[ind]
                yy = y[ind]
                rho[k] = scipy.stats.pearsonr(xx, yy)[0]
        self.rho = rho


class statSigma(object):
    def __init__(self, *, dataMC, dataSigma):
        self.sigmaMC_mat = np.std(dataMC, axis=2)
        self.sigmaX_mat = dataSigma
        self.sigmaMC = np.nanmean(self.sigmaMC_mat, axis=1)
        self.sigmaX = np.nanmean(self.sigmaX_mat, axis=1)
        self.sigma_mat = np.sqrt(self.sigmaMC_mat**2+self.sigmaX_mat**2)
        self.sigma = np.nanmean(self.sigma_mat, axis=1)