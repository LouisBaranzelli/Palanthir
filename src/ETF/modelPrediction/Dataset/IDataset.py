from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from src.ETF.cours import Cours

from abc import ABC, abstractmethod


class IDataset(ABC):
    """
    Classe abstraite représentant un dataset.
    """

    @abstractmethod
    def getDimInput(self) -> int:
        """
        Méthode abstraite pour obtenir la taille initiale du vecteur requis dans la liste chainee des datasets
        :return: Un entier représentant la dimension.
        """
        pass

    @abstractmethod
    def run(self, dataset: 'IDataset') -> 'IDataset':
        "Methode qui sera appelee lors du chainage"
        pass

    @abstractmethod
    def getData(self) -> pd.DataFrame:
        "Valeur vectorisee sans les labels"
        pass


    @abstractmethod
    def getLabel(self) -> pd.DataFrame:
        "Le Label mis a jours en fonction des transformations apportees au dataset"
        pass

