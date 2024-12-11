from src.ETF.modelPrediction.Model.ElbowMethod import ElbowMethod


class TestElbowMethod:

    def test_bySecondDerivative(self):
        k = [1,2,3,4,5,6,7,8,9,10]
        inertia = [1000, 600, 350, 200, 150, 120, 100, 90, 85, 80]
        assert ElbowMethod.byDerivativeMethod(k_values=k, inertias=inertia) == 6

        inertia = [1000, 600, 350, 200, 150, 120, 85, 90, 80, 90]
        assert ElbowMethod.byDerivativeMethod(k_values=k, inertias=inertia) == 6

        #
        inertia = [700, 400, 220, 200, 150, 120, 85, 90, 80, 90]
        assert ElbowMethod.byDerivativeMethod(k_values=k, inertias=inertia) == 5

        inertia = [700, 300, 310, 150, 200, 120, 85, 90, 80, 90]
        assert ElbowMethod.byDerivativeMethod(k_values=k, inertias=inertia) == 5

        inertia = [700, 300, 310, 150, 200, 120, 85, 90, 80, 200]
        assert ElbowMethod.byDerivativeMethod(k_values=k, inertias=inertia) == 5

        k = [1, 2, 4, 5, 6, 7, 10]
        inertia = [700, 300, 150, 200, 120, 85, 200]
        assert ElbowMethod.byDerivativeMethod(k_values=k, inertias=inertia) == 6