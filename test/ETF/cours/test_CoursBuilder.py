import pathlib
from typing import List

import pandas as pd
import pandas.testing as pdt


from src.ETF.cours.Cours import Cours
from src.ETF.cours.CoursBuilder import CoursBuilder
from src.service.TimeService import TimeService
from src.util.constants.Frequency import Frequency
from src.util.constants.TimeReference import TimeReference


class TestCoursBuilder:

    def test_fromList(self):

        valuesList: List = [15, 18, 17, 16, 14, 19, 20, 21, 22, 23, 24]
        startDateStr = '15-03-2023 10:00:00'

        coursDay: Cours = CoursBuilder.fromList(valuesList, TimeService.fromString(startDateStr), Frequency.CALENDAR_DAY)
        coursDayReverse: Cours = CoursBuilder.fromList(valuesList, TimeService.fromString(startDateStr),
                                                       Frequency.CALENDAR_DAY, TimeReference.FROM_END)
        cours_hours: Cours = CoursBuilder.fromList(valuesList, TimeService.fromString(startDateStr), Frequency.HOURLY)

        assert coursDay.getStart().toString() == startDateStr
        assert coursDay.getEnd().toString() == f"{15+len(valuesList)-1}-03-2023 10:00:00"
        assert coursDay.getFrequency() == Frequency.CALENDAR_DAY
        assert (coursDay.getValues().iloc[:] == valuesList).all()

        assert f"05-03-2023 10:00:00" == coursDayReverse.getStart().toString()
        assert coursDayReverse.getEnd().toString() == f"15-03-2023 10:00:00"

        assert cours_hours.getStart().toString() == startDateStr
        assert cours_hours.getFrequency() == Frequency.HOURLY
        assert cours_hours.getEnd().toString() == f"15-03-2023 {10+len(valuesList) - 1}:00:00"
        assert pd.api.types.is_datetime64_any_dtype(cours_hours.getValues().index)

    def test_fromCsv(self):
        cours: Cours = CoursBuilder.fromCsv(pathlib.Path('test.csv'), Frequency.CALENDAR_DAY, separator=',', timeFormat='%Y-%m-%d')
        assert f"03-01-2023 00:00:00" == cours.getStart().toString()

        cours = CoursBuilder.fromCsv(pathlib.Path('total_d.txt'), Frequency.CALENDAR_DAY, separator='\t', column=2, timeFormat='%d/%m/%Y %H:%M')
        assert cours.getValues().iloc[0] == 60.270
        assert cours.getValues().index[0].strftime(TimeService.getTimeFormat()) == '09-11-2023 00:00:00'


