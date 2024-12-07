from datetime import timedelta

import pytest

from src.service.TimeService import TimeService
from src.util.constants.Frequency import Frequency
from src.util.constants.UnitVectorDataframe import UnitVectorDataframe


def test_UnitDataframe():
    assert UnitVectorDataframe.getColumnsIndex(rowUnit=UnitVectorDataframe.CALENDAR_DAY, columnUnit=UnitVectorDataframe.HOURLY) == 24
    assert UnitVectorDataframe.getColumnsIndex(rowUnit=UnitVectorDataframe.MONTH_END,
                                               columnUnit=UnitVectorDataframe.HOURLY) == 24*31
    assert UnitVectorDataframe.getColumnsIndex(rowUnit=UnitVectorDataframe.WEEKLY,
                                               columnUnit=UnitVectorDataframe.BUSINESS_DAY) == 5
    assert UnitVectorDataframe.getColumnsIndex(rowUnit=UnitVectorDataframe.MONTH_END,
                                               columnUnit=UnitVectorDataframe.BUSINESS_DAY) == 23

    with pytest.raises(Exception):
        UnitVectorDataframe.getColumnsIndex(rowUnit=UnitVectorDataframe.HOURLY, columnUnit=UnitVectorDataframe.HOURLY)
    with pytest.raises(Exception):
        UnitVectorDataframe.getColumnsIndex(rowUnit=UnitVectorDataframe.HOURLY, columnUnit=UnitVectorDataframe.MONTH_END)

def test_getFrequency():
    assert UnitVectorDataframe.WEEKLY.getFrequency() == Frequency.WEEKLY


def test_getDifference():
    dateEnd: TimeService = TimeService.fromString('15-11-2024 10:00:00').round(Frequency.MONTH_END)
    dateStart: TimeService = TimeService.fromString('15-11-2024 10:00:00').round(Frequency.MONTH_START)

    result = UnitVectorDataframe.MONTH_END.getNumbersOfEnumBetweenTime(dateStart, dateEnd)
    assert result == 1
    result = UnitVectorDataframe.WEEKLY.getNumbersOfEnumBetweenTime(dateStart, dateEnd)
    assert result == 3
    result = UnitVectorDataframe.CALENDAR_DAY.getNumbersOfEnumBetweenTime(dateStart, dateEnd)
    assert result == 30

    dateEnd: TimeService = TimeService.fromString('15-12-2025 10:00:00').round(Frequency.MONTH_END)
    dateStart: TimeService = TimeService.fromString('15-01-2024 10:00:00').round(Frequency.MONTH_START)

    result = UnitVectorDataframe.WEEKLY.getNumbersOfEnumBetweenTime(dateStart, dateEnd)
    assert result == 103
    with pytest.raises(Exception):
        UnitVectorDataframe.WEEKLY.getNumbersOfEnumBetweenTime(dateEnd, dateStart)
