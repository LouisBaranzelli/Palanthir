from typing import List, Dict

from scipy.interpolate import UnivariateSpline, PPoly, splrep, splder

from src.service.LogService import LogService


class ElbowMethod:

    @staticmethod
    def byDerivativeMethod(k_values: List[int], inertias: List [float]) -> int:

        '''
        Je cherche la valeur pour laquelle la dérivée seconde est proche de 0. Une dérivée seconde proche de 0 indique
         que la courbure de la fonction se stabilise, c'est-à-dire que la pente de la courbe change moins rapidement.
        Cela suggère que la courbe initiale commence à s'aplatir.
        '''

        tck = splrep(k_values, inertias, k=3)
        secondDerivative = splder(tck, n=2)
        ppoly = PPoly.from_spline(secondDerivative)

        k: List[float] = ppoly.roots()

        if len(k) == 0:
            raise Exception("Failing to find elbow.")
        LogService.info(f"[ElbowMethod] Found the best number of cluster: {int(sum(k)/len(k))}")
        return int(sum(k)/len(k))







