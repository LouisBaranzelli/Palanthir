from typing import List

import pandas as pd
import pytest

from src.ETF.cours.Cours import Cours
from src.ETF.cours.CoursBuilder import CoursBuilder
from src.service.TimeService import TimeService
from src.util.constants.Frequency import Frequency
from src.util.constants.TimeReference import TimeReference


class TestCours:

    def test_shorten(self):
        valuesList: List = [15, 18, 17, 16, 14, 19, 20, 21, 22, 23, 24]
        date = TimeService.fromString('15-03-2023 10:00:00')
        coursBegin: Cours = CoursBuilder.fromList(valuesList, date, Frequency.CALENDAR_DAY)
        coursEnd: Cours = CoursBuilder.fromList(valuesList, date, Frequency.CALENDAR_DAY, TimeReference.FROM_END)
        assert '17-03-2023 10:00:00' == coursBegin.shorten(date.addDay(2),
                                                           TimeReference.FROM_BEGINNING).getStart().toString()
        assert '13-03-2023 10:00:00' == coursEnd.shorten(date.addDay(-2),
                                                         TimeReference.FROM_BEGINNING).getStart().toString()
        with pytest.raises(Exception):
            coursBegin.shorten(TimeService.fromString('15-02-2023 10:00:00'), TimeReference.FROM_BEGINNING)
        with pytest.raises(Exception):
            coursBegin.shorten(TimeService.fromString('15-05-2023 10:00:00'), TimeReference.FROM_BEGINNING)
        with pytest.raises(Exception):
            coursEnd.shorten(TimeService.fromString('16-03-2023 10:00:00'), TimeReference.FROM_END)
        with pytest.raises(Exception):
            coursEnd.shorten(TimeService.fromString('16-01-2023 10:00:00'), TimeReference.FROM_END)

    def test_toVariation(self):
        valuesList = [1, 2, 4, 2 ,1, 1.5, 0.5]
        date = TimeService.fromString('15-03-2023 10:00:00')
        cours: Cours = CoursBuilder.fromList(valuesList, date, Frequency.CALENDAR_DAY)
        variations: pd.Series = cours.toVariation().getValues()
        assert (variations.iloc[:7] == [0.00, 100.00, 100.00, -50.00, -50.00, 50.00, -66.67]).all()

    def test_cleanTimeSerie(self):
        valuesList = [None, 1, 2, None, 4, 5, None]
        date = TimeService.fromString('15-03-2023 10:00:00')
        cours: Cours = CoursBuilder.fromList(valuesList, date, Frequency.CALENDAR_DAY)
        assert (cours.getValues().iloc[:] == [1, 2, 3, 4, 5]).all



