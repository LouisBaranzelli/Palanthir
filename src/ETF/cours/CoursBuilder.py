import pathlib
from typing import List

import pandas as pd

from src.ETF.cours.Cours import Cours
from src.ETF.cours.SanityCheck import SanityCheck
from src.service.TimeService import TimeService
from src.util.constants import Frequency
from src.util.constants.TimeReference import TimeReference


class CoursBuilder:

    @staticmethod
    def fromList(values: List, dateReference: TimeService, step: Frequency, reference: TimeReference = TimeReference.FROM_BEGINNING, sanityCheck: bool = True, sanitiser: SanityCheck = SanityCheck()) -> Cours:

        dateReference = pd.to_datetime(dateReference.toString(), format=TimeService.getTimeFormat())
        if reference == TimeReference.FROM_BEGINNING:
            dates = pd.date_range(start=dateReference, periods=len(values), freq=step.getValue())
        else:
            dates = pd.date_range(end=dateReference, periods=len(values), freq=step.getValue())

        return CoursBuilder.fromTimeSerie(pd.Series(data=values, index=dates), step, sanityCheck=sanityCheck, sanitiser=sanitiser)



    @staticmethod
    def fromCsv(path: pathlib.Path, step: Frequency, column: int = None, separator: str = ';', timeFormat: str = TimeService.getTimeFormat(), sanityCheck: bool = True, sanitiser: SanityCheck = SanityCheck()):
        '''
        :param separator:
        :param timeFormat:
        :param path:
        :param step:
        :param column: start from 0, column used in the time serie from csv
        :return:
        '''
        df = pd.read_csv(path, sep=separator)
        df[df.columns[0]] = pd.to_datetime(df[df.columns[0]], format=timeFormat)
        df.set_index(df.columns[0], inplace=True)

        if column is None:
            column = 0
        data: pd.Series = df.iloc[:, column]

        return CoursBuilder.fromTimeSerie(data, step, sanityCheck=sanityCheck, sanitiser=sanitiser)

    @staticmethod
    def fromTimeSerie(timeSerie: pd.Series, step: Frequency, sanityCheck: bool = True, sanitiser: SanityCheck = SanityCheck()):
        '''
        Index in string in or in datetime. If string must comply with format. Can be used in Cours class.
        '''

        # todo: adapter les format pour avoir en input un index toujours en datetime
        # if pd.api.types.is_datetime64_any_dtype(timeSerie.index): # si index en datetime -> switch en string
        #     timeSerie.index = timeSerie.index.strftime(TimeService.getTimeFormat())
        if sanityCheck:
            cours: Cours = sanitiser.cleanAndFillMissingValue(Cours(timeSerie, step))
        else:
            cours: Cours = Cours(timeSerie, step)
        return cours


