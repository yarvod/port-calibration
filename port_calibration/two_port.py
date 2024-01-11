from port_calibration import OnePortCalibration


class TwoPortCalibration:
    """Two port calibration based on TOSL (Through, Open, Short, Load/Match) calibration"""

    def __init__(
        self,
        load_sm11,
        load_sm22,
        load_sm12,
        load_sm21,
        open_sm11,
        open_sm22,
        short_sm11,
        short_sm22,
        throw_sm11,
        throw_sm22,
        throw_sm12,
        throw_sm21,
        s11_load=0,
        s11_open=1,
        s11_short=-1,
    ):
        self.load_sm11 = load_sm11
        self.load_sm22 = load_sm22
        self.load_sm12 = load_sm12
        self.load_sm21 = load_sm21

        self.open_sm11 = open_sm11
        self.open_sm22 = open_sm22

        self.short_sm11 = short_sm11
        self.short_sm22 = short_sm22

        self.throw_sm11 = throw_sm11
        self.throw_sm22 = throw_sm22
        self.throw_sm12 = throw_sm12
        self.throw_sm21 = throw_sm21

        self.s11_load = s11_load
        self.s11_open = s11_open
        self.s11_short = s11_short

        # forward
        self.e00 = 0
        self.e11 = 0
        self.e10e01 = 0
        self.e30 = 0
        self.e22 = 0
        self.e10e32 = 0

        # reverse
        self.e33_r = 0
        self.e22_r = 0
        self.e23e32_r = 0
        self.e03_r = 0
        self.e11_r = 0
        self.e23e01_r = 0

    def cals(self):
        return {
            "E00": self.e00,  # D
            "E11": self.e11,  # S
            "E10E01": self.e10e01,  # R
            "E30": self.e30,
            "E22": self.e22,
            "E10E32": self.e10e32,
            "E33'": self.e33_r,  # Reversed D
            "E22'": self.e22_r,  # Reversed S
            "E23'E32'": self.e23e32_r,  # Reversed R
            "E03'": self.e03_r,
            "E11'": self.e11_r,
            "E23'E01'": self.e23e01_r,
        }

    def _step_1(self):
        """STEP 1: One port calibration for P1 and P2 (open, short, load)"""

        # P1 forward
        p1 = OnePortCalibration(
            sm11_open=self.open_sm11,
            sm11_short=self.short_sm11,
            sm11_load=self.load_sm11,
            s11_short=self.s11_short,
            s11_open=self.s11_open,
            s11_load=self.s11_load,
        )
        p1.calculate_calibration()
        self.e00 = p1.cals["D"]
        self.e11 = p1.cals["S"]
        self.e10e01 = p1.cals["R"]

        p2 = OnePortCalibration(
            sm11_open=self.open_sm22,
            sm11_short=self.short_sm22,
            sm11_load=self.load_sm22,
            s11_short=self.s11_short,
            s11_open=self.s11_open,
            s11_load=self.s11_load,
        )
        p2.calculate_calibration()
        self.e33_r = p2.cals["D"]
        self.e22_r = p2.cals["S"]
        self.e23e32_r = p2.cals["R"]

    def _step_2(self):
        """STEP 2: Connect 50 Ohm to P1 and P2"""

        # P1: sm21 = e30
        self.e30 = self.load_sm21

        # P2: sm12 = e03_r
        self.e03_r = self.load_sm12

    def _step_3(self):
        """STEP 3: Throw calibration"""

        # P1
        delta_e = self.e00 * self.e11 - self.e10e01
        self.e22 = (self.throw_sm11 - self.e00) / (self.throw_sm11 * self.e11 - delta_e)
        self.e10e32 = (self.throw_sm21 - self.e30) * (1 - self.e11 * self.e22)

        # P2
        delta_e_r = self.e33_r * self.e22_r - self.e23e32_r
        e11_r = (self.throw_sm22 - self.e33_r) / (
            self.throw_sm22 * self.e22_r - delta_e_r
        )
        self.e23e01_r = (self.throw_sm12 - self.e03_r) * (1 - self.e22_r * e11_r)

    def calibrate(self):
        self._step_1()
        self._step_2()
        self._step_3()

    def calc_D(self, sm11, sm22, sm12, sm21):
        a = 1 + self.e11 * (sm11 - self.e00) / self.e10e01
        b = 1 + self.e22_r * (sm22 - self.e33_r) / self.e23e32_r
        c = (
            self.e22
            * self.e11_r
            * ((sm21 - self.e30) / self.e10e32)
            * ((sm12 - self.e03_r) / self.e23e01_r)
        )
        return a * b - c

    def calc_S11(self, sm11, sm22, sm12, sm21):
        D = self.calc_D(sm11, sm22, sm12, sm21)
        a = (sm11 - self.e00) / self.e10e01
        b = 1 + self.e22_r * (sm22 - self.e33_r) / self.e23e32_r
        c = (
            self.e22
            * ((sm21 - self.e30) / self.e10e32)
            * ((sm12 - self.e03_r) / self.e23e01_r)
        )
        return (a * b - c) / D

    def calc_S21(self, sm11, sm22, sm12, sm21):
        D = self.calc_D(sm11, sm22, sm12, sm21)
        a = (sm21 - self.e30) / self.e10e32
        b = 1 + (self.e22_r - self.e22) * (sm22 - self.e33_r) / self.e23e32_r
        return a * b / D

    def calc_S22(self, sm11, sm22, sm12, sm21):
        D = self.calc_D(sm11, sm22, sm12, sm21)
        a = (sm22 - self.e33_r) / self.e23e32_r
        b = 1 + self.e22 * (sm22 - self.e00) / self.e10e01
        c = (
            self.e11_r
            * ((sm21 - self.e30) / self.e10e32)
            * ((sm12 - self.e03_r) / self.e23e01_r)
        )
        return (a * b - c) / D

    def calc_S12(self, sm11, sm22, sm12, sm21):
        D = self.calc_D(sm11, sm22, sm12, sm21)
        a = (sm12 - self.e03_r) / self.e23e01_r
        b = 1 + (self.e11 - self.e11_r) * (sm11 - self.e00) / self.e10e01
        return a * b / D
