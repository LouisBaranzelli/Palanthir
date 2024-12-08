
from enum import Enum

import pandas as pd

from src.util.constants.Frequency import Frequency


class UnitVectorDataframe(Enum):
    '''
    Nombre d'heures connues unite de temps
    '''

    MONTH_DAYS = 'row: Month columns: Days'
    WEEK_DAYS = 'row: Week columns: Days'
    WORKINGDAYSWEEK_DAYS = 'row: Working days week columns: Days'

    def getUnitLength(self) -> int:
        length = {

            UnitVectorDataframe.MONTH_DAYS: 31,
            UnitVectorDataframe.WEEK_DAYS: 7,
            UnitVectorDataframe.WORKINGDAYSWEEK_DAYS: 5,
        }
        return length.get(self, "unknown key")

    def getColFrequency(self) -> Frequency:
        frequency = {
            UnitVectorDataframe.MONTH_DAYS: Frequency.CALENDAR_DAY, # 1 - 31
            UnitVectorDataframe.WEEK_DAYS: Frequency.WEEKDAYS, # 1 - 7, avec Lundi
            UnitVectorDataframe.WORKINGDAYSWEEK_DAYS: Frequency.BUSINESS_DAY,# 1 - 5 inclus dans 1 - 7
        }

        return frequency.get(self, "unknown key")

    def getRowFrequency(self) -> Frequency:
        frequency = {
            UnitVectorDataframe.MONTH_DAYS: Frequency.MONTH_END,
            UnitVectorDataframe.WEEK_DAYS: Frequency.WEEKLY,
            UnitVectorDataframe.WORKINGDAYSWEEK_DAYS: Frequency.WEEKLY,
        }

        return frequency.get(self, "unknown key")

    def getColumnsIndex(self) -> str:
        '''
         Génère un index de la colonne de dates sous forme de `DatetimeIndex` en fonction des unités de row.
        '''

        indexCol = {
            UnitVectorDataframe.MONTH_DAYS: pd.Series(range(1, 32)).apply(lambda x: f"{x:02d}"),
            UnitVectorDataframe.WEEK_DAYS: pd.Series(range(1, 8)).apply(lambda x: str(x)),
            UnitVectorDataframe.WORKINGDAYSWEEK_DAYS: pd.Series(range(1, 6)).apply(lambda x: str(x))
        }

        return indexCol.get(self, "unknown key")

    # def getSerieFrequency(self) -> Frequency:
    #     frequency = {
    #         UnitVectorDataframe.MONTH_DAYS: Frequency.CALENDAR_DAY,
    #         UnitVectorDataframe.WEEK_DAYS: Frequency.CALENDAR_DAY,
    #         UnitVectorDataframe.WORKINGDAYSWEEK_WEEK: Frequency.CALENDAR_DAY
    #     }
    #
    #     return frequency.get(self, "unknown key")