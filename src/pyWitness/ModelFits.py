from .DataRaw import DataRaw as _DataRaw
from .Utils import getColorOfLabeledFromGca as _getColorofLabeledFromGca

import numpy as _np
import pandas as _pandas
import copy as _copy
from scipy import integrate as _integrate
from scipy import optimize as _optimize
from scipy import interpolate as _interpolate
from scipy.stats import norm as _norm
from scipy.stats import chi2 as _chi2
import scipy.special as _sc
import matplotlib.pyplot as _plt
import random as _rand
import math as _math
# from numba import jit
import time as _time


# @jit(nopython=True)
def normpdf(x, mean, sigma):
    stp = _np.sqrt(2 * _np.pi)
    return 1.0 / (sigma * stp) * _np.exp(-0.5 * ((x - mean) / sigma) ** 2)


def normcdf(x, mean, sigma):
    z = (x - mean) / sigma

    return _sc.ndtr(z)


def truncatedMean(mu, sigma, x):
    beta = (x - mu) / sigma
    Z = normpdf(beta, 0, 1) / normcdf(beta, 0, 1)
    return mu - sigma * Z


def truncatedVar(mu, sigma, x):
    beta = (x - mu) / sigma
    Z = normpdf(beta, 0, 1) / normcdf(beta, 0, 1)
    return sigma ** 2 * (1. - Z * beta - Z ** 2)


class Parameter(object):

    def __init__(self, name, value, fixed=False):
        self.name = name
        self.__value = value
        self.__fixed = fixed
        self.other = None

    @property
    def value(self):
        if not self.other:
            return self.__value
        else:
            return self.other.value

    @value.setter
    def value(self, value):
        if not self.other:
            self.__value = value
        else:
            self.other.value = value

    @property
    def fixed(self):
        return self.__fixed

    @fixed.setter
    def fixed(self, fixed):
        self.__fixed = fixed

    def set_equal(self, other):
        self.other = other
        self.fixed = True

    def unset_equal(self):
        self.other = None
        self.fixed = False

    def __eq__(self, other):
        return self.value == other.value

    def __float__(self):
        return float(self.value)

    def __copy__(self):
        new = Parameter(0)
        new.value = self.value
        return new

    def __repr__(self):

        if self.fixed:
            fixStr = "fixed"

            if self.other:
                fixStr = fixStr + " " + self.other.name

        else:
            fixStr = "free"

        return self.name + " " + ('%.3f' % self.value) + " (" + fixStr + ")"


class ModelFit(object):
    def __init__(self, processedData, debug=False, integrationSigma=6, chi2Var='expected'):

        self.debugIoPadSize = 60

        self.fit_parameters = None
        self.fit_parameters_bootstrap = []

        self.set_equal_variance = False
        self.set_unequal_variance = False

        # check chi2Var variable
        if chi2Var != 'expected' and chi2Var != 'observed':
            print("chi2Var should be 'expected'|'observed'")

        self.processedData = processedData
        self.numberConditions = processedData.numberConditions
        self.lineupSize = processedData.lineupSize
        self.numberTPLineups = processedData.numberTPLineups
        self.numberTALineups = processedData.numberTALineups
        self.pred_rates = processedData.data_rates.copy()  # copy the processed data rates for a prediction data frame
        self.pred_rates.iloc[:, :] = 0.0
        self.iteration = 0
        self.debug = debug
        self.integrationSigma = integrationSigma
        self.chi2Var = chi2Var

        # parameters 
        self.parameterNames = []
        self.lureMean = self.addParameter("lureMean", 0.0)
        self.lureSigma = self.addParameter("lureSigma", 1.0)
        self.targetMean = self.addParameter("targetMean", 1.0)
        self.targetSigma = self.addParameter("targetSigma", 1.0)
        self.lureBetweenSigma = self.addParameter("lureBetweenSigma", 0.0)
        self.targetBetweenSigma = self.addParameter("targetBetweenSigma", 0.0)

        thresholds = _np.linspace(self.targetMean.value, self.targetMean.value + self.targetSigma.value,
                                  self.numberConditions)
        self.thresholds = []
        for i in range(0, self.numberConditions, 1):
            self.thresholds.append(self.addParameter("c" + str(i + 1), thresholds[i]))

        self.calculateWithinSigmas()

    def addParameter(self, name, value, fixed=False):
        self.parameterNames.append(name)
        p = Parameter(name, value, fixed)
        setattr(self, name, p)
        return p

    def freeParameterList(self):
        freeParams = []
        for p in self.parameterNames:
            p = getattr(self, p)
            if not p.fixed:
                freeParams.append(p)

        return freeParams

    def resetParameters(self):
        self.lureMean.value = 0.0
        self.lureSigma.value = 1.0
        self.targetMean.value = 1.0
        self.targetSigma.value = 1.0
        self.lureBetweenSigma.value = 0.3
        self.targetBetweenSigma.value = 0.3

        thresholds = _np.linspace(self.targetMean.value, self.targetMean.value + self.targetSigma.value,
                                  self.numberConditions)
        for i in range(0, self.numberConditions, 1):
            getattr(self, "c" + str(i + 1)).value = thresholds[i]

    def printParameters(self):
        for p in self.parameterNames:
            p = getattr(self, p)
            print('ModelFit.printParameters> ', p)


    def setDebug(self, debug = True):
        self.debug = debug

    def setEqualVariance(self):
        self.set_equal_variance = True
        self.lureMean.value = 0.0
        self.lureMean.fixed = True
        self.lureSigma.set_equal(self.targetSigma)
        self.targetMean.value = 1.0
        self.targetSigma.value = 1.0
        self.targetSigma.fixed = True
        self.lureBetweenSigma.set_equal(self.targetBetweenSigma)
        # self.targetBetweenSigma.fixed = True
        self.targetBetweenSigma.value = 0.1

    def setUnequalVariance(self):
        self.set_unequal_variance = True
        self.lureMean.value = 0.0
        self.lureMean.fixed = True
        self.lureSigma.value = 1.0
        self.lureSigma.fixed = True
        self.targetMean.value = 1.0
        self.targetSigma.value = 1.0
        self.targetSigma.fixed = False
        self.lureBetweenSigma.set_equal(self.targetBetweenSigma)
        self.targetBetweenSigma.fixed = False
        self.targetBetweenSigma.value = 0.1

    def setParameterEstimates(self):

        self.targetMean.value = self.processedData.mu_pred
        if self.set_unequal_variance:
            self.targetSigma.value = self.processedData.sigma_pred

        for i in range(0, len(self.processedData.c_pred), 1):
            c_pred = _np.flip(self.processedData.c_pred.values)[i]
            if c_pred != -_np.inf:
                self.__getattribute__("c" + str(i + 1)).value = _np.flip(self.processedData.c_pred.values)[i]
            else:
                self.__getattribute__("c" + str(i + 1)).value = -10.0
                self.__getattribute__("c" + str(i + 1)).fixed = True

    def calculateWithinSigmas(self):
        self.lureWithinSigma = _np.sqrt(self.lureSigma.value ** 2 - self.lureBetweenSigma.value ** 2)
        self.targetWithinSigma = _np.sqrt(self.targetSigma.value ** 2 - self.targetBetweenSigma.value ** 2)

    def calculateFrequencyForCriterion(self, c1, c2):
        pred_c1 = self.calculateCumulativeFrequencyForCriterion(c1)
        pred_c2 = self.calculateCumulativeFrequencyForCriterion(c2)

        return pred_c2 - pred_c1

    def calculateFrequenciesForAllCriteria(self):
        pred_tafid_array = []
        pred_tpsid_array = []
        pred_tpfid_array = []

        for i in range(0, len(self.thresholds), 1):
            if i < len(self.thresholds) - 1:
                [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateFrequencyForCriterion(self.thresholds[i + 1],
                                                                                           self.thresholds[i])
            else:
                [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(self.thresholds[i])

            pred_tafid_array.append(pred_tafid)
            pred_tpsid_array.append(pred_tpsid)
            pred_tpfid_array.append(pred_tpfid)

        pred_tafid_array = _np.array(pred_tafid_array)
        pred_tasid_array = pred_tafid_array / self.lineupSize
        pred_tpsid_array = _np.array(pred_tpsid_array)
        pred_tpfid_array = _np.array(pred_tpfid_array)

        pred_tarid = self.numberTALineups - pred_tafid_array.sum()
        pred_tprid = self.numberTPLineups - pred_tpsid_array.sum() - pred_tpfid_array.sum()

        if self.debug:
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tafid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tafid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tasid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tasid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tarid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tarid)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tpfid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tpfid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tpsid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tpsid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tprid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tprid)

        return [pred_tarid,
                pred_tasid_array,
                pred_tafid_array,
                pred_tprid,
                pred_tpsid_array,
                pred_tpfid_array]

    @property
    def chi2(self):

        debug = self.debug
        self.debug = False

        freeParams = self.freeParameterList()
        p0 = []
        for p in freeParams:
            p0.append(p.value)
        chi2 = self.calculateChi2(p0)

        self.debug = debug
        return chi2

    @property
    def numberFreeParameters(self):
        iFreeParams = 0
        freeParams = self.freeParameterList()
        for p in freeParams:
            iFreeParams = iFreeParams + 1

        return iFreeParams

    @property
    def numberDataPoints(self):
        if self.lineupSize == 1:
            return 2 * self.numberConditions
        else:
            return 3 * self.numberConditions

    @property
    def numberDegreesOfFreedom(self):
        return self.numberDataPoints - self.numberFreeParameters

    @property
    def chi2PerNDF(self):
        return self.chi2 / self.numberDegreesOfFreedom

    def generateTALineup(self):
        memoryStrength = _np.random.normal(self.lureMean, self.targetMean, self.lineupSize)

        return [-1, memoryStrength]

    def generateTPLineup(self):
        memoryStrength = _np.random.normal(self.lureMean, self.targetMean, self.lineupSize)
        lineupLocation = int(_math.floor(_np.random.rand() * self.lineupSize))
        targetStrength = _np.random.normal(self.targetMean, self.targetSigma, 1)

        memoryStrength[lineupLocation] = targetStrength
        return [lineupLocation, memoryStrength]

    def generateFrequenciesForAllCriteria(self, mcScale=20):
        totalLineups = self.numberTALineups + self.numberTPLineups

        fractionTALineups = self.numberTALineups
        totalMCLineups = mcScale * totalLineups

        pred_tafid_array = _np.zeros(self.numberConditions)
        pred_tpsid_array = _np.zeros(self.numberConditions)
        pred_tpfid_array = _np.zeros(self.numberConditions)

        for i in range(totalMCLineups):
            r = _rand.random()
            if r < fractionTALineups:
                memoryStrength = self.generateTALineup()
            else:
                memoryStrength = self.generateTPLineup()

            self.monteCarloDecision(pred_tafid_array,
                                    pred_tpsid_array,
                                    pred_tpfid_array,
                                    memoryStrength)

        pred_tasid_array = pred_tafid_array / self.lineupSize
        pred_tarid = self.numberTALineups - pred_tafid_array.sum()
        pred_tprid = self.numberTPLineups - pred_tpsid_array.sum() - pred_tpfid_array.sum()

        return [pred_tarid,
                pred_tasid_array,
                pred_tafid_array,
                pred_tprid,
                pred_tpsid_array,
                pred_tpfid_array]

    def monteCarloDecision(self, pred_tafid_array, pred_tpsid_array, pred_tpfid_array, memoryStrength):
        pass

    def generateRawData(self, nGenParticipants=10000, tasid=False, debug=False):
        if self.lineupSize != 1:
            return self.generateRawDataLineup(nGenParticipants=nGenParticipants, tasid=tasid, debug=debug)
        else:
            return self.generateRawDataShowup(nGenParticipants=nGenParticipants, tasid=tasid, debug=debug)

    def generateRawDataLineup(self, nGenParticipants=10000, tasid=False, debug=False):
        [pred_tarid,
         pred_tasid_array,
         pred_tafid_array,
         pred_tprid,
         pred_tpsid_array,
         pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        nParticipants = pred_tarid + pred_tafid_array.sum() + pred_tprid + pred_tpsid_array.sum() + pred_tpfid_array.sum()

        if nGenParticipants == -1:
            nGenParticipants = nParticipants

        numberConfidence = len(pred_tafid_array)

        numberTALineups = pred_tarid + pred_tafid_array.sum()
        numberTPLineups = pred_tprid + pred_tpfid_array.sum() + pred_tpsid_array.sum()

        prob_tarid = pred_tarid / numberTALineups
        prob_tafid = pred_tafid_array / numberTALineups

        prob_tprid = pred_tprid / numberTPLineups
        prob_tpfid = pred_tpfid_array / numberTPLineups
        prob_tpsid = pred_tpsid_array / numberTPLineups

        prob_ta = _np.zeros(2 * numberConfidence + 1)
        prob_tp = _np.zeros(2 * numberConfidence + 1)

        prob_ta[0] = prob_tarid
        prob_ta[1:(1 + numberConfidence)] = prob_tafid
        prob_ta[(1 + numberConfidence):] = 0.0

        prob_tp[0] = prob_tprid
        prob_tp[1:(1 + numberConfidence)] = prob_tpfid
        prob_tp[(1 + numberConfidence):] = prob_tpsid

        genTALineups = numberTALineups / (numberTALineups + numberTPLineups) * nGenParticipants
        genTPLineups = numberTPLineups / (numberTALineups + numberTPLineups) * nGenParticipants

        gen_ta = _np.random.multinomial(genTALineups, prob_ta)
        gen_tp = _np.random.multinomial(genTPLineups, prob_tp)

        gen_tarid = gen_ta[0]
        gen_tafid_array = gen_ta[1:(1 + numberConfidence)]
        gen_tasid_array = gen_ta[(1 + numberConfidence):]
        gen_tprid = gen_tp[0]
        gen_tpfid_array = gen_tp[1:(1 + numberConfidence)]
        gen_tpsid_array = gen_tp[(1 + numberConfidence):]

        if tasid:
            gen_tafid_array = gen_tafid_array - gen_tasid_array

        if debug:
            print('ModelFit.generateRawDataShowup> gen_tafid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tafid_array)
            print('ModelFit.generateRawDataShowup> gen_tasid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tasid_array)
            print('ModelFit.generateRawDataShowup> gen_tarid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tarid)

            print('ModelFit.generateRawDataShowup> gen_tpfid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tpfid_array)
            print('ModelFit.generateRawDataShowup> gen_tpsid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tpsid_array)
            print('ModelFit.generateRawDataShowup> gen_tprid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tprid)

        dr = _DataRaw('')

        # generate TA rejections
        dr.addParticipant(participantId=None,
                          lineupSize=self.processedData.lineupSize,
                          targetLineup="targetAbsent",
                          responseType="rejectId",
                          confidence=1,
                          n=int(gen_tarid))

        # generate TP rejections
        dr.addParticipant(participantId=None,
                          lineupSize=self.processedData.lineupSize,
                          targetLineup="targetPresent",
                          responseType="rejectId",
                          confidence=1,
                          n=int(gen_tprid))

        # generate TA filler
        for i in range(0, len(gen_tafid_array)):
            dr.addParticipant(participantId=None,
                              lineupSize=self.processedData.lineupSize,
                              targetLineup="targetAbsent",
                              responseType="fillerId",
                              confidence=i + 1,  # this should be confidence from DataRaw.
                              n=int(gen_tafid_array[i]))

        # generate TA suspect
        if tasid:
            for i in range(0, len(gen_tasid_array)):
                dr.addParticipant(participantId=None,
                                  lineupSize=self.processedData.lineupSize,
                                  targetLineup="targetAbsent",
                                  responseType="suspectId",
                                  confidence=i + 1,  # this should be confidence from DataRaw.
                                  n=int(gen_tasid_array[i]))

        # generate TP filler
        for i in range(0, len(gen_tpfid_array)):
            dr.addParticipant(participantId=None,
                              lineupSize=self.processedData.lineupSize,
                              targetLineup="targetPresent",
                              responseType="fillerId",
                              confidence=i + 1,  # this should be confidence from DataRaw.
                              n=int(gen_tpfid_array[i]))

        # generate TP suspect
        for i in range(0, len(gen_tpsid_array)):
            dr.addParticipant(participantId=None,
                              lineupSize=self.processedData.lineupSize,
                              targetLineup="targetPresent",
                              responseType="suspectId",
                              confidence=i + 1,  # this should be confidence from DataRaw.
                              n=int(gen_tpsid_array[i]))

        return dr

    def generateRawDataShowup(self, nGenParticipants=10000, tasid=False, debug=False):
        [pred_tarid,
         pred_tasid_array,
         pred_tafid_array,
         pred_tprid,
         pred_tpsid_array,
         pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        numberTALineups = pred_tasid_array.sum()
        numberTPLineups = pred_tpsid_array.sum()

        if nGenParticipants == -1:
            nGenParticipants = numberTALineups + numberTPLineups

        genTALineups = numberTALineups / (numberTALineups + numberTPLineups) * nGenParticipants
        genTPLineups = numberTPLineups / (numberTALineups + numberTPLineups) * nGenParticipants

        gen_tasid_array = _np.random.multinomial(genTALineups, pred_tasid_array / numberTALineups)
        gen_tpsid_array = _np.random.multinomial(genTPLineups, pred_tpsid_array / numberTPLineups)

        # print(gen_tasid_array, gen_tpsid_array)

        if debug:
            print('ModelFit.generateRawDataShowup> pred_tasid'.ljust(self.debugIoPadSize, ' ') + ":", pred_tasid_array)
            print('ModelFit.generateRawDataShowup> pred_tpsid'.ljust(self.debugIoPadSize, ' ') + ":", pred_tpsid_array)

            print('ModelFit.generateRawDataShowup> gen_tasid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tasid_array)
            print('ModelFit.generateRawDataShowup> gen_tpsid'.ljust(self.debugIoPadSize, ' ') + ":", gen_tpsid_array)

        dr = _DataRaw('')

        # confidence = self.processedData.data_rates.columns.get_level_values(self.processedData.dependentVariable,'central').values[-1::-1]
        confidence = self.processedData.data_rates.columns.get_level_values(
            self.processedData.dependentVariable).values[-1::-1]
        # target absent
        for i in range(0, len(gen_tasid_array)):

            if i <= len(gen_tasid_array) / 2.0:
                responseType = "rejectId"
            else:
                responseType = "suspectId"

            dr.addParticipant(participantId=None,
                              lineupSize=self.processedData.lineupSize,
                              targetLineup="targetAbsent",
                              responseType=responseType,
                              confidence=confidence[i],
                              n=int(_np.round(gen_tasid_array[i])))

        # target present
        for i in range(0, len(gen_tpsid_array)):
            if i <= len(gen_tasid_array) / 2:
                responseType = "rejectId"
            else:
                responseType = "suspectId"

            dr.addParticipant(participantId=None,
                              lineupSize=self.processedData.lineupSize,
                              targetLineup="targetPresent",
                              responseType=responseType,
                              confidence=confidence[i],
                              n=int(_np.round(gen_tpsid_array[i])))

        return dr

    def calculateChi2(self, params):

        freeParams = self.freeParameterList()

        for i in range(0, len(freeParams), 1):
            p = freeParams[i]
            p.value = params[i]

        if self.debug:
            print('------------------------------------------------------------------------------')
            print('ModelFit.calculateChi2> chi2 valuation number'.ljust(self.debugIoPadSize, ' ') + ":", self.iteration)
            print('ModelFit.calculateChi2> params               '.ljust(self.debugIoPadSize, ' ') + ":", params)

        [pred_tarid, pred_tasid_array, pred_tafid_array,
         pred_tprid, pred_tpsid_array, pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        if self.lineupSize != 1:
            chi2_tafid = 0
            chi2_tpsid = 0
            chi2_tpfid = 0
            chi2_tarid = 0
            chi2_tprid = 0

            for i in range(0, self.numberConditions):
                if self.chi2Var == "observed":
                    var_tafid = self.processedData.data_pivot.loc['targetAbsent', 'fillerId'][i]
                    var_tpsid = self.processedData.data_pivot.loc['targetPresent', 'suspectId'][i]
                    var_tpfid = self.processedData.data_pivot.loc['targetPresent', 'fillerId'][i]
                elif self.chi2Var == "expected":
                    var_tafid = abs(pred_tafid_array[i])
                    var_tpsid = abs(pred_tpsid_array[i])
                    var_tpfid = abs(pred_tpfid_array[i])

                chi2_tafid = chi2_tafid + (
                            self.processedData.data_pivot.loc['targetAbsent', 'fillerId'][i] - pred_tafid_array[
                        i]) ** 2 / var_tafid
                chi2_tpsid = chi2_tpsid + (
                            self.processedData.data_pivot.loc['targetPresent', 'suspectId'][i] - pred_tpsid_array[
                        i]) ** 2 / var_tpsid
                chi2_tpfid = chi2_tpfid + (
                            self.processedData.data_pivot.loc['targetPresent', 'fillerId'][i] - pred_tpfid_array[
                        i]) ** 2 / var_tpfid

            if self.chi2Var == "observed":
                var_tarid = pred_tarid
                var_tprid = pred_tprid
            elif self.chi2Var == "expected":
                var_tarid = self.processedData.data_pivot.loc['targetAbsent', 'rejectId'].sum()
                var_tprid = self.processedData.data_pivot.loc['targetPresent', 'rejectId'].sum()

            chi2_tarid = (self.processedData.data_pivot.loc[
                              'targetAbsent', 'rejectId'].sum() - pred_tarid) ** 2 / var_tarid
            chi2_tprid = (self.processedData.data_pivot.loc[
                              'targetPresent', 'rejectId'].sum() - pred_tprid) ** 2 / var_tprid

            chi2 = chi2_tafid + chi2_tpsid + chi2_tpfid + chi2_tarid + chi2_tprid

            # Criterion flip guard
            for i in range(0, len(self.thresholds) - 1):
                if self.thresholds[i].value > self.thresholds[i + 1].value:
                    chi2 = chi2 + 10000

            if self.debug:
                print('ModelFit.calculateChi2> chi2 tafid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tafid)
                print('ModelFit.calculateChi2> chi2 tarid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tarid)
                print('ModelFit.calculateChi2> chi2 tpfid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tpfid)
                print('ModelFit.calculateChi2> chi2 tpsid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tpsid)
                print('ModelFit.calculateChi2> chi2 tprid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tprid)
                print('ModelFit.calculateChi2> chi2 total'.ljust(self.debugIoPadSize, ' ') + ":", chi2)

        else:
            chi2_ta = 0
            chi2_tp = 0

            for i in range(0, self.numberConditions):
                if self.chi2Var == "observed":
                    var_ta = abs(self.processedData.data_pivot.loc['targetAbsent', 'suspectId'][i] +
                                 self.processedData.data_pivot.loc['targetAbsent', 'rejectId'][i])
                    var_tp = abs(self.processedData.data_pivot.loc['targetPresent', 'suspectId'][i] +
                                 self.processedData.data_pivot.loc['targetPresent', 'rejectId'][i])
                elif self.chi2Var == "expected":
                    var_ta = abs(pred_tasid_array[i])
                    var_tp = abs(pred_tpsid_array[i])

                chi2_ta = chi2_ta + (self.processedData.data_pivot.loc['targetAbsent', 'suspectId'][i] +
                                     self.processedData.data_pivot.loc['targetAbsent', 'rejectId'][i] -
                                     pred_tasid_array[i]) ** 2 / var_ta
                chi2_tp = chi2_tp + (self.processedData.data_pivot.loc['targetPresent', 'suspectId'][i] +
                                     self.processedData.data_pivot.loc['targetPresent', 'rejectId'][i] -
                                     pred_tpsid_array[i]) ** 2 / var_tp

            chi2 = chi2_ta + chi2_tp

            # Criterion flip guard
            for i in range(0, len(self.thresholds) - 1):
                if self.thresholds[i].value > self.thresholds[i + 1].value:
                    chi2 = chi2 + 10000

            if self.debug:
                print('ModelFit.calculateChi2> chi2 ta    '.ljust(self.debugIoPadSize, ' ') + ":", chi2_ta)
                print('ModelFit.calculateChi2> chi2 tp    '.ljust(self.debugIoPadSize, ' ') + ":", chi2_tp)
                print('ModelFit.calculateChi2> chi2 total '.ljust(self.debugIoPadSize, ' ') + ":", chi2)

        self.iteration = self.iteration + 1

        try:
            self.chi2_array.append(chi2)
        except:
            pass
        # if freeParams[0].value < freeParams[1].value/2 :
        #    chi2 = chi2 + 100

        return chi2

    def fit(self, maxiter=5000, method="Nelder-Mead", resetParameters=False):

        if resetParameters:
            self.resetParameters()

        freeParams = self.freeParameterList()
        p0 = []
        for p in freeParams:
            p0.append(p.value)

        if self.debug:
            print('fit> starting parameters'.ljust(self.debugIoPadSize, ' ') + ":", p0)

        self.iteration = 0

        def chiSquared(x):
            return self.calculateChi2(x)

        self.chi2_array = []

        tStart = _time.perf_counter()
        opt = _optimize.minimize(chiSquared, p0, method=method, options={"maxiter": maxiter})
        tEnd = _time.perf_counter()

        if self.debug:
            print(opt)

        # Store fit output
        self.numberIterations = opt["nit"]
        self.fitStatus = opt["message"]
        self.timeDiff = tEnd - tStart
        self.pValue = 1 - _chi2.cdf(self.chi2, self.numberDegreesOfFreedom)

        print("fit iterations", self.numberIterations)
        print("fit status    ", self.fitStatus)
        print("fit time      ", self.timeDiff)
        print("fit chi2      ", self.chi2)
        print("fit ndf       ", self.numberDegreesOfFreedom)
        print("fit chi2/ndf  ", self.chi2PerNDF)
        print("fit p-value   ", self.pValue)

        # Post fit calculations
        self.calculateD()

        # self.thresholds = opt['x'][0:self.numberConditions]

    def saveParametersToTable(self, name="temp"):

        if self.fit_parameters is None:
            columns = _copy.copy(self.parameterNames)
            columns.insert(0, "name")
            columns.extend(["numberIterations", "chi2", "fitStatus", "d", "p-value"])
            self.fit_parameters = _pandas.DataFrame(columns=columns, dtype=float)

        values = {}

        values["name"] = name
        for p in self.parameterNames:
            values[p] = p = getattr(self, p).value

        try:
            values["numberIterations"] = self.numberIterations
            values["chi2"] = self.chi2
            values["fitStatus"] = self.fitStatus
            values["d"] = self.d
            values["p-value"] = self.pValue
        except:
            pass

        print(values)

        self.fit_parameters = self.fit_parameters.append(values, ignore_index=True)

    def printParameterTable(self):
        print(self.fit_parameters)

    def writeParameterTableCsv(self, fileName="fitParameters_temp.csv"):
        self.fit_parameters.to_csv(fileName)

    def setParametersFromFile(self, fileName="fitParameters_temp.csv", fitName="temp", replace=False):

        fitParameters = _pandas.read_csv(fileName)

        fitParametersSeries = fitParameters.loc[fitParameters['name'] == fitName]

        self.setParametersFromSeries(fitParametersSeries)
        self.saveParametersToTable(fitName + "_Loaded")

        if replace:
            self.fit_paramters = fitParameters

    def setParametersFromSeries(self, series):

        # loop of series keys
        for k in series.keys():

            if k == "chi2":
                continue

            try:
                attrib = getattr(self, k)
                if type(attrib) == Parameter:
                    attrib.value = series[k]
            except AttributeError:
                pass

    def calculateConfidenceBootstrap(self, nBootstraps=200):
        self.debug = False

        chi2 = []
        c1 = []

        # TODO bootstrapping with conditions
        for i in range(0, nBootstraps, 1):
            dr = self.processedData.dataRaw.resampleWithReplacement()
            dp = dr.process()
            self.processedData = dp
            self.resetParameters()
            self.targetBetweenSigma.value = 0.3

            self.numberConditions = dp.numberConditions
            self.lineupSize = dp.lineupSize
            self.numberTPLineups = dp.numberTPLineups
            self.numberTALineups = dp.numberTALineups
            self.pred_rates = dp.data_rates.copy()  # copy the processed data rates for a prediction data frame
            self.pred_rates.iloc[:, :] = 0.0
            self.iteration = 0

            self.fit()
            self.printParameters()

            self.fit_parameters_bootstrap.append([getattr(self,n).value for n in self.parameterNames])

            chi2.append(self.chi2)
            c1.append(self.c1.value)

        # TODO fix output
        _pandas.DataFrame(self.fit_parameters_bootstrap).to_csv("geoff.csv")

        return [chi2, c1]

    def calculateD(self):
        self.d = (self.targetMean.value - self.lureMean.value) / _np.sqrt(
            (self.targetSigma.value ** 2 + self.lureSigma.value ** 2) / 2.0)

    def plotModel(self, xlow=-5, xhigh=5, baseRate = 0.5):
        x = _np.linspace(xlow, xhigh, 200)
        target = _norm.pdf(x, self.targetMean.value, self.targetSigma.value)
        lure = _norm.pdf(x, self.lureMean.value, self.lureSigma.value)*(1/baseRate-1)
        ratio = _np.trapz(target,x)/(_np.trapz(target,x)+_np.trapz(lure,x))


        _plt.subplot(2, 1, 1)
        _plt.plot(x, target, label="Target")
        _plt.plot(x, lure, label="Lure")
        _plt.ylabel("Probability density")

        # lure mean
        _plt.axvline(self.lureMean.value, 0, 0.8, linestyle='-.', color='#000000')
        _plt.text(self.lureMean.value, target.max() * 1.1, "$\mu_l$", ha='center')
        # lure sigma
        _plt.axvline(self.lureMean.value - self.lureSigma.value, 0, 0.8, linestyle='-.', color='#000000')
        _plt.text(self.lureMean.value - self.lureSigma.value / 2, target.max() * 1.1 / 2, "$\sigma_l$", ha='center')
        _plt.arrow(self.lureMean.value, target.max() * 1.1 / 3,
                   -self.lureSigma.value, 0,
                   length_includes_head=True, head_length=1 / 6, head_width=0.025,
                   capstyle='butt', shape='full')

        # target mean
        _plt.axvline(self.targetMean.value, 0, 0.8, linestyle='-.', color='#000000')
        _plt.text(self.targetMean.value, target.max() * 1.1, "$\mu_t$", ha='center')
        # target sigma
        _plt.axvline(self.targetMean.value + self.targetSigma.value, 0, 0.8, linestyle='-.', color='#000000')
        _plt.text(self.targetMean.value + self.targetSigma.value / 2, target.max() * 1.1 / 2, "$\sigma_t$", ha='center')
        _plt.arrow(self.targetMean.value, target.max() * 1.1 / 3,
                   self.targetSigma.value, 0,
                   length_includes_head=True, head_length=1 / 6, head_width=0.025,
                   capstyle='butt', shape='full')

        # Plot vertical range
        _plt.ylim(0, max([target.max(), lure.max()]) * 1.25)

        _plt.subplot(2, 1, 2)
        _plt.plot(x, target, label="Target")
        _plt.plot(x, lure, label="Lure")

        i = 1

        for t in self.thresholds:
            _plt.axvline(t.value, 0, 0.8, linestyle='--', color='#000000')
            _plt.text(t.value, target.max() * 1.1, "$c_{0}$".format(i), ha='center')
            i = i + 1

        _plt.xlabel("Memory strength")
        _plt.ylabel("Probability density")

        # Plot vertical range
        _plt.ylim(0, max([target.max(), lure.max()]) * 1.25)

        # Legend
        _plt.legend()

        # Tight layout for plot
        _plt.tight_layout()

        print(f"baseRate: {baseRate}")
        print(f"area ratio: {ratio}")

    def plotShaded(self, distribution, clow, chigh, baseRate=0.50, fill=True, linestyle="-", color="red", alpha=1, hatch="None"):
        if clow > 0:
            xlow = self.thresholds[clow - 1].value
        else:
            xlow = -5

        if chigh < len(self.thresholds):
            xhigh = self.thresholds[chigh - 1].value
        else:
            xhigh = 5

        x = _np.linspace(xlow, xhigh, 200)

        if distribution == "target":
            y = _norm.pdf(x, self.targetMean.value, self.targetSigma.value)
        elif distribution == "lure":
            y = _norm.pdf(x, self.lureMean.value, self.lureSigma.value)*(1/baseRate-1)

        if fill:
            if hatch != "None":
                _plt.fill_between(x, 0, y, color=color, alpha=alpha, hatch=hatch, edgecolor="black")
            else:
                _plt.fill_between(x, 0, y, color=color, alpha=alpha)
        else:
            _plt.plot(x, y, linestyle=linestyle, color=color, alpha=alpha)

        _plt.xlabel("Memory strength")
        _plt.ylabel("Probability density")

    def plotCriteria(self, linestyle="-", color="black", alpha=1):
        x = _np.linspace(-5, 5, 200)
        y = _norm.pdf(x, self.targetMean.value, self.targetSigma.value)
        i = 1

        for t in self.thresholds:
            _plt.axvline(t.value, 0, 0.7, linestyle=linestyle, color=color)
            xrange = _plt.gca().get_xlim()
            tx = (t.value - xrange[0]) / (xrange[1] - xrange[0])
            _plt.text(tx, 0.8, "$c_{0}$".format(i), ha='center', transform=_plt.gca().transAxes)
            i = i + 1

    def plotFit(self):
        if self.lineupSize != 1:
            self.plotFitLineup()
        else:
            self.plotFitShowup()

    def plotFitLineup(self):

        [pred_tarid,
         pred_tasid_array,
         pred_tafid_array,
         pred_tprid,
         pred_tpsid_array,
         pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        # confidence = _np.flip(list(self.processedData.data_rates.columns.get_level_values(self.processedData.dependentVariable)))
        confidence = list(self.processedData.data_pivot.loc['targetAbsent', 'fillerId'].axes[0].droplevel())
        x = _np.arange(0, pred_tasid_array.size, 1) + 1

        fig = _plt.figure(constrained_layout=True)
        gs = fig.add_gridspec(3, 3)
        ax1 = fig.add_subplot(gs[0, 0:2])
        ax2 = fig.add_subplot(gs[1, 0:2])
        ax3 = fig.add_subplot(gs[2, 0:2])

        ax4 = fig.add_subplot(gs[0, 2])
        # ax6 = fig.add_subplot(gs[1,2])
        ax5 = fig.add_subplot(gs[2, 2])

        # tafid fit bar
        _plt.sca(ax1)
        _plt.bar(confidence, pred_tafid_array, fill=False, label="Prediction")
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetAbsent', 'fillerId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetAbsent', 'fillerId']),
                      fmt='o',
                      markersize=5,
                      capsize=5,
                      label="Data")
        _plt.ylabel("TA Filler ID")

        ax1.xaxis.set_major_locator(_plt.MaxNLocator(integer=True))

        _plt.legend()

        # tasid data plot
        _plt.sca(ax2)
        _plt.bar(confidence, pred_tpsid_array, fill=False)
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetPresent', 'suspectId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetPresent', 'suspectId']),
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TP Suspect ID")

        ax2.xaxis.set_major_locator(_plt.MaxNLocator(integer=True))

        # tpfid data plot
        _plt.sca(ax3)
        _plt.bar(confidence, pred_tpfid_array, fill=False)
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetPresent', 'fillerId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetPresent', 'fillerId']),
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TP Filler ID")
        _plt.xlabel("Confidence bin")

        ax3.xaxis.set_major_locator(_plt.MaxNLocator(integer=True))

        # tarid data plot
        _plt.sca(ax4)
        _plt.bar([0], [pred_tarid], fill=False)
        _plt.errorbar([0],
                      [self.processedData.data_pivot.loc['targetAbsent', 'rejectId'].sum()],
                      [_np.sqrt(self.processedData.data_pivot.loc['targetAbsent', 'rejectId'].sum())],
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TA Reject ID")
        _plt.tick_params(axis='x',  # changes apply to the x-axis
                         which='both',  # both major and minor ticks are affected
                         bottom=False,  # ticks along the bottom edge are off
                         top=False,  # ticks along the top edge are off
                         labelbottom=False)  # labels along the bottom edge are off

        # tarid data plot
        _plt.sca(ax5)
        _plt.bar([0], [pred_tprid], fill=False)
        _plt.errorbar([0],
                      [self.processedData.data_pivot.loc['targetPresent', 'rejectId'].sum()],
                      [_np.sqrt(self.processedData.data_pivot.loc['targetPresent', 'rejectId'].sum())],
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TP Reject ID")
        _plt.tick_params(axis='x',  # changes apply to the x-axis
                         which='both',  # both major and minor ticks are affected
                         bottom=False,  # ticks along the bottom edge are off
                         top=False,  # ticks along the top edge are off
                         labelbottom=False)  # labels along the bottom edge are off

        _plt.tight_layout()

    def plotFitShowup(self):

        [pred_tarid,
         pred_tasid_array,
         pred_tafid_array,
         pred_tprid,
         pred_tpsid_array,
         pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        confidence = _np.flip(list(
            self.processedData.data_rates.columns.get_level_values(self.processedData.dependentVariable)))

        x = range(0, pred_tasid_array.size, 1)

        fig = _plt.figure()
        _plt.subplot(2, 1, 1)

        _plt.bar(confidence, pred_tasid_array, fill=False, label="Prediction")
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetAbsent', 'suspectId'] +
                      self.processedData.data_pivot.loc['targetAbsent', 'rejectId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetAbsent', 'suspectId'] +
                               self.processedData.data_pivot.loc['targetAbsent', 'rejectId']),
                      fmt='o',
                      markersize=5,
                      capsize=5,
                      label="Data")
        _plt.ylabel("TA frequencies")
        _plt.legend()

        _plt.subplot(2, 1, 2)
        _plt.bar(confidence, pred_tpsid_array, fill=False)
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetPresent', 'suspectId'] +
                      self.processedData.data_pivot.loc['targetPresent', 'rejectId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetPresent', 'suspectId'] +
                               self.processedData.data_pivot.loc['targetPresent', 'rejectId']),
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TP frequencies")

        _plt.tight_layout()

    def plotROC(self, criterion1=-10, criterion2=10, nsteps=100, label="Indep model", colorFromLabel=""):

        rate_tafid_array = []
        rate_tpfid_array = []
        rate_tpsid_array = []

        for x in _np.linspace(criterion1, criterion2, nsteps):
            [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(x)

            rate_tafid_array.append(pred_tafid / self.lineupSize / self.numberTALineups)
            rate_tpfid_array.append(pred_tpfid / self.numberTPLineups)
            rate_tpsid_array.append(pred_tpsid / self.numberTPLineups)

        if colorFromLabel == "":
            _plt.plot(rate_tafid_array, rate_tpsid_array, linestyle='--', label=label)
        else:
            fc = _getColorofLabeledFromGca(colorFromLabel)
            _plt.plot(rate_tafid_array, rate_tpsid_array, linestyle='--', label=label, color=fc)

    def plotCAC(self, nsteps=50, label="Indep model", colorFromLabel="", baseRate = 0.5):

        # need to create look up between confidence and criterion
        confidence = self.processedData.data_rates.loc[self.processedData.dependentVariable, 'central']

        rate_tafid_array = []
        rate_tasid_array = []
        rate_tpfid_array = []
        rate_tpsid_array = []

        for i in range(0, len(self.thresholds), 1):
            if i < len(self.thresholds) - 1:
                [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateFrequencyForCriterion(self.thresholds[i + 1],
                                                                                           self.thresholds[i])
            else:
                [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(self.thresholds[i])

            rate_tafid_array.append(pred_tafid)
            rate_tasid_array.append(pred_tafid / self.lineupSize)
            rate_tpfid_array.append(pred_tpfid)
            rate_tpsid_array.append(pred_tpsid)

        rate_tafid_array = _np.array(rate_tafid_array)
        rate_tasid_array = _np.array(rate_tasid_array)
        rate_tpfid_array = _np.array(rate_tpfid_array)
        rate_tpsid_array = _np.array(rate_tpsid_array)

        if self.processedData.lineupSize != 1 :
            cac = baseRate * rate_tpsid_array / (baseRate * rate_tpsid_array + (1-baseRate)*rate_tasid_array)
            if colorFromLabel == "":
                _plt.plot(confidence[-1::-1], cac, linestyle='--', label=label)
            else:
                fc = _getColorofLabeledFromGca(colorFromLabel)
                _plt.plot(confidence[-1::-1], cac, linestyle='--', label=label, color=fc)
        else :
            cac1 = rate_tpsid_array / (rate_tpsid_array + rate_tasid_array)
            cac2 = rate_tasid_array / (rate_tpsid_array + rate_tasid_array)
            if colorFromLabel == "":
                _plt.plot(confidence[-1::-1][confidence[-1::-1] >=0], cac1[confidence[-1::-1] >=0], linestyle='--', label=label, color='k')
                _plt.plot(confidence[-1::-1][confidence[-1::-1] <=0], cac2[confidence[-1::-1] <=0], linestyle='--', label=label,
                    color='k')
            else:
                fc = _getColorofLabeledFromGca(colorFromLabel)
                _plt.plot(confidence[-1::-1][confidence[-1::-1] >=0], cac1[confidence[-1::-1] >=0], linestyle='--', label=label, color=fc)
                _plt.plot(confidence[-1::-1][confidence[-1::-1] <=0], cac2[confidence[-1::-1] <=0], linestyle='--', label=label, color=fc)


    def plotChi2History(self):

        _plt.plot(self.chi2_array)
        _plt.axhline(self.chi2, linestyle="--")

        _plt.xlabel("$\\chi^2$ function evaluation iteration")
        _plt.ylabel("$\\chi^2$")

        # Tight layout for plot
        _plt.tight_layout()


###########################################################################################################################################
class ModelFitIndependentObservationSimple(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFit.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma, chi2Var=chi2Var)

    def calculateCumulativeFrequencyForCriterion(self, c):
        # target ID in target present lineups 
        def probTargetIDTargetPresent(x):
            return _norm.cdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * _norm.pdf(x,
                                                                                                                self.targetMean.value,
                                                                                                                self.targetSigma.value)

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x):
            return _norm.cdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 2) * _norm.pdf(x,
                                                                                                                self.lureMean.value,
                                                                                                                self.lureSigma.value) * _norm.cdf(
                x, self.targetMean.value, self.targetSigma.value)

        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        # filler ID (suspect ID) in target absent lineups 
        def probFillerIDTargetAbsentIntegral(x1):
            return _norm.cdf(x1) ** self.lineupSize

        prob_tpsid = probTargetIDTargetPresentIntegral(float(c), 6)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(float(c), 6)
        prob_tafid = 1 - probFillerIDTargetAbsentIntegral(float(c))

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])


###########################################################################################################################################
class ModelFitIndependentObservation(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFit.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma, chi2Var=chi2Var)

    def setEqualVariance(self):
        super().setEqualVariance()

        self.targetBetweenSigma.fixed = False
        self.targetBetweenSigma.value = 0.3

    def setUnequalVariance(self):
        super().setUnequalVariance()

        self.targetBetweenSigma.fixed = False
        self.targetBetweenSigma.value = 0.3

    def monteCarloDecision(self, pred_tafid_array, pred_tpsid_array, pred_tpfid_array, memoryStrength):
        pass

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        # target ID in target present lineups 

        def probTargetIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureWithinSigma) ** (self.lineupSize - 1) * \
                normpdf(x, self.targetMean.value, self.targetWithinSigma) * \
                (1 - normcdf(float(c), x, self.targetBetweenSigma.value))

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureWithinSigma) ** (self.lineupSize - 2) * \
                normpdf(x, self.lureMean.value, self.lureWithinSigma) * \
                normcdf(x, self.targetMean.value, self.targetWithinSigma) * \
                (1 - normcdf(float(c), x, self.targetBetweenSigma.value))

        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetAbsent(x):
            return normpdf(x, self.lureMean.value, self.lureWithinSigma) * \
                normcdf(x, self.lureMean.value, self.lureWithinSigma) ** (self.lineupSize - 1) * \
                (1 - normcdf(float(c), x, self.targetBetweenSigma.value))

        # filler ID (suspect ID) in target absent lineups 
        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(
            self.targetMean.value - self.targetSigma.value * self.integrationSigma,
            self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])


###########################################################################################################################################
class ModelFitBestRest(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFit.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma, chi2Var=chi2Var)

    def mean(self, w, lm, ls, tm, ts, nlineup):
        tlm = truncatedMean(lm, ls, w)
        ttm = truncatedMean(tm, ts, w)

        return w - ((nlineup - 2) * tlm + ttm) / (nlineup - 1)

    def sigma(self, w, lm, ls, tm, ts, nlineup):
        tlv = truncatedVar(lm, ls, w)
        ttv = truncatedVar(tm, ts, w)

        return _np.sqrt(((nlineup - 2) * tlv + ttv) / (nlineup - 1) ** 2)

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        # target ID in target present lineups
        def probTargetIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                normpdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize)
                             )
                 )

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 2) * \
                normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                       self.targetSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                        self.targetSigma.value, self.lineupSize)
                             )
                 )

        # filler ID in target present lineups
        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetAbsent(x):
            return normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize))
                 )

            # filler ID (suspect ID) in target absent lineups

        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(
            self.targetMean.value - self.targetSigma.value * self.integrationSigma,
            self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])


###########################################################################################################################################
class ModelFitEnsemble(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFit.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma, chi2Var=chi2Var)

    def mean(self, w, lm, ls, tm, ts, nlineup):
        tlm = truncatedMean(lm, ls, w)
        ttm = truncatedMean(tm, ts, w)

        return (w * (nlineup - 1) - tlm * (nlineup - 2) - ttm) / nlineup

    def sigma(self, w, lm, ls, tm, ts, nlineup):
        tlv = truncatedVar(lm, ls, w)
        ttv = truncatedVar(tm, ts, w)

        return _np.sqrt((ttv + (nlineup - 2) * tlv) / nlineup ** 2)

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        # target ID in target present lineups
        def probTargetIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                normpdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize)
                             )
                 )

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 2) * \
                normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                       self.targetSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                        self.targetSigma.value, self.lineupSize)
                             )
                 )

        # filler ID in target present lineups
        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetAbsent(x):
            return normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize))
                 )

        # filler ID (suspect ID) in target absent lineups
        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(
            self.targetMean.value - self.targetSigma.value * self.integrationSigma,
            self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])


###########################################################################################################################################
class ModelFitIntegration(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFit.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma, chi2Var=chi2Var)

    def mean(self, w, lm, ls, tm, ts, nlineup):
        tlm = truncatedMean(lm, ls, w)
        ttm = truncatedMean(tm, ts, w)

        return w + ttm + (nlineup - 2) * tlm

    def sigma(self, w, lm, ls, tm, ts, nlineup):
        tlv = truncatedVar(lm, ls, w)
        ttv = truncatedVar(tm, ts, w)

        return _np.sqrt(nlineup ** 2 * self.targetBetweenSigma.value ** 2 + ttv + (nlineup - 2) * tlv)

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        # target ID in target present lineups
        def probTargetIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                normpdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize)
                             )
                 )

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 2) * \
                normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                       self.targetSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                        self.targetSigma.value, self.lineupSize)
                             )
                 )

        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetAbsent(x):
            return normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize))
                 )

        # filler ID (suspect ID) in target absent lineups
        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(
            self.targetMean.value - self.targetSigma.value * self.integrationSigma,
            self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])

class ModelFitDesignatedInnocent(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=6, chi2Var='expected'):
        ModelFit.__init__(self,processedData, debug=debug, integrationSigma=integrationSigma, chi2Var=chi2Var)

        # parameters
        self.innocentMean = self.addParameter("innocentMean", 1.0)
        self.innocentSigma = self.addParameter("innocentSigma", 1.0)

    def resetParameters(self):
        ModelFit.resetParameters(self)

        self.innocentMean.value = 0.5
        self.innocentSigma.value = 1.0

    def setEqualVariance(self):

        ModelFit.setEqualVariance(self)

        # self.innocentSigma.set_equal(self.targetSigma)

    def setUnequalVariance(self):

        ModelFit.setUnequalVariance(self)

        self.innocentMean.value = 1.0
        self.innocentSigma.value = 1.0

    def calculateFrequenciesForAllCriteria(self):
        pred_tafid_array = []
        pred_tasid_array = []
        pred_tpsid_array = []
        pred_tpfid_array = []

        for i in range(0, len(self.thresholds), 1):
            if i < len(self.thresholds) - 1:
                [pred_tafid, pred_tasid, pred_tpsid, pred_tpfid] = self.calculateFrequencyForCriterion(self.thresholds[i + 1],
                                                                                           self.thresholds[i])
            else:
                [pred_tafid, pred_tasid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(self.thresholds[i])

            pred_tafid_array.append(pred_tafid)
            pred_tasid_array.append(pred_tasid)
            pred_tpsid_array.append(pred_tpsid)
            pred_tpfid_array.append(pred_tpfid)

        pred_tafid_array = _np.array(pred_tafid_array)
        pred_tasid_array = _np.array(pred_tasid_array)
        pred_tpsid_array = _np.array(pred_tpsid_array)
        pred_tpfid_array = _np.array(pred_tpfid_array)

        pred_tarid = self.numberTALineups - pred_tasid_array.sum() - pred_tafid_array.sum()
        pred_tprid = self.numberTPLineups - pred_tpsid_array.sum() - pred_tpfid_array.sum()

        if self.debug:
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tafid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tafid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tasid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tasid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tarid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tarid)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tpfid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tpfid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tpsid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tpsid_array)
            print('ModelFits.calculateFrequenciesForAllCriteria> pred_tprid'.ljust(self.debugIoPadSize, ' ') + ":",
                  pred_tprid)

        return [pred_tarid,
                pred_tasid_array,
                pred_tafid_array,
                pred_tprid,
                pred_tpsid_array,
                pred_tpfid_array]

    def calculateChi2(self, params):

        freeParams = self.freeParameterList()

        for i in range(0, len(freeParams), 1):
            p = freeParams[i]
            p.value = params[i]

        if self.debug:
            print('------------------------------------------------------------------------------')
            print('ModelFit.calculateChi2> chi2 valuation number'.ljust(self.debugIoPadSize, ' ') + ":", self.iteration)
            print('ModelFit.calculateChi2> params               '.ljust(self.debugIoPadSize, ' ') + ":", params)

        [pred_tarid, pred_tasid_array, pred_tafid_array,
         pred_tprid, pred_tpsid_array, pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        if self.lineupSize != 1:
            chi2_tafid = 0
            chi2_tasid = 0
            chi2_tpsid = 0
            chi2_tpfid = 0
            chi2_tarid = 0
            chi2_tprid = 0

            for i in range(0, self.numberConditions):
                if self.chi2Var == "observed":
                    var_tafid = self.processedData.data_pivot.loc['targetAbsent', 'fillerId'][i]
                    var_tasid = self.processedData.data_pivot.loc['targetAbsent', 'designateId'][i]
                    var_tpfid = self.processedData.data_pivot.loc['targetPresent', 'fillerId'][i]
                    var_tpsid = self.processedData.data_pivot.loc['targetPresent', 'suspectId'][i]
                elif self.chi2Var == "expected":
                    var_tafid = abs(pred_tafid_array[i])
                    var_tasid = abs(pred_tasid_array[i])
                    var_tpsid = abs(pred_tpsid_array[i])
                    var_tpfid = abs(pred_tpfid_array[i])

                chi2_tafid = chi2_tafid + (
                            self.processedData.data_pivot.loc['targetAbsent', 'fillerId'][i] - pred_tafid_array[
                        i]) ** 2 / var_tafid
                chi2_tasid = chi2_tasid + (
                            self.processedData.data_pivot.loc['targetAbsent', 'designateId'][i] - pred_tasid_array[
                        i]) ** 2 / var_tasid
                chi2_tpfid = chi2_tpfid + (
                            self.processedData.data_pivot.loc['targetPresent', 'fillerId'][i] - pred_tpfid_array[
                        i]) ** 2 / var_tpfid
                chi2_tpsid = chi2_tpsid + (
                            self.processedData.data_pivot.loc['targetPresent', 'suspectId'][i] - pred_tpsid_array[
                        i]) ** 2 / var_tpsid


            if self.chi2Var == "observed":
                var_tarid = pred_tarid
                var_tprid = pred_tprid
            elif self.chi2Var == "expected":
                var_tarid = self.processedData.data_pivot.loc['targetAbsent', 'rejectId'].sum()
                var_tprid = self.processedData.data_pivot.loc['targetPresent', 'rejectId'].sum()

            chi2_tarid = (self.processedData.data_pivot.loc[
                              'targetAbsent', 'rejectId'].sum() - pred_tarid) ** 2 / var_tarid
            chi2_tprid = (self.processedData.data_pivot.loc[
                              'targetPresent', 'rejectId'].sum() - pred_tprid) ** 2 / var_tprid

            chi2 = chi2_tafid + chi2_tasid + chi2_tpsid + chi2_tpfid + chi2_tarid + chi2_tprid

            # Criterion flip guard
            for i in range(0, len(self.thresholds) - 1):
                if self.thresholds[i].value > self.thresholds[i + 1].value:
                    chi2 = chi2 + 10000

            if self.debug:
                print('ModelFit.calculateChi2> chi2 tafid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tafid)
                print('ModelFit.calculateChi2> chi2 tasid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tasid)
                print('ModelFit.calculateChi2> chi2 tarid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tarid)
                print('ModelFit.calculateChi2> chi2 tpfid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tpfid)
                print('ModelFit.calculateChi2> chi2 tpsid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tpsid)
                print('ModelFit.calculateChi2> chi2 tprid'.ljust(self.debugIoPadSize, ' ') + ":", chi2_tprid)
                print('ModelFit.calculateChi2> chi2 total'.ljust(self.debugIoPadSize, ' ') + ":", chi2)

            # Criterion flip guard
            for i in range(0, len(self.thresholds) - 1):
                if self.thresholds[i].value > self.thresholds[i + 1].value:
                    chi2 = chi2 + 10000

        self.iteration = self.iteration + 1

        try:
            self.chi2_array.append(chi2)
        except:
            pass
        # if freeParams[0].value < freeParams[1].value/2 :
        #    chi2 = chi2 + 100

        return chi2

    @property
    def numberDataPoints(self):
        return 4 * self.numberConditions

    def plotModel(self, xlow = -5, xhigh = 5):
        ModelFit.plotModel(self,xlow=xlow, xhigh=xhigh)

        x = _np.linspace(xlow, xhigh, 200)
        innocent = _norm.pdf(x, self.innocentMean.value, self.innocentSigma.value)

        _plt.subplot(2, 1, 1)
        _plt.plot(x, innocent, label="Innocent")

        _plt.subplot(2, 1, 2)
        _plt.plot(x, innocent, label="Innocent")
        _plt.legend()

    def plotFit(self):

        [pred_tarid,
         pred_tasid_array,
         pred_tafid_array,
         pred_tprid,
         pred_tpsid_array,
         pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        # confidence = _np.flip(list(self.processedData.data_rates.columns.get_level_values(self.processedData.dependentVariable)))
        confidence = list(self.processedData.data_pivot.loc['targetAbsent', 'fillerId'].axes[0].droplevel())
        x = _np.arange(0, pred_tasid_array.size, 1) + 1

        fig = _plt.figure(constrained_layout=True)
        gs = fig.add_gridspec(4, 3)
        ax1 = fig.add_subplot(gs[0, 0:2])
        ax2 = fig.add_subplot(gs[1, 0:2])
        ax3 = fig.add_subplot(gs[2, 0:2])
        ax4 = fig.add_subplot(gs[3, 0:2])

        ax5 = fig.add_subplot(gs[0, 2])
        # ax6 = fig.add_subplot(gs[1,2])
        ax6 = fig.add_subplot(gs[2, 2])

        # tafid fit bar
        _plt.sca(ax1)
        _plt.bar(confidence, pred_tafid_array, fill=False, label="Prediction")
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetAbsent', 'fillerId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetAbsent', 'fillerId']),
                      fmt='o',
                      markersize=5,
                      capsize=5,
                      label="Data")
        _plt.ylabel("TA Filler ID")

        ax1.xaxis.set_major_locator(_plt.MaxNLocator(integer=True))

        _plt.legend()

        # tafid fit bar
        _plt.sca(ax2)
        _plt.bar(confidence, pred_tasid_array, fill=False, label="Prediction")
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetAbsent', 'designateId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetAbsent', 'designateId']),
                      fmt='o',
                      markersize=5,
                      capsize=5,
                      label="Data")
        _plt.ylabel("TA Innocent ID")

        ax1.xaxis.set_major_locator(_plt.MaxNLocator(integer=True))

        _plt.legend()

        # tpsid data plot
        _plt.sca(ax3)
        _plt.bar(confidence, pred_tpsid_array, fill=False)
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetPresent', 'suspectId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetPresent', 'suspectId']),
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TP Suspect ID")

        ax2.xaxis.set_major_locator(_plt.MaxNLocator(integer=True))

        # tpfid data plot
        _plt.sca(ax4)
        _plt.bar(confidence, pred_tpfid_array, fill=False)
        _plt.errorbar(confidence,
                      self.processedData.data_pivot.loc['targetPresent', 'fillerId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetPresent', 'fillerId']),
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TP Filler ID")
        _plt.xlabel("Confidence bin")

        ax3.xaxis.set_major_locator(_plt.MaxNLocator(integer=True))

        # tarid data plot
        _plt.sca(ax5)
        _plt.bar([0], [pred_tarid], fill=False)
        _plt.errorbar([0],
                      [self.processedData.data_pivot.loc['targetAbsent', 'rejectId'].sum()],
                      [_np.sqrt(self.processedData.data_pivot.loc['targetAbsent', 'rejectId'].sum())],
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TA Reject ID")
        _plt.tick_params(axis='x',  # changes apply to the x-axis
                         which='both',  # both major and minor ticks are affected
                         bottom=False,  # ticks along the bottom edge are off
                         top=False,  # ticks along the top edge are off
                         labelbottom=False)  # labels along the bottom edge are off

        # tarid data plot
        _plt.sca(ax6)
        _plt.bar([0], [pred_tprid], fill=False)
        _plt.errorbar([0],
                      [self.processedData.data_pivot.loc['targetPresent', 'rejectId'].sum()],
                      [_np.sqrt(self.processedData.data_pivot.loc['targetPresent', 'rejectId'].sum())],
                      fmt='o',
                      markersize=5,
                      capsize=5)
        _plt.ylabel("TP Reject ID")
        _plt.tick_params(axis='x',  # changes apply to the x-axis
                         which='both',  # both major and minor ticks are affected
                         bottom=False,  # ticks along the bottom edge are off
                         top=False,  # ticks along the top edge are off
                         labelbottom=False)  # labels along the bottom edge are off

        _plt.tight_layout()

    def plotROC(self, criterion1=-10, criterion2=10, nsteps=100, label="Indep model", colorFromLabel=""):

        rate_tafid_array = []
        rate_tasid_array = []
        rate_tpfid_array = []
        rate_tpsid_array = []

        for x in _np.linspace(criterion1, criterion2, nsteps):
            [pred_tafid, pred_tasid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(x)

            rate_tafid_array.append(pred_tafid / self.numberTALineups)
            rate_tasid_array.append(pred_tasid / self.numberTALineups)
            rate_tpfid_array.append(pred_tpfid / self.numberTPLineups)
            rate_tpsid_array.append(pred_tpsid / self.numberTPLineups)

        if colorFromLabel == "":
            _plt.plot(rate_tasid_array, rate_tpsid_array, linestyle='--', label=label)
        else:
            fc = _getColorofLabeledFromGca(colorFromLabel)
            _plt.plot(rate_tasid_array, rate_tpsid_array, linestyle='--', label=label, color=fc)

    def plotCAC(self, nsteps=50, label="Indep model", colorFromLabel=""):

        # need to create look up between confidence and criterion
        confidence = self.processedData.data_rates.loc[self.processedData.dependentVariable, 'central']

        rate_tafid_array = []
        rate_tasid_array = []
        rate_tpfid_array = []
        rate_tpsid_array = []

        for i in range(0, len(self.thresholds), 1):
            if i < len(self.thresholds) - 1:
                [pred_tafid, pred_tasid, pred_tpsid, pred_tpfid] = self.calculateFrequencyForCriterion(self.thresholds[i + 1],
                                                                                           self.thresholds[i])
            else:
                [pred_tafid, pred_tasid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(self.thresholds[i])

            rate_tafid_array.append(pred_tafid)
            rate_tasid_array.append(pred_tasid)
            rate_tpfid_array.append(pred_tpfid)
            rate_tpsid_array.append(pred_tpsid)

        rate_tafid_array = _np.array(rate_tafid_array)
        rate_tasid_array = _np.array(rate_tasid_array)
        rate_tpfid_array = _np.array(rate_tpfid_array)
        rate_tpsid_array = _np.array(rate_tpsid_array)

        cac = rate_tpsid_array / (rate_tpsid_array+rate_tasid_array)

        if colorFromLabel == "":
            _plt.plot(confidence[-1::-1], cac, linestyle='--', label=label)
        else:
            fc = _getColorofLabeledFromGca(colorFromLabel)
            _plt.plot(confidence[-1::-1], cac, linestyle='--', label=label, color=fc)


class ModelFitDesignatedInnocentIndependentObservationSimple(ModelFitDesignatedInnocent):
    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFitDesignatedInnocent.__init__(self,
                                            processedData,
                                            debug=debug,
                                            integrationSigma=integrationSigma,
                                            chi2Var=chi2Var)

    def calculateCumulativeFrequencyForCriterion(self, c):

        def probFillerIDTargetAbsent(x) :
            return _norm.cdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-2)* \
                _norm.cdf(x,self.innocentMean.value, self.innocentSigma.value) *\
                _norm.pdf(x,self.lureMean.value, self.lureSigma.value)

        def probFillerIDTargetAbsentIntegral(x1,x2) :
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        def probSuspectIDTargetAbsent(x) :
            return _norm.cdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-1) *\
                   _norm.pdf(x,self.innocentMean.value, self.innocentSigma.value)

        def probSuspectIDTargetAbsentIntegral(x1,x2) :
            return _integrate.quad(probSuspectIDTargetAbsent, x1, x2)[0]

        def probTargetIDTargetPresent(x):
            return _norm.cdf(x, self.lureMean.value,self.lureSigma.value) ** (self.lineupSize - 1) * \
                _norm.pdf(x,self.targetMean.value,self.targetSigma.value)

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x):
            return _norm.cdf(x,self.lureMean.value,self.lureSigma.value) ** (self.lineupSize - 2) * \
                _norm.pdf(x,self.lureMean.value,self.lureSigma.value) * \
                _norm.cdf(x,self.targetMean.value,self.targetSigma.value)

        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        prob_tafid = (self.lineupSize - 1) *probFillerIDTargetAbsentIntegral(float(c), 6)
        prob_tasid = probSuspectIDTargetAbsentIntegral(float(c), 6)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(float(c), 6)
        prob_tpsid = probTargetIDTargetPresentIntegral(float(c), 6)

        pred_tafid = prob_tafid * self.numberTALineups
        pred_tasid = prob_tasid * self.numberTALineups
        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups

        return _np.array([pred_tafid, pred_tasid, pred_tpsid, pred_tpfid])


class ModelFitDesignatedInnocentEnsemble(ModelFitDesignatedInnocent):
    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFitDesignatedInnocent.__init__(self,
                                            processedData,
                                            debug=debug,
                                            integrationSigma=integrationSigma,
                                            chi2Var=chi2Var)



    def mean(self, w, lm, ls, tm, ts, nlineup):
        tlm = truncatedMean(lm, ls, w)
        ttm = truncatedMean(tm, ts, w)

        return (w * (nlineup - 1) - tlm * (nlineup - 2) - ttm) / nlineup

    def sigma(self, w, lm, ls, tm, ts, nlineup):
        tlv = truncatedVar(lm, ls, w)
        ttv = truncatedVar(tm, ts, w)

        return _np.sqrt((ttv + (nlineup - 2) * tlv) / nlineup ** 2)

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        def probFillerIDTargetAbsent(x):
            return normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize))
                 )

        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        def probSuspectIDTargetAbsent(x) :
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                normpdf(x, self.innocentMean.value, self.innocentSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize)
                             )
                 )
        def probSuspectIDTargetAbsentIntegral(x1,x2) :
            return _integrate.quad(probSuspectIDTargetAbsent, x1, x2)[0]

        def probTargetIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                normpdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                       self.lureSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                        self.lureSigma.value, self.lineupSize)
                             )
                 )

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 2) * \
                normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                       self.targetSigma.value, self.lineupSize),
                             self.sigma(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                        self.targetSigma.value, self.lineupSize)
                             )
                 )

        # filler ID in target present lineups
        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]


        prob_tpsid = probTargetIDTargetPresentIntegral(
            self.targetMean.value - self.targetSigma.value * self.integrationSigma,
            self.targetMean.value + self.targetSigma.value * self.integrationSigma)

        prob_tasid = probSuspectIDTargetAbsentIntegral(
            self.innocentMean.value - self.innocentSigma.value * self.integrationSigma,
            self.innocentMean.value + self.innocentSigma.value * self.integrationSigma)

        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tasid = prob_tasid * self.numberTALineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tasid, pred_tpsid, pred_tpfid])

class ModelFitLureTargetPresent(ModelFitDesignatedInnocent) :
    def __init__(self, processedData, debug=False, integrationSigma=6, chi2Var='expected'):
        ModelFitDesignatedInnocent.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma, chi2Var=chi2Var)

        # TODO should be fixed in ModelFitDesignatedInnocent
        self.innocentMean.value = 0.0
        self.innocentSigma.value = 1.0

        # parameters
        self.lureTPMean = self.addParameter("lureTPMean", 0.0)
        self.lureTPSigma = self.addParameter("lureTPSigma", 1.0)

    def resetParameters(self):
        ModelFitDesignatedInnocent.resetParameters(self)

        # TODO should be fixed in ModelFitDesignatedInnocent
        self.innocentMean.value = 0.0
        self.innocentSigma.value = 1.0
        self.lureTPMean.value = 0.0
        self.lureTPSigma.value = 1.0

    def setEqualVariance(self):

        ModelFitDesignatedInnocent.setEqualVariance(self)

        # self.innocentSigma.set_equal(self.targetSigma)

    def setUnequalVariance(self):

        ModelFitDesignatedInnocent.setUnequalVariance(self)

        self.lureTPMean.value = 0.0
        self.lureTPSigma.value = 1.0


class ModelFitLureTargetPresentEnsemble(ModelFitLureTargetPresent):

    def __init__(self, processedData, debug=False, integrationSigma=8, chi2Var='expected'):
        ModelFitLureTargetPresent.__init__(self,
                                           processedData,
                                           debug=debug,
                                           integrationSigma=integrationSigma,
                                           chi2Var=chi2Var)

    def mean(self, w, lm, ls, tm, ts, nlineup):
        tlm = truncatedMean(lm, ls, w)
        ttm = truncatedMean(tm, ts, w)

        return (w * (nlineup - 1) - tlm * (nlineup - 2) - ttm) / nlineup

    def sigma(self, w, lm, ls, tm, ts, nlineup):
        tlv = truncatedVar(lm, ls, w)
        ttv = truncatedVar(tm, ts, w)

        return _np.sqrt((ttv + (nlineup - 2) * tlv) / nlineup ** 2)

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        def probFillerIDTargetAbsent(x):
            return normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                (1 - normcdf(float(c),
                             self.mean(x,
                                       self.lureMean.value,
                                       self.lureSigma.value,
                                       self.innocentMean.value,
                                       self.innocentSigma.value,
                                       self.lineupSize),
                             self.sigma(x,
                                        self.lureMean.value,
                                        self.lureSigma.value,
                                        self.innocentMean.value,
                                        self.innocentSigma.value,
                                        self.lineupSize))
                 )

        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        def probSuspectIDTargetAbsent(x) :
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                normpdf(x, self.innocentMean.value, self.innocentSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x,
                                       self.lureMean.value,
                                       self.lureSigma.value,
                                       self.lureMean.value,
                                       self.lureSigma.value,
                                       self.lineupSize),
                             self.sigma(x,
                                        self.lureMean.value,
                                        self.lureSigma.value,
                                        self.lureMean.value,
                                        self.lureSigma.value,
                                        self.lineupSize)
                             )
                 )
        def probSuspectIDTargetAbsentIntegral(x1,x2) :
            return _integrate.quad(probSuspectIDTargetAbsent, x1, x2)[0]

        def probTargetIDTargetPresent(x):
            return normcdf(x, self.lureTPMean.value, self.lureTPSigma.value) ** (self.lineupSize - 1) * \
                normpdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x,
                                       self.lureTPMean.value,
                                       self.lureTPSigma.value,
                                       self.lureTPMean.value,
                                       self.lureTPSigma.value,
                                       self.lineupSize),
                             self.sigma(x,
                                        self.lureTPMean.value,
                                        self.lureTPSigma.value,
                                        self.lureTPMean.value,
                                        self.lureTPSigma.value,
                                        self.lineupSize)
                             )
                 )

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetPresent(x):
            return normcdf(x, self.lureTPMean.value, self.lureTPSigma.value) ** (self.lineupSize - 2) * \
                normpdf(x, self.lureTPMean.value, self.lureTPSigma.value) * \
                normcdf(x, self.targetMean.value, self.targetSigma.value) * \
                (1 - normcdf(float(c),
                             self.mean(x,
                                       self.lureTPMean.value,
                                       self.lureTPSigma.value,
                                       self.targetMean.value,
                                       self.targetSigma.value,
                                       self.lineupSize),
                             self.sigma(x,
                                        self.lureTPMean.value,
                                        self.lureTPSigma.value,
                                        self.targetMean.value,
                                        self.targetSigma.value,
                                        self.lineupSize)
                             )
                 )

        # filler ID in target present lineups
        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]


        prob_tpsid = probTargetIDTargetPresentIntegral(
            self.targetMean.value - self.targetSigma.value * self.integrationSigma,
            self.targetMean.value + self.targetSigma.value * self.integrationSigma)

        prob_tasid = probSuspectIDTargetAbsentIntegral(
            self.innocentMean.value - self.innocentSigma.value * self.integrationSigma,
            self.innocentMean.value + self.innocentSigma.value * self.integrationSigma)

        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tasid = prob_tasid * self.numberTALineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tasid, pred_tpsid, pred_tpfid])

class ModelFitComposite:
    def __init__(self):
        self.model_fits = []
        self.debug = False
        self.debugIoPadSize = 60
        self.iteraction = 0

    def addFit(self, fit):
        self.model_fits.append(fit)

    def fit(self, maxiter=5000, method="Nelder-Mead", resetParameters=False):
        if resetParameters:
            pass
            # self.resetParameters()

        freeParams = self.freeParameterList()
        p0 = []
        for p in freeParams:
            p0.append(p.value)

        if self.debug:
            print('fit> starting parameters'.ljust(self.debugIoPadSize, ' ') + ":", p0)

        self.iteration = 0

        def chiSquared(x):
            return self.calculateChi2(x)

        self.chi2_array = []

        tStart = _time.perf_counter()
        opt = _optimize.minimize(chiSquared, p0, method=method, options={"maxiter": maxiter})
        tEnd = _time.perf_counter()

        if self.debug:
            print(opt)

        # Store fit output
        self.numberIterations = opt["nit"]
        self.fitStatus = opt["message"]
        self.timeDiff = tEnd - tStart
        # self.pValue = 1 - _chi2.cdf(self.chi2, self.numberDegreesOfFreedom)

        print("fit iterations", self.numberIterations)
        print("fit status    ", self.fitStatus)
        print("fit time      ", self.timeDiff)
        print("fit chi2      ", self.chi2)
        print("fit ndf       ", self.numberDegreesOfFreedom)
        print("fit chi2/ndf  ", self.chi2PerNDF)
        print("fit p-value   ", self.pValue)

    def freeParameterList(self):

        freeParams = []

        for m in self.model_fits:
            for p in m.parameterNames:
                p = getattr(m, p)
                if not p.fixed:
                    freeParams.append(p)

        unique = []
        unique_id = []
        for x in freeParams:
            if id(x) not in unique_id:
                unique.append(x)
                unique_id.append(id(x))


        return unique

    @property
    def chi2(self):

        debug = self.debug
        self.debug = False

        freeParams = self.freeParameterList()
        p0 = []
        for p in freeParams:
            p0.append(p.value)
        chi2 = self.calculateChi2(p0)

        print("chi2>",chi2)

        self.debug = debug
        return chi2

    @property
    def numberFreeParameters(self):
        iFreeParams = 0
        freeParams = self.freeParameterList()
        for p in freeParams:
            iFreeParams = iFreeParams + 1

        return iFreeParams

    def calculateChi2(self, params):

        freeParams = self.freeParameterList()

        for fp, sp in zip(freeParams, params):
            fp.value = sp

        chi2Sum = 0

        for mf in self.model_fits:
            chi2Sum += mf.chi2

        if self.debug:
            print('------------------------------------------------------------------------------')
            print('ModelFit.calculateChi2> chi2 valuation number'.ljust(self.debugIoPadSize, ' ') + ":", self.iteration)
            print('ModelFit.calculateChi2> params               '.ljust(self.debugIoPadSize, ' ') + ":", params)
            print('ModelFit.calculateChi2> chi2                 '.ljust(self.debugIoPadSize, ' ') + ":", chi2Sum)


        self.iteration += 1

        return chi2Sum

    @property
    def numberDegreesOfFreedom(self):
        ndf = 0
        for m in self.model_fits:
            ndf += m.numberDataPoints

        ndf -= self.numberFreeParameters

        return ndf

    @property
    def chi2PerNDF(self):
        return self.chi2 / self.numberDegreesOfFreedom

    @property
    def pValue(self):
        return 1 - _chi2.cdf(self.chi2, self.numberDegreesOfFreedom)
