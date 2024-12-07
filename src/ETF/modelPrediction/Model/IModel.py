import pandas as pd


class IModel:

    def __init__(self):
        self.__prediction: pd.DataFrame = pd.DataFrame()

    def getPrediction(self) -> pd.DataFrame:
        return self.__prediction

    def train(self) -> 'IModel':
        pass