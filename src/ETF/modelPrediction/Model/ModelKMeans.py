import pathlib
from typing import Optional, List

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split

from src.ETF.cours.CoursBuilder import CoursBuilder
from src.ETF.modelPrediction.Dataset.SetDataframe import SetDataframe
from src.ETF.modelPrediction.Dataset.SetVector import SetVector
from src.ETF.modelPrediction.Dataset.IDataset import IDataset
from src.ETF.modelPrediction.Dataset.UtilityDataset import UtilityDataset
from src.ETF.modelPrediction.Model.ElbowMethod import ElbowMethod
from src.service.LogService import LogService
from src.util.constants.Frequency import Frequency
from src.util.constants.UnitVectorDataframe import UnitVectorDataframe


class ModelKMeans(IDataset):

    def __init__(self, dataset: IDataset, k: Optional[int] = None, verbose: bool = True):

        if verbose:
            LogService.info(f' [MODEL] Initializing ModelKMeans with k = {k}')

        self.__xTrain, self.__xTest = UtilityDataset.split(dataset, 0.5)
        self.__dataset: IDataset = dataset
        if k is None:
            inertias: List[float] = []
            k_values = range(1, len(self.__xTrain // 3))
            for v in tqdm(k_values, 'Optimal k Calculation'):
                model = ModelKMeans(dataset, v, verbose=False)
                inertias.append(model.getTestResult())
            k = ElbowMethod.byDerivativeMethod(k_values, inertias)
            LogService.debug(f"[MODEL] k_values: {k_values}, inertia: {inertias}")

        self.__model = KMeans(n_clusters=k, random_state=42)
        self.train()
        if verbose:
            LogService.info(f' [MODEL] ModelKMeans completed, with k = {k}, error associated: {self.getTestResult()}')

    def train(self):
        self.__model.fit(self.__xTrain)

    def predict(self, data: IDataset) -> IDataset:

        outputs = self.__model.predict(data.getData())
        predictions = pd.DataFrame([self.__model.cluster_centers_[prediction] for prediction in outputs])
        predictions.index = data.getData().index
        return SetDataframe(predictions, data.getLabel(), data.getDimInput())

    def getTestResult(self) -> float:
        '''
        :return: La valeur moyenne de l'ecart entre predict et true
        '''

        results = self.__model.predict(self.__xTest)
        predictions = pd.DataFrame([self.__model.cluster_centers_[prediction] for prediction in results])
        predictions.index = self.__xTest.index
        return abs(predictions.sum(axis=1) - self.__xTest.sum(axis=1)).sum() / len(self.__xTest)

    def getDimInput(self) -> int:
        return self.__dataset.getDimInput()

    def run(self, dataset: 'IDataset') -> 'IDataset':
        pass

    def getData(self) -> pd.DataFrame:
        output: pd.DataFrame = pd.DataFrame(self.__model.predict(self.__dataset.getData()))
        output.index = self.__dataset.getData().index
        return output

    def getLabel(self) -> pd.DataFrame:
        pass


cours = CoursBuilder.fromCsv(pathlib.Path('total_d.txt'), Frequency.CALENDAR_DAY, separator='\t', column=2,
                             timeFormat='%d/%m/%Y %H:%M').toVariation()
dataset: IDataset = SetVector(cours, shapeVector=UnitVectorDataframe.WORKINGDAYSWEEK_DAYS)

v = ModelKMeans(dataset).getData()
pass
