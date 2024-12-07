import pandas as pd

from src.service.TimeService import TimeService
from src.util.constants.Frequency import Frequency
from src.util.constants.UpDown import UpDown


class TestTimeService:

    def test_TimeService(self):
        date = TimeService.fromString('15-03-2023 10:00:00')
        assert date.isAfter(TimeService.fromString('14-03-2023 10:00:00'))
        assert not date.isAfter(TimeService.fromString('16-03-2023 10:00:00'))
        assert date.isBefore(TimeService.fromString('14-05-2023 10:00:00'))
        assert not date.isBefore(TimeService.fromString('16-01-2023 10:00:00'))

    def test_formatTime(self):
        date_index = pd.date_range(start='2024-01-20', periods=1, freq='D')
        df = pd.DataFrame({'value': [42]}, index=date_index)
        assert TimeService.convertTimeFormat(df).index[0] == '20-01-2024 00:00:00'

    def test_round(self):
        assert TimeService.fromString('15-03-2023 10:00:00').round(Frequency.CALENDAR_DAY, UpDown.Up).toString() == '16-03-2023 00:00:00'
        assert TimeService.fromString('15-03-2023 10:00:00').round(Frequency.CALENDAR_DAY, UpDown.Down).toString() == '15-03-2023 00:00:00'
        assert TimeService.fromString('15-03-2023 10:00:00').round(Frequency.BUSINESS_DAY, UpDown.Down).toString() == '15-03-2023 00:00:00'

        assert TimeService.fromString('15-03-2023 10:00:00').round(Frequency.MONTH_END).toString() == '01-04-2023 00:00:00'
        assert TimeService.fromString('30-03-2023 10:00:00').round(Frequency.MONTH_END).toString() == '01-04-2023 00:00:00'
        assert TimeService.fromString('01-04-2023 00:00:00').round(Frequency.MONTH_END).toString() == '01-04-2023 00:00:00'
        assert TimeService.fromString('01-04-2023 00:00:00').round(Frequency.MONTH_START).toString() == '01-04-2023 00:00:00'

        assert TimeService.fromString('31-12-2023 10:00:00').round(Frequency.MONTH_END).toString() == '01-01-2024 00:00:00'
        assert TimeService.fromString('2-01-2023 10:00:00').round(Frequency.MONTH_START).toString() == '01-01-2023 00:00:00'

        assert TimeService.fromString('15-11-2024 10:00:00').round(Frequency.WEEKLY, upDown=UpDown.Up).toString() == '18-11-2024 00:00:00'
        assert TimeService.fromString('15-11-2024 10:00:00').round(Frequency.WEEKLY, upDown=UpDown.Down).toString() == '11-11-2024 00:00:00'
        assert TimeService.fromString('11-11-2024 10:00:00').round(Frequency.WEEKLY, upDown=UpDown.Down).toString() == '11-11-2024 00:00:00'
        assert TimeService.fromString('11-11-2024 00:00:00').round(Frequency.WEEKLY, upDown=UpDown.Down).toString() == '11-11-2024 00:00:00'

        assert TimeService.fromString('11-11-2024 00:00:00').round(Frequency.YEAR_END, upDown=UpDown.Down).toString() == '01-01-2025 00:00:00'
        assert TimeService.fromString('11-11-2024 00:00:00').round(Frequency.YEAR_START, upDown=UpDown.Down).toString() == '01-01-2024 00:00:00'
