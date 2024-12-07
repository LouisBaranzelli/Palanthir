from typing import Callable

import pandas as pd
from pandas import Index

from src.ETF.cours.Cours import Cours
from src.service.LogService import LogService
from src.service.TimeService import TimeService


class SanityCheck():

    def __init__(self, missingValueStrategy: Callable[[pd.Series], float] = lambda window:window.mean(), thresholdWrongValue: float = 0.05):

        self.__missingValueStrategy : Callable = missingValueStrategy
        self.__threshold = thresholdWrongValue

    def cleanAndFillMissingValue(self, cours: Cours) -> Cours:

        '''
        Complete les valeur manquante en fonction d'un callable appele sur une window de la TS de taille fixe
        :param cours:
        :return:
        '''

        LogService.debug(f'[SANITY CHECK] Start')
        ts: pd.Series = cours.getValues()

        ts = pd.to_numeric(ts, errors='coerce')
        nbrWrongValue = ts.isna().sum()
        if (nbrWrongValue / len(ts)) > self.__threshold:
            raise Exception (f"To much N/A Value or non-numeric values: {round(nbrWrongValue / len(ts) * 100, 2)}%")
        elif nbrWrongValue > 0:
            LogService.info(f'[SANITY CHECK] {nbrWrongValue} rows have been deleted.')
            ts = ts.dropna()
            cours = Cours(ts, cours.getFrequency())

        if len(ts) == 0:
            raise Exception (f"[SANITY CHECK] Empty serie.")

        firstDateTimeStamp = pd.to_datetime(cours.getStart().toString(), format=TimeService.getTimeFormat())
        lstDateTimeStamp = pd.to_datetime(cours.getEnd().toString(), format=TimeService.getTimeFormat())

        allDates: Index = pd.date_range(start=firstDateTimeStamp, end=lstDateTimeStamp, freq=cours.getFrequency().getValue())
        WINDOW_SIZE_POURCENTAGE: float = 0.05
        windowSize = int(len(allDates) * WINDOW_SIZE_POURCENTAGE)

        # verifier que la ts soit plus grande que la windos:
        previousDate: pd.Timestamp = None
        for date in allDates:
            if date not in ts.index:
                position: int = ts.index.get_loc(previousDate) # last date valid (la premiere est valid car utilise pour cree alldates)
                previousValidValue: pd.Series = ts.iloc[max(0, position - windowSize):position+1]
                ts[date] = self.__missingValueStrategy(previousValidValue)
                ts = ts.sort_index()
            previousDate = date



        return Cours(ts, cours.getFrequency())

