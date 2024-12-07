import pathlib
from typing import List

import numpy as np
import pandas as pd
import pytest
from pandas import Index

from src.ETF.cours.Cours import Cours
from src.ETF.cours.CoursBuilder import CoursBuilder
from src.ETF.modelPrediction.Dataset.DatasetShift import DatasetShift
from src.ETF.modelPrediction.Dataset.DatasetVector import DatasetVector
from src.service.TimeService import TimeService
from src.util.constants.Frequency import Frequency
from src.util.constants.UnitVectorDataframe import UnitVectorDataframe


# def test_getShiftDataset():
#     valuesList: List = [15, 18, 17, 16, 14, 19, 20, 21, 22, 23, 24]
#     date = TimeService.fromString('15-03-2023 10:00:00')
#     cours: Cours = CoursBuilder.fromList(valuesList, date, Frequency.CALENDAR_DAY)
#     size=3
#
#     datasetShift = DatasetShift(cours, size)
#
#     assert datasetShift.getXTrain().shape[1] == size - 1
#     assert datasetShift.getXTrain().iloc[0].tolist() == valuesList[:size-1]
#     assert datasetShift.getYTrain().iloc[0].tolist() == valuesList[size - 1]
#     with pytest.raises(Exception):
#         DatasetShift(cours, 1000)
#     assert datasetShift.getYTest().iloc[-1].tolist() == valuesList[-1]


def test_DatasetVectorWeekDays():

    valuesList: List = list(range(11*7)) # 77
    date = TimeService.fromString('21-01-2025 12:00:00')
    cours: Cours = CoursBuilder.fromList(valuesList, date, Frequency.CALENDAR_DAY) # end : 07/04/2025 12h -> Lundi

    # WEEK_DAYS
    dataset: DatasetVector = DatasetVector(cours=cours, shapeVector=UnitVectorDataframe.WEEK_DAYS)
    coursTrain, coursTest = dataset.getCours()
    assert coursTrain.getStart().toString() == '27-01-2025 00:00:00'
    assert coursTrain.getEnd().toString() == '16-03-2025 00:00:00'
    assert coursTest.getStart().toString() == '17-03-2025 00:00:00'
    assert coursTest.getEnd().toString() == '30-03-2025 00:00:00'


def test_DatasetVectorWorkingWeekDays():
    # WORKINGDAYSWEEK_DAYS

    valuesList: List = list(range(20 * 7))  # 77
    ts = pd.Series(valuesList)
    date = TimeService.fromString('21-01-2025 00:00:00')
    datesIndex: Index = pd.date_range(start=date.toString(),
                                      periods=len(valuesList),
                                      freq='D')

    ts.index = datesIndex
    cours: Cours = CoursBuilder.fromTimeSerie(ts, step=Frequency.CALENDAR_DAY)

    # ma missing row strategy doit retourner 0 mais necessite des valeurs dans la row (ne retourne pas 0 directement) pour le teste
    dataset: DatasetVector = DatasetVector(cours=cours, shapeVector=UnitVectorDataframe.WORKINGDAYSWEEK_WEEK, missingValueStrategy=lambda row:row.mean() - row.mean())
    coursTrain, coursTest = dataset.getCours()
    assert coursTrain.getStart().toString() == '27-01-2025 00:00:00'
    assert coursTrain.getEnd().toString() == '02-05-2025 00:00:00'
    assert coursTest.getStart().toString() == '05-05-2025 00:00:00'
    assert coursTest.getEnd().toString() == '30-05-2025 00:00:00'

    # si tout les jours de la semaine sont fournis et vendredi manquant ne dois pas etre remplace par un Samedi
    # assert coursTrain.getValues()[pd.Timestamp('2025-02-10 00:00:00')] == 0
    # les weekend sont bien skipped:
    assert coursTrain.getValues()[pd.Timestamp('2025-02-21 00:00:00')] == 31 # Vendredi
    assert coursTrain.getValues()[pd.Timestamp('2025-02-24 00:00:00')] == 34 # Lundi


def test_DatasetVectorMonthDays():
    # MONTH_DAYS
    lenTs = 395
    valuesList: List = list(range(lenTs)) #24*
    date = TimeService.fromString('21-01-2025 00:00:00')
    datesIndex: Index = pd.date_range(start=date.toString(),
                                      periods=lenTs,
                                      freq='D')
    ts = pd.Series(valuesList)
    ts.index = datesIndex

    ts["22-02-2025 00:00:00"] = 100
    ts["22-02-2025 04:00:00"] = 200

    cours: Cours = CoursBuilder.fromTimeSerie(ts, step=Frequency.CALENDAR_DAY)

    dataset: DatasetVector = DatasetVector(cours=cours, shapeVector=UnitVectorDataframe.MONTH_DAYS, ratioSplitTest=0.4)
    coursTrain, coursTest = dataset.getCours()
    assert coursTrain.getStart().toString() == '01-02-2025 00:00:00'
    assert coursTrain.getEnd().toString() == '31-07-2025 00:00:00'
    assert coursTest.getStart().toString() == '01-08-2025 00:00:00'
    assert coursTest.getEnd().toString() == '31-12-2025 00:00:00'

    trainTs = coursTrain.getValues()
    trainTs.index = trainTs.index.strftime(TimeService.getTimeFormat())

    testTs = coursTest.getValues()
    testTs.index = testTs.index.strftime(TimeService.getTimeFormat())

    assert trainTs['31-03-2025 00:00:00'] == 69
    assert trainTs['01-04-2025 00:00:00'] == 70
    assert dataset.getXTrain().iloc[1, 30] == 69
    assert trainTs['28-02-2025 00:00:00'] == 38
    assert trainTs['01-03-2025 00:00:00'] == 39
    assert trainTs['22-02-2025 00:00:00'] == 150
    assert testTs['01-09-2025 00:00:00'] == 223
    assert testTs['30-09-2025 00:00:00'] == 252
