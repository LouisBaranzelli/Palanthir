
from datetime import datetime, timedelta
from typing import Union

import pandas as pd

from src.service.LogService import LogService
from src.util.constants.Frequency import Frequency
from src.util.constants.UpDown import UpDown


class TimeService:
    __format = '%d-%m-%Y %H:%M:%S'

    def __init__(self, year: int = 0, month: int = 0, day: int = 0, hour: int = 0, minute: int = 0,
                 seconde: int = 0):
        self.__time: datetime = datetime(year, month, day, hour, minute, seconde)

    def addDay(self, d: int) -> 'TimeService':
        delta = timedelta(days=d)
        time = self.__time + delta
        return TimeService(time.year, time.month, time.day, time.hour, time.second)

    def toString(self) -> str:
        return self.__time.strftime(TimeService.__format)

    def __eq__(self, other):
        return self.toString() == other.toString()

    @staticmethod
    def convertTimeFormat(df: Union[pd.DataFrame, pd.Series]) -> Union[pd.DataFrame, pd.Series]:

        df.index = pd.to_datetime(df.index, format=TimeService.getTimeFormat())
        return df

    def __new__(cls, year: int = 0, month: int = 0, day: int = 0, hour: int = 0, minute: int = 0, second: int = 0):
        if TimeService.__format is None:
            LogService().debug(f"Date format: {cls.__format}.")
        return super().__new__(cls)

    def isAfter(self, date: 'TimeService'):
        return self.__time > date.getDateTime()

    def isBefore(self, date: 'TimeService'):
        return self.__time < date.getDateTime()

    def round(self, unit: Frequency, upDown: UpDown = UpDown.Up) -> 'TimeService':

        '''

        :param unit:
        :param upDown: Si Frequency est DAYLY ou WEEKLY, arrondit superieur ou inferieur
        :return:
        '''

        time: datetime = self.__time
        if unit in [Frequency.CALENDAR_DAY, Frequency.BUSINESS_DAY]:
            if self.__time.hour != 0 or self.__time.minute != 0 or self.__time.second != 0 or self.__time.microsecond != 0:
                time = self.__time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=upDown.value)

        elif unit  in [Frequency.MONTH_END, Frequency.MONTH_START]:
            isNotRound: bool = self.__time.day != 1 or self.__time.hour != 0 or self.__time.minute != 0 or self.__time.second != 0 or self.__time.microsecond != 0
            if isNotRound and unit == Frequency.MONTH_END and upDown == UpDown.Up:
                if self.__time.month == 12:
                    time = self.__time.replace(year=self.__time.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                else:
                    time = self.__time.replace(month=self.__time.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else: # Frequency.MONTH_START
                    time = self.__time.replace(month=self.__time.month, day=1, hour=0, minute=0, second=0,
                                                   microsecond=0)

        elif unit in [Frequency.WEEKLY]:
            isNotRound: bool = self.__time.weekday() != 0 or self.__time.hour != 0 or self.__time.minute != 0 or self.__time.second != 0 or self.__time.microsecond != 0
            if isNotRound:
                remainDay: int = 7 - self.__time.weekday() if upDown == UpDown.Up else - self.__time.weekday()
                time = self.__time + timedelta(days=remainDay)
                LogService.debug(f'Round date: {self.__time} with: {unit}/{upDown} -> {time}')
                time = TimeService(time.year, time.month, time.day, time.hour, time.second).round(unit=Frequency.CALENDAR_DAY, upDown=UpDown.Down).getDateTime()

        elif unit in [Frequency.YEAR_END, Frequency.YEAR_START]:
            isNotRound: bool = self.__time.month != 1 or self.__time.day != 1 or self.__time.hour != 0 or self.__time.minute != 0 or self.__time.second != 0 or self.__time.microsecond != 0
            if isNotRound and unit == Frequency.YEAR_END:
                time = self.__time.replace(year=self.__time.year + 1, month=1, day=1, hour=0, minute=0, second=0,
                                                  microsecond=0)
            else:
                time = self.__time.replace(year=self.__time.year, month=1, day=1, hour=0, minute=0, second=0,
                                                  microsecond=0)

        else:
            raise(ValueError(f'Format not take in charge yet: {unit}'))

        LogService.debug(f'Round date: {self.__time} with: {unit}/{upDown} -> {time}')
        return TimeService(time.year, time.month, time.day, time.hour, time.second)


    @staticmethod
    def getTimeFormat() -> str:
        return TimeService.__format

    @staticmethod
    def fromString(d: str) -> 'TimeService':
        t = datetime.strptime(d, TimeService.__format)
        return TimeService(t.year, t.month, t.day, t.hour, t.minute, t.second)

    def getDateTime(self) -> datetime:
        return self.__time

    @staticmethod
    def setTimeFormart(s: str):
        TimeService.__format = s

    @staticmethod
    def getNumbersOfEnumBetweenTime(frequency: Frequency, dateStart: 'TimeService', dateEnd: 'TimeService'):
        '''
        return the delta datetime function accordingly to the ennum
        '''

        delta: timedelta = dateEnd.getDateTime() - dateStart.getDateTime()

        if dateStart.isAfter(dateEnd):
            raise Exception(f"dateStart: {dateStart.toString()} is after dateEnd: {dateEnd.toString()}")

        if frequency == Frequency.HOURLY:
            return int(delta.total_seconds() / 3600)  # Convertit en heures

        if frequency == Frequency.CALENDAR_DAY:
            return delta.days

        if frequency == Frequency.WEEKLY:
            roundStartWeek: TimeService = dateStart.round(Frequency.WEEKLY, upDown=UpDown.Up)
            roundEndWeek: TimeService = dateEnd.round(Frequency.WEEKLY, upDown=UpDown.Down)
            return (roundEndWeek.getDateTime() - roundStartWeek.getDateTime()).days // 7

        if frequency == Frequency.MONTH_END:
            yearsDiff = dateEnd.getDateTime().year - dateStart.getDateTime().year
            monthsDiff = dateEnd.getDateTime().month - dateStart.getDateTime().month
            return yearsDiff * 12 + monthsDiff

        else:
            raise ValueError("Unité non supportée pour cette différence de temps")


