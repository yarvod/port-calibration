import numpy as np


class OnePortCalibration:
    """One port S11 calibration based on OSL (Open, Short, Load/Match) calibration"""

    def __init__(
        self,
        sm11_open,
        sm11_short,
        sm11_load,
        s11_open: float = 1,
        s11_short: float = -1,
        s11_load: float = 0,
    ):
        """
        :param sm11_open - Calibration data for Open
        :param sm11_short - Calibration data for Short
        :param sm11_load - Calibration data for Load
        :param s11_open - Ideal open reflection coeff
        :param s11_short - Ideal short reflection coeff
        :param s11_load - Ideal load reflection coeff
        """
        self.sm11_open = sm11_open
        self.sm11_short = sm11_short
        self.sm11_load = sm11_load
        self.s11_open = s11_open
        self.s11_short = s11_short
        self.s11_load = s11_load
        self.calibrated_measure = []
        self.cals = {"D": [], "S": [], "R": []}

    @staticmethod
    def calculate_error_matrix(C, V):
        C_H = np.matrix.getH(C)
        inv_CC_H = np.linalg.inv(np.dot(C_H, C))
        result = np.dot(np.dot(inv_CC_H, C_H), V.T)
        return result

    def append_error_coeffs(self, vector):
        self.cals["D"].append(vector[1])
        self.cals["S"].append(vector[2])
        self.cals["R"].append(vector[0] + vector[1] * vector[2])

    def calibrate_measure(self, sm11):
        assert sm11 is not None, "Measure data should not be None!"
        gamma = (sm11 - self.cals["D"]) / (
            self.cals["R"] + self.cals["S"] * (sm11 - self.cals["D"])
        )
        self.calibrated_measure = gamma
        return gamma

    def calculate_calibration(self):
        self.cals = {"D": [], "S": [], "R": []}
        for i in range(len(self.sm11_load)):
            C = np.array(
                [
                    [self.s11_load, 1, self.s11_load * self.sm11_load[i]],
                    [self.s11_open, 1, self.s11_open * self.sm11_open[i]],
                    [self.s11_short, 1, self.s11_short * self.sm11_short[i]],
                ]
            )
            V = np.array([self.sm11_load[i], self.sm11_open[i], self.sm11_short[i]])
            self.append_error_coeffs(self.calculate_error_matrix(C, V))

        for k in self.cals.keys():
            self.cals[k] = np.array(self.cals[k])
