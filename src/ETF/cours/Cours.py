import math

import pandas as pd

from src.service.TimeService import TimeService
from src.util.constants.Frequency import Frequency
from src.util.constants.TimeReference import TimeReference


class Cours:
    def __init__(self, values: pd.Series, frequency: Frequency, isVariation: bool = False):

        '''
        Possede la responsabilite de verifier que les valeurs sont cleans
        :param values: Time serie avec index datetime format seulement
        :param frequency:
        '''

        if (not isinstance(values.index, pd.DatetimeIndex)):
            raise Exception(f"Time serie must have index in date time.")

        self.__values: pd.Series = values.sort_index()

        self.__values = TimeService.convertTimeFormat(self.__values).apply(Cours.__roundToSignificant)

        self.__start: TimeService = TimeService.fromString(self.__values.index[0].strftime(TimeService.getTimeFormat()))
        self.__end: TimeService = TimeService.fromString(self.__values.index[-1].strftime(TimeService.getTimeFormat()))
        self.__isVariation: bool = isVariation
        self.__frequency: Frequency = frequency

    def getStart(self) -> TimeService:
        return self.__start

    def getEnd(self) -> TimeService:
        return self.__end

    def getFrequency(self) -> Frequency:
        return self.__frequency

    def getValues(self) -> pd.Series:
        return self.__values

    def isVariation(self) -> bool:
        return self.__isVariation

    def shorten(self, date: TimeService, reference: TimeReference) -> 'Cours':

        if date.isBefore(self.getStart()) | date.isAfter(self.getEnd()):
            raise Exception(f"Can not shorten with this date {date.toString()}")

        if reference == TimeReference.FROM_BEGINNING:
            return Cours(self.__values.truncate(before=date.toString()), self.__frequency)

        if reference == TimeReference.FROM_END:
            return Cours(self.__values.truncate(after=date.toString()), self.__frequency)

    def toVariation(self) -> 'Cours':
        '''
        [1, 2, 4, 2, 1, 1.5, 0.5] -> [0.00, 100.00, 100.00, -50.00, -50.00, 50.00, -66.67]
        '''

        return Cours(((self.__values - self.__values.shift(1)) * 100 / self.__values.shift(1)).fillna(0),
                     self.__frequency, isVariation=True)

    @staticmethod
    def __roundToSignificant(x, significantDigits=4):
        if x == 0:
            return 0
        else:
            try:
                # Calculer le facteur d'échelle pour arrondir à 3 chiffres significatifs
                scale = significantDigits - int(math.floor(math.log10(abs(x)))) - 1
                return round(x, scale)
            except ValueError:
                pass # cas des Nan Value
            except TypeError:
                pass

