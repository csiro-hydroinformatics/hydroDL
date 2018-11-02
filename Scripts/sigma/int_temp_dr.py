import os
import rnnSMAP
from rnnSMAP import runTrainLSTM
import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.stats as stats

import imp
imp.reload(rnnSMAP)
rnnSMAP.reload()

#################################################
# intervals temporal test
doOpt = []
# doOpt.append('train')
doOpt.append('test')
doOpt.append('plotConf')
# doOpt.append('plotMap')
# doOpt.append('plotBox')
# doOpt.append('plotVS')

rootDB = rnnSMAP.kPath['DB_L3_NA']
rootOut = rnnSMAP.kPath['OutSigma_L3_NA']
drLst = np.arange(0, 1, 0.1)
drStrLst = ["%02d" % (x*100) for x in drLst]
testName = 'CONUSv4f1'
yrLst = [2015]

#################################################
if 'train' in doOpt:
    opt = rnnSMAP.classLSTM.optLSTM(
        rootDB=rootDB,
        rootOut=rootOut,
        syr=2015, eyr=2015,
        var='varLst_Forcing', varC='varConstLst_Noah',
        train='CONUSv4f1', dr=0.5, modelOpt='relu',
        model='cudnn', loss='sigma',
    )
    for k in range(0, len(drLst)):
        opt['dr'] = drLst[k]
        opt['out'] = 'CONUSv4f1_y15_Forcing_dr'+drStrLst[k]
        cudaID = k % 3
        runTrainLSTM.runCmdLine(
            opt=opt, cudaID=cudaID, screenName=opt['out'])

#################################################
if 'test' in doOpt:
    rootOut = rnnSMAP.kPath['OutSigma_L3_NA']
    rootDB = rnnSMAP.kPath['DB_L3_NA']

    predField = 'LSTM'
    targetField = 'SMAP'
    dsLst = list()
    statErrLst = list()
    statSigmaLst = list()
    statConfLst = list()
    for k in range(0, len(drLst)):
        out = 'CONUSv4f1_y15_Forcing_dr'+drStrLst[k]
        testName = testName
        ds = rnnSMAP.classDB.DatasetPost(
            rootDB=rootDB, subsetName=testName, yrLst=yrLst)
        ds.readData(var='SMAP_AM', field='SMAP')
        ds.readPred(rootOut=rootOut, out=out, drMC=100, field='LSTM')
        statErr = ds.statCalError(predField='LSTM', targetField='SMAP')
        statSigma = ds.statCalSigma(field='LSTM')
        statConf = ds.statCalConf(predField='LSTM', targetField='SMAP')

        dsLst.append(ds)
        statErrLst.append(statErr)
        statSigmaLst.append(statSigma)
        statConfLst.append(statConf)

#################################################
if 'plotConf' in doOpt:
    fig, axes = plt.subplots(ncols=2, figsize=(8, 6))

    confXLst = list()
    confMCLst = list()
    for k in range(0, len(drStrLst)):
        statConf = statConfLst[k]
        confXLst.append(statConf.conf_sigmaX)
        confMCLst.append(statConf.conf_sigmaMC)
    rnnSMAP.funPost.plotConf(confXLst, ax=axes[0], legendLst=drStrLst)
    axes[0].set_title('sigmaX')
    rnnSMAP.funPost.plotConf(confMCLst, ax=axes[1], legendLst=drStrLst)
    axes[1].set_title('sigmaMC')
    fig.show()


#################################################
if 'plotVS' in doOpt:

    strSigmaLst = ['sigmaX', 'sigmaMC']
    for iS in range(0, len(strSigmaLst)):
        fig, axes = plt.subplots(3, 3, figsize=(8, 6))
        for k in range(1, len(drStrLst)):
            statSigma = statSigmaLst[k]
            strS = strSigmaLst[iS]
            strE = 'RMSE'
            y = getattr(statErr, strE)
            x = getattr(statSigma, strS)
            ax = axes[k-1]
            rnnSMAP.funPost.plotVS(x, y, ax=ax, doRank=False)
            # rnnSMAP.funPost.plot121Line(ax)
            if iS == 0:
                ax.set_ylabel(strE)
            if iE == len(strErrLst)-1:
                ax.set_xlabel(strS)
        fig.suptitle('Temporal '+trainName)
        saveFile = os.path.join(saveFolder, 'vsPlot_'+trainName)
        fig.savefig(saveFile)
        plt.close(fig)
        y = getattr(statSigma, 'sigmaMC')
        x = getattr(statSigma, 'sigmaX')
        fig = rnnSMAP.funPost.plotVS(x, y)
        saveFile = os.path.join(saveFolder, 'vsPlotSigma_'+trainName)
        fig.savefig(saveFile)