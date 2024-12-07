import pathlib

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

from src.ETF.cours.Cours import Cours
from src.ETF.cours.CoursBuilder import CoursBuilder
from src.ETF.modelPrediction.Dataset.DatasetVector import DatasetWeekVectorDays, DatasetDaysVectorHours
from src.ETF.modelPrediction.Dataset.IDataset import IDataset
from src.ETF.modelPrediction.Model.IModel import IModel
from src.service.LogService import LogService
from src.util.constants.Frequency import Frequency


class ModelKMeans(IModel):

    def __init__(self, dataset: IDataset, k: int):
        super().__init__()
        self.__dataset: IDataset = dataset
        self.__model = None
        self.__k = k

        LogService.info(f'Mode used: ModelKMeans with k = {self.__k}')
        LogService.info(f'Number lines loaded for the train: {len(dataset.getXTrain())}')

    def train(self) -> IModel:
        self.__model = KMeans(n_clusters=self.__k, random_state=42)
        self.__model.fit(self.__dataset.getXTrain())
        return self

    def test(self):
        '''
        :return: La valeur moyenne de l'ecart entre predict et true
        '''

        predictions = self.__model.predict(self.__dataset.getXTest())
        self.__prediction = pd.DataFrame([self.__model.cluster_centers_[prediction] for prediction in predictions])
        self.__prediction.index = self.__dataset.getXTest().index
        return abs(self.__prediction.sum(axis=1) - self.__dataset.getXTest().sum(axis=1)).sum() / len(self.__dataset.getXTest())


cours = CoursBuilder.fromCsv(pathlib.Path('total_d.txt'), Frequency.CALENDAR_DAY, separator='\t', column=2,
                                 timeFormat='%d/%m/%Y %H:%M').toVariation()
dataset: IDataset = DatasetWeekVectorDays(cours)
#
results = []

for k in range(1, 36):
    model = ModelKMeans(dataset, k)
    model.train()
    results.append(model.test())

sns.lineplot(data=results)
plt.xlabel('k')
plt.ylabel('Erreur moyenne')
plt.title('Resultats')


model = ModelKMeans(dataset, 13)
model.train().test()


dfTrue = pd.melt(dataset.getXTest())
dfPredict = pd.melt(model.getPrediction())
df_combined = pd.concat([dfTrue, dfPredict])
sns.lineplot(data=df_combined, markers=True, dashes=False)

plt.show()