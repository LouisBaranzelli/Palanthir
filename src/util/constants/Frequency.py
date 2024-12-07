from enum import Enum


class Frequency(Enum):
    # non utilisable directement car plusieurs eenum peuvent avoir la meme valeur
    BUSINESS_DAY = 'WORKING_DAY'
    CALENDAR_DAY = "CALENDAR_DAY"  # Jour calendaire
    WEEKDAYS = 'WEEKDAYS'
    WEEKLY = 'WEEKLY'
    MONTH_END = "MONTH_END"  # Fin de mois
    MONTH_START = 'MONTH_START'
    YEAR_START = 'YEAR_START'
    YEAR_END = 'YEAR_END'
    HOURLY = 'HOURLY'


    def getValue(self) -> str:
        '''
        Frequence pandas
        '''
        formats = {
            Frequency.BUSINESS_DAY: "B",
            Frequency.WEEKDAYS: "D",
            Frequency.MONTH_END: "M",
            Frequency.CALENDAR_DAY: "D",
            Frequency.WEEKLY:"W"
        }
        return formats.get(self, "unknown frequency")

    @staticmethod
    def getFrequencyFromValue(s: str) -> 'Frequency':
        for freq in Frequency:
            if freq.value == s:
                return freq
        raise (Exception(f"This frequency does not exist: {s}"))

    # @classmethod
    # def fromName(cls, name):
    #     try:
    #         return cls[name]
    #     except KeyError:
    #         raise ValueError(f"No Frequency found with name '{name}'")

    def getDatetimeFormat(self) -> str:

        formats = {
            # Frequency.BUSINESS_DAY: "YYYY-MM-DD",
            # Frequency.CUSTOM_BUSINESS_DAY: "YYYY-MM-DD",
            Frequency.CALENDAR_DAY: "YYYY-MM-DD",
            Frequency.BUSINESS_DAY: "YYYY-MM-DD",
            Frequency.WEEKLY: "YYYY-WW",
            Frequency.MONTH_END: "YYYY-MM",
            # Frequency.MONTH_START: "YYYY-MM",
            # Frequency.QUARTER_END: "YYYY-Q",
            # Frequency.QUARTER_START: "YYYY-Q",
            # Frequency.YEAR_END: "YYYY",
            # Frequency.YEAR_START: "YYYY",
            # Frequency.HOURLY: "YYYY-MM-DD HH",

        }
        return formats.get(self, "unknown format")

    def getLabel(self) -> str:
        labels = {
            # Frequency.BUSINESS_DAY: "business day",
            # Frequency.CUSTOM_BUSINESS_DAY: "custom business day",
            Frequency.CALENDAR_DAY: "day",
            Frequency.WEEKLY: "week",
            Frequency.MONTH_END: "month",
            Frequency.BUSINESS_DAY: "day of week",
            # Frequency.MONTH_START: "month",
            # Frequency.QUARTER_END: "quarter",
            # Frequency.QUARTER_START: "quarter",
            # Frequency.YEAR_END: "year",
            # Frequency.YEAR_START: "year",
            # Frequency.HOURLY: "hour",

        }
        return labels.get(self, "unknown frequency")

    def getDatetimeIndexFormat(self, light: bool = False) -> str:

        '''
        strinf format date time.
        Le format peut dependre de parametre exterieur: une journe peut etre de 1-31 ou de 1 a 7. (Pandas commence a 0
        pour les jours de la semaine)
        '''

        formats = {
            Frequency.BUSINESS_DAY: "%Y-%m-%d",
            Frequency.CALENDAR_DAY: "%Y-%m-%d",
            Frequency.MONTH_END: "%Y-%m",
            Frequency.MONTH_START: "%Y-%m",
            Frequency.YEAR_END: "%Y",
            Frequency.YEAR_START: "%Y",
            Frequency.HOURLY: "%Y-%m-%d %H",
            Frequency.WEEKLY: "%Y-W%W",
            Frequency.WEEKDAYS: "%Y-%m-%d",
        }

        formatsLight = {

            # Format pour une fréquence de jour ouvré personnalisé : également le jour du mois en deux chiffres.
            Frequency.CALENDAR_DAY: "%d",
            # Format pour une fréquence de jour calendaire : le jour du mois en deux chiffres.
            Frequency.WEEKLY: "W%W",
            # Format pour une fréquence hebdomadaire : semaine de l'année (W suivi du numéro de la semaine).
            Frequency.MONTH_END: "%m",  # Format pour une fréquence de fin de mois : mois en deux chiffres.
            Frequency.MONTH_START: "%m",  # Format pour une fréquence de début de mois : mois en deux chiffres.
            # Format pour une fréquence de fin de trimestre : trimestre (Q suivi du numéro du trimestre).
            # Format pour une fréquence de début de trimestre : trimestre (Q suivi du numéro du trimestre).
            Frequency.YEAR_END: "%Y",  # Format pour une fréquence de fin d'année : année en quatre chiffres.
            Frequency.YEAR_START: "%Y",  # Format pour une fréquence de début d'année : année en quatre chiffres.
            Frequency.HOURLY: "%H",  # Format pour une fréquence horaire : heure en deux chiffres (de 00 à 23).
            Frequency.BUSINESS_DAY: "%u",
            Frequency.WEEKDAYS: "%u"

        }
        return formats.get(self, None) if not light else formatsLight.get(self, None)
