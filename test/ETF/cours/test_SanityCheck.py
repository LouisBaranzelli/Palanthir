from typing import List

import pandas as pd
from pandas import Index

from src.ETF.cours.Cours import Cours
from src.ETF.cours.CoursBuilder import CoursBuilder
from src.ETF.cours.SanityCheck import SanityCheck
from src.service.TimeService import TimeService
from src.util.constants.Frequency import Frequency


class TestSanityCheck:

    def test_fillMissingValue(self):

        valuesList: List = list(range(101))
        ts = pd.Series(valuesList)
        date = TimeService.fromString('01-01-2025 10:00:00')
        datesIndex: Index = pd.date_range(start=date.toString(),
                                          periods=len(valuesList),
                                          freq='D')
        ts.index = datesIndex
        # la premiere valeur de la semaine est invalide
        for date in ["2025-01-05 10:00:00", "2025-01-06 10:00:00", "2025-01-07 10:00:00"]:
            ts = ts.drop(index=date)
        ts["2025-01-01 10:00:00"] = 'Faux'
        ts["2025-01-12 10:00:00"] = 'Faux'
        ts["2025-01-15 10:00:00"] = None
        ts["2025-04-09 10:00:00"] = None
        ts["2025-04-11 10:00:00"] = None

        cours: Cours = CoursBuilder.fromTimeSerie(ts, step=Frequency.CALENDAR_DAY, sanityCheck=False)
        sanitisedCours: Cours = SanityCheck(thresholdWrongValue=0.07).cleanAndFillMissingValue(cours)

        ts = sanitisedCours.getValues()

        assert sanitisedCours.getStart().toString() == "02-01-2025 10:00:00"
        assert ts["2025-01-05 10:00:00"] == (1 + 2 + 3)/3
        assert ts["2025-04-09 10:00:00"] == (97 + 96 + 95 + 94 + 93)/5
        assert ts["2025-01-6 10:00:00"] == 2
        assert ts["2025-01-7 10:00:00"] == 2
        assert ts["2025-01-12 10:00:00"] == (10 + 9 +8 + 7 + 2) / 5
