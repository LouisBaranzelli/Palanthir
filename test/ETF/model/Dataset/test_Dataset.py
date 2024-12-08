import pathlib
from typing import List

import numpy as np
import pandas as pd
import pytest
from pandas import Index

from src.ETF.cours.Cours import Cours
from src.ETF.cours.CoursBuilder import CoursBuilder
from src.ETF.modelPrediction.Dataset.DatasetShift import DatasetShift
from src.ETF.modelPrediction.Dataset.SetVector import SetVector
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
    dataset: SetVector = SetVector(cours=cours, shapeVector=UnitVectorDataframe.WEEK_DAYS)
    cours = dataset.getCours()
    assert cours.getStart().toString() == '27-01-2025 00:00:00'
    assert cours.getEnd().toString() == '06-04-2025 00:00:00'


def test_DatasetVectorWorkingWeekDays():
    # WORKINGDAYSWEEK_DAYS

    valuesList: List = list(range(10 * 7))  # 77
    ts = pd.Series(valuesList)
    date = TimeService.fromString('21-01-2025 00:00:00')
    datesIndex: Index = pd.date_range(start=date.toString(),
                                      periods=len(valuesList),
                                      freq='D')

    ts.index = datesIndex
    cours: Cours = CoursBuilder.fromTimeSerie(ts, step=Frequency.CALENDAR_DAY)

    # ma missing row strategy doit retourner 0 mais necessite des valeurs dans la row (ne retourne pas 0 directement) pour le teste
    dataset: SetVector = SetVector(cours=cours, shapeVector=UnitVectorDataframe.WORKINGDAYSWEEK_DAYS, missingValueStrategy=lambda row: row.mean() - row.mean())
    cours = dataset.getCours()
    assert cours.getStart().toString() == '27-01-2025 00:00:00'
    assert cours.getEnd().toString() == '28-03-2025 00:00:00'

    # les weekend sont bien skipped:
    assert cours.getValues()[pd.Timestamp('2025-01-31 00:00:00')] == 10 # Vendredi
    assert cours.getValues()[pd.Timestamp('2025-02-03 00:00:00')] == 13 # Lundi

    assert dataset.getLabel().iloc[0,0] == (13 + 14 + 15 + 16 + 17) / 5

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

    # several value for 1 date
    ts["22-02-2025 00:00:00"] = 100
    ts["22-02-2025 04:00:00"] = 200

    cours: Cours = CoursBuilder.fromTimeSerie(ts, step=Frequency.CALENDAR_DAY)

    dataset: SetVector = SetVector(cours=cours, shapeVector=UnitVectorDataframe.MONTH_DAYS)
    cours = dataset.getCours()
    assert cours.getStart().toString() == '01-02-2025 00:00:00'
    assert cours.getEnd().toString() == '31-01-2026 00:00:00'

    ts = cours.getValues()
    ts.index = ts.index.strftime(TimeService.getTimeFormat())

    assert ts['31-03-2025 00:00:00'] == 69
    assert ts['01-04-2025 00:00:00'] == 70
    assert dataset.getDataFrame().iloc[1, 30] == 69
    assert ts['28-02-2025 00:00:00'] == 38
    assert ts['01-03-2025 00:00:00'] == 39
    assert ts['22-02-2025 00:00:00'] == 150
    assert ts['01-09-2025 00:00:00'] == 223
    assert ts['30-09-2025 00:00:00'] == 252

