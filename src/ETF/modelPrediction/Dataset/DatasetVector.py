from typing import Callable, Tuple

import numpy as np
import pandas as pd
from pandas import DatetimeIndex, Index

from src.ETF.cours.Cours import Cours
from src.ETF.cours.CoursBuilder import CoursBuilder
from src.ETF.modelPrediction.Dataset.IDataset import IDataset
from src.service.LogService import LogService
from src.service.TimeService import TimeService
from src.util.constants.UnitVectorDataframe import UnitVectorDataframe
from src.util.constants.UpDown import UpDown


class DatasetVector(IDataset):
    def __init__(self, cours: Cours, shapeVector: UnitVectorDataframe,
                 severalValueMatching:Callable[[pd.Series], float] = lambda row:row.mean(),
                 missingValueStrategy: Callable[[pd.Series], float] = lambda row:0 ,
                 yValueStrategy: Callable[[pd.Series], float] = lambda row: row.mean(),
                 ratioSplitTest=0.2):

        '''
        Objectif
        Transformer les données des cours en un dataset composé de vecteurs de taille uniforme. Les premières et dernières dates
        seront tronquées pour s’adapter à la fréquence choisie, garantissant des périodes complètes.

        Cette transformation doit également gérer les cas suivants :
        Dates inexistantes : Par exemple, le 31 février, qui peut être présent dans un vecteur (comme dans le cas d'un mois standardisé à 31 jours), mais inexistant dans les données réelles.
        Consolidation temporelle : Adapter les données pour des périodes spécifiques comme des semaines ou des jours, en ajustant les index et les valeurs.

        Exemples
        Avant transformation :
        [Lundi 01/01, Mardi 02/01, ..., Mercredi 12/12] (longueur = 365, échelle journalière)
        Après transformation :
        [Lundi 01/01, ..., Dimanche 07/01] (longueur = 52, échelle hebdomadaire)

        :param cours:
        :param shapeVector: Strategie de vectorisation
        :param severalValueMatching: Strategie dans le cas ou plusieurs valeurs correspondent a une date du Vecteur
        :param missingValueStrategy: Strategie pour ajouter lors de l'ajout de valeurs des dates creees
        :param yValueStrategy: Strategie pour labeliser la row n sur la base de la row n+1
        :param ratioSplitTest:

        '''

        LogService.info(f"[DatasetVector] Attempt to create DatasetVector, shape: {shapeVector}")

        self.__cours: Cours = cours
        self.__shapeVector: UnitVectorDataframe = shapeVector

        self.__severalValueMatchingStrategy: Callable = severalValueMatching
        self.__yValueStrategy: Callable = yValueStrategy
        self.__rowFrequency = self.__shapeVector.getRowFrequency()
        self.__colFrequency = self.__shapeVector.getColFrequency()
        self.__missingValueStrategy = missingValueStrategy

        # Tronque le cours pour que ca commence sur un vecteur entier
        firstDate: TimeService = self.__cours.getStart().round(unit=self.__rowFrequency, upDown=UpDown.Up)
        lastDate: TimeService = self.__cours.getEnd().round(unit=self.__rowFrequency, upDown=UpDown.Down)
        LogService.debug(f"[DatasetVector] First Date: {firstDate.toString()}, Last Date: {lastDate.toString()}")
        if firstDate.isAfter(lastDate):
            raise Exception(f"Round: {self.__rowFrequency}. First date {cours.getStart().toString()}, rounded in {self.__firstDate.toString()} is after last date {cours.getEnd().toString()} rounded in {lastDate.toString()}:")

        # Cree le df avec le bon nombre de lignes et de colones
        nbrLigne: int = TimeService.getNumbersOfEnumBetweenTime(self.__rowFrequency, firstDate, lastDate)
        nbrColonne: int = len(self.__shapeVector.getColumnsIndex())
        LogService.debug(f"[DatasetVector] Final dimension of the dataframe col: {nbrColonne}, row: {nbrLigne}")

        if any(val in [nbrLigne, nbrColonne] for val in [0, 1]):
            raise Exception(f"Not enought data to make the dataframe of vector: col: {nbrColonne}, row: {nbrLigne}")

        # Creation des indexs des rows
        self.__firstDateTimeStamp = pd.to_datetime(firstDate.toString(), format=TimeService.getTimeFormat())
        dates = pd.date_range(start=self.__firstDateTimeStamp, periods=nbrLigne, freq=self.__rowFrequency.getValue())

        df = pd.DataFrame(None, index=dates, columns=[f"{self.__colFrequency.getLabel()} {indexCol}" for indexCol in range(nbrColonne)])
        df.index = pd.to_datetime(df.index, format=self.__rowFrequency.getDatetimeIndexFormat())
        df = self.__fillDataframe(df)

        df['y'] = df.apply(lambda row: row.mean(), axis=1)
        df['y']  = df['y'] .shift(-1)
        df = df.iloc[:-1] # derniere ligne invalide car y = nan
        # ! self.__df ne contient pas les valeurs Y car dimension importante pour generer les indexs du cours
        self.__df = df.iloc[:,:-1].copy()
        super().__init__(df, ratioSplitTest)
        LogService.info(f"[DatasetVector] Completed")

    def __fillDataframe(self,df: pd.DataFrame):

        '''
        Méthode interne pour remplir et compléter le DataFrame. Il s'agit de vecteurs de même taille représentant des
        objets de taille variable (les mois peuvent avoir 30 ou 31 jours). Les valeurs sont complétées selon les
        stratégies fournies en argument.
        '''

        datesIndexCol = self.__shapeVector.getColumnsIndex()

        rowDatetimeIndexFormat = self.__rowFrequency.getDatetimeIndexFormat()
        colDatetimeIndexFormat = self.__colFrequency.getDatetimeIndexFormat(light=True)  # light: not 12/12/2022 mais seulement 12
        if None in [rowDatetimeIndexFormat, colDatetimeIndexFormat]:
            raise Exception(f"Unknown format associated to enum: {self.__rowFrequency}")

        coursValues = self.__cours.getValues()
        self.__unexistingValueToFilter: list = []

        # Toutes les date qui devront etre presentes dans la serie finale
        allDates: Index = pd.date_range(start=self.__firstDateTimeStamp, periods=df.shape[0]*df.shape[1], freq=self.__colFrequency.getValue())

        for i, (indexRow, row) in enumerate(df.iterrows()):
            for indexCol, (_, value) in enumerate(row.items()):
                result = coursValues[
                    (coursValues.index.strftime(rowDatetimeIndexFormat) == indexRow.strftime(rowDatetimeIndexFormat)) &
                    (coursValues.index.strftime(colDatetimeIndexFormat) == datesIndexCol[indexCol])]
                if not result.empty:
                    row[indexCol] = self.__severalValueMatchingStrategy(result)
                else:
                    # si pas present soit date valide et donnee manquante soit date invalide
                    resultExist = ((allDates.strftime(rowDatetimeIndexFormat) == indexRow.strftime(rowDatetimeIndexFormat)) &
                    (allDates.strftime(colDatetimeIndexFormat) == datesIndexCol[indexCol]))
                    if resultExist.any(): # cas ou la date est correcte mais la donnee est manquante
                        raise Exception (f'Missing Value: {indexRow.strftime(rowDatetimeIndexFormat)} {datesIndexCol[indexCol]}')
                    else: # cas ou  la date n'existe pas (31 Fevrier)
                        row[indexCol] = self.__missingValueStrategy(row)
                        if row[indexCol] == np.nan:
                            raise Exception("A non-existing date can not be replaced by Nan Value")
                        self.__unexistingValueToFilter.append((i, indexCol))

        error = len(self.__unexistingValueToFilter) * 100 / df.size
        if error > 2:  # a A dapter, mais 3% semble le maximal possible, en general 0.5 jours par mois, soit 1.5% normalement
            raise Exception(f"Number of no-existing value anormaly hight: got {error}%")

        return df

    def getCours(self) -> Tuple[Cours, Cours]:
        '''
        Retourne les cours issus des Dataframe avec les index initiaux
        :return: Train cours, Validation cours
        '''

        # Creation des indexs a filtrer
        indexValuesToFilter = [r * self.__df.shape[1] + c for r, c in self.__unexistingValueToFilter]
        dfTrain = super().getXTrain().T.melt().iloc[:,1]
        indexTrainToFilters = [indexValueToFilter for indexValueToFilter in indexValuesToFilter if indexValueToFilter < len(dfTrain)]

        dfTest = super().getXTest().T.melt().iloc[:,1]
        indexValuesToFilter = [i - len(dfTrain) for i in indexValuesToFilter]
        indexTestToFilters = [indexValueToFilter for indexValueToFilter in indexValuesToFilter if
                              indexValueToFilter >= 0]

        # Suppression des dates impossible comme le 31 Fevrier
        for indexTrainToFilter in indexTrainToFilters:
            dfTrain.iloc[indexTrainToFilter] = np.nan
        dfTrain = dfTrain.dropna() # dropna pour supprimer d'un coup toutes les valeurs inutiles

        for indexTestToFilter in indexTestToFilters:
            dfTest.iloc[indexTestToFilter] = np.nan
        dfTest = dfTest.dropna()

        # Ajout des indexes
        datesIndex: Index = pd.date_range(start=self.__firstDateTimeStamp, periods=len(dfTrain) + len(dfTest),
                                          freq=self.__shapeVector.getColFrequency().getValue())
        dateIndexTrain = datesIndex[:len(dfTrain)]
        dateIndexTest = datesIndex[len(dfTrain):]

        dfTrain.index = dateIndexTrain
        dfTest.index = dateIndexTest
        return CoursBuilder.fromTimeSerie(dfTrain, self.__colFrequency, sanityCheck=False), CoursBuilder.fromTimeSerie(dfTest, self.__colFrequency, sanityCheck=False)

