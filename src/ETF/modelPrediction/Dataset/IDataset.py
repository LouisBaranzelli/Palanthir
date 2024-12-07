from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from src.ETF.cours import Cours


class IDataset:

    def __init__(self, df: pd.DataFrame, ratioSplitTest=0.2):

        if df.isna().any().any():
            raise Exception("Le dataframe contient des NaN Value et va decaler les indexes")

        dfXTrain, dfXTest = train_test_split(df, test_size=ratioSplitTest, shuffle=False)

        self.__X_train: pd.DataFrame = dfXTrain.iloc[:, :-1]
        self.__y_train: pd.Series = dfXTrain.iloc[:, -1]
        self.__X_test: pd.DataFrame = dfXTest.iloc[:, :-1]
        self.__y_test: pd.Series = dfXTest.iloc[:, -1]

    def getXTrain(self) -> pd.DataFrame:
        return self.__X_train

    # def getYTrain(self) -> pd.DataFrame:
    #     return self.__y_train

    def getXTest(self) -> pd.DataFrame:
        return self.__X_test

    # def getYTest(self) -> pd.DataFrame:
    #     return self.__y_test

    def getCours(self) -> Cours:
        pass

