import pandas as pd

from src.ETF.cours.Cours import Cours
from src.ETF.modelPrediction.Dataset.IDataset import IDataset


class DatasetShift(IDataset):
    def __init__(self, cours: Cours, vectorSize: int, ratioSplitTest=0.2):

        self.__ratioSplitTest = ratioSplitTest
        self.__cours = cours
        __dataset: pd.DataFrame = pd.DataFrame()
        if vectorSize > self.__cours.getValues().size:
            raise (Exception(f"Can not create shift dataset, size: {vectorSize} > vector X size values.getValues().size"))
        for i in range(vectorSize, 0, -1):
            __dataset[f'lag_{i}'] = self.__cours.getValues().shift(i - 1)

        super().__init__(__dataset.dropna())

