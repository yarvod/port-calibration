import numpy as np

from port_calibration import TwoPortCalibration


def _measured_one_port(D, S, R, gamma):
    return D + (R * gamma) / (1 - S * gamma)


def _thru_measurements(
    e00,
    e11,
    e10e01,
    e30,
    e22,
    e10e32,
    e33_r,
    e22_r,
    e23e32_r,
    e03_r,
    e11_r,
    e23e01_r,
):
    delta_e = e00 * e11 - e10e01
    throw_sm11 = (e22 * delta_e - e00) / (e22 * e11 - 1)
    throw_sm21 = e30 + e10e32 / (1 - e11 * e22)

    delta_e_r = e33_r * e22_r - e23e32_r
    throw_sm22 = (e11_r * delta_e_r - e33_r) / (e11_r * e22_r - 1)
    throw_sm12 = e03_r + e23e01_r / (1 - e22_r * e11_r)

    return throw_sm11, throw_sm22, throw_sm12, throw_sm21


def test_two_port_calibration_recovers_error_terms_and_thru():
    e00 = np.array([0.02 + 0.01j, -0.015 + 0.005j, 0.01 - 0.02j])
    e11 = np.array([0.05 - 0.01j, -0.03 + 0.02j, 0.02 + 0.03j])
    e10e01 = np.array([0.9 + 0.02j, 1.05 - 0.03j, 0.8 + 0.1j])

    e33_r = np.array([-0.01 + 0.015j, 0.02 - 0.01j, -0.005 + 0.005j])
    e22_r = np.array([0.04 + 0.01j, -0.02 + 0.015j, 0.03 - 0.02j])
    e23e32_r = np.array([1.1 - 0.05j, 0.95 + 0.04j, 1.02 - 0.02j])

    e22 = np.array([0.02 - 0.01j, -0.015 + 0.02j, 0.01 + 0.005j])
    e10e32 = np.array([0.98 + 0.01j, 1.02 - 0.02j, 0.95 + 0.05j])
    e11_r = np.array([0.03 + 0.02j, -0.025 + 0.01j, 0.015 - 0.02j])
    e23e01_r = np.array([1.03 - 0.02j, 0.97 + 0.03j, 1.01 + 0.01j])

    open_sm11 = _measured_one_port(e00, e11, e10e01, 1)
    short_sm11 = _measured_one_port(e00, e11, e10e01, -1)
    load_sm11 = _measured_one_port(e00, e11, e10e01, 0)

    open_sm22 = _measured_one_port(e33_r, e22_r, e23e32_r, 1)
    short_sm22 = _measured_one_port(e33_r, e22_r, e23e32_r, -1)
    load_sm22 = _measured_one_port(e33_r, e22_r, e23e32_r, 0)

    load_sm12 = np.zeros_like(e00, dtype=complex)
    load_sm21 = np.zeros_like(e00, dtype=complex)

    e30 = np.zeros_like(e00, dtype=complex)
    e03_r = np.zeros_like(e00, dtype=complex)
    throw_sm11, throw_sm22, throw_sm12, throw_sm21 = _thru_measurements(
        e00,
        e11,
        e10e01,
        e30,
        e22,
        e10e32,
        e33_r,
        e22_r,
        e23e32_r,
        e03_r,
        e11_r,
        e23e01_r,
    )

    cal = TwoPortCalibration(
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
    )
    cal.calibrate()

    np.testing.assert_allclose(cal.e00, e00, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.e11, e11, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.e10e01, e10e01, rtol=1e-9, atol=1e-12)

    np.testing.assert_allclose(cal.e33_r, e33_r, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.e22_r, e22_r, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.e23e32_r, e23e32_r, rtol=1e-9, atol=1e-12)

    np.testing.assert_allclose(cal.e22, e22, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.e10e32, e10e32, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.e11_r, e11_r, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.e23e01_r, e23e01_r, rtol=1e-9, atol=1e-12)

    s11 = cal.calc_S11(throw_sm11, throw_sm22, throw_sm12, throw_sm21)
    s22 = cal.calc_S22(throw_sm11, throw_sm22, throw_sm12, throw_sm21)
    s21 = cal.calc_S21(throw_sm11, throw_sm22, throw_sm12, throw_sm21)
    s12 = cal.calc_S12(throw_sm11, throw_sm22, throw_sm12, throw_sm21)

    np.testing.assert_allclose(s11, np.zeros_like(s11), rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(s22, np.zeros_like(s22), rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(s21, np.ones_like(s21), rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(s12, np.ones_like(s12), rtol=1e-9, atol=1e-12)


def test_two_port_with_noisy_standards_produces_reasonable_thru():
    rng = np.random.default_rng(1)
    points = 6

    def cnoise(scale):
        return rng.normal(scale=scale, size=points) + 1j * rng.normal(
            scale=scale, size=points
        )

    e00 = 0.02 + 0.01j + cnoise(0.002)
    e11 = 0.05 - 0.01j + cnoise(0.002)
    e10e01 = 0.95 + 0.02j + cnoise(0.002)

    e33_r = -0.01 + 0.015j + cnoise(0.002)
    e22_r = 0.04 + 0.01j + cnoise(0.002)
    e23e32_r = 1.05 - 0.03j + cnoise(0.002)

    e22 = 0.02 - 0.01j + cnoise(0.002)
    e10e32 = 0.98 + 0.02j + cnoise(0.002)
    e11_r = 0.03 + 0.02j + cnoise(0.002)
    e23e01_r = 1.02 - 0.02j + cnoise(0.002)

    open_sm11 = _measured_one_port(e00, e11, e10e01, 1) + cnoise(0.003)
    short_sm11 = _measured_one_port(e00, e11, e10e01, -1) + cnoise(0.003)
    load_sm11 = _measured_one_port(e00, e11, e10e01, 0) + cnoise(0.003)

    open_sm22 = _measured_one_port(e33_r, e22_r, e23e32_r, 1) + cnoise(0.003)
    short_sm22 = _measured_one_port(e33_r, e22_r, e23e32_r, -1) + cnoise(0.003)
    load_sm22 = _measured_one_port(e33_r, e22_r, e23e32_r, 0) + cnoise(0.003)

    load_sm12 = cnoise(0.001)
    load_sm21 = cnoise(0.001)

    e30 = np.zeros_like(e00, dtype=complex)
    e03_r = np.zeros_like(e00, dtype=complex)
    throw_sm11, throw_sm22, throw_sm12, throw_sm21 = _thru_measurements(
        e00,
        e11,
        e10e01,
        e30,
        e22,
        e10e32,
        e33_r,
        e22_r,
        e23e32_r,
        e03_r,
        e11_r,
        e23e01_r,
    )
    throw_sm11 += cnoise(0.003)
    throw_sm22 += cnoise(0.003)
    throw_sm12 += cnoise(0.003)
    throw_sm21 += cnoise(0.003)

    cal = TwoPortCalibration(
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
    )
    cal.calibrate()

    s11 = cal.calc_S11(throw_sm11, throw_sm22, throw_sm12, throw_sm21)
    s22 = cal.calc_S22(throw_sm11, throw_sm22, throw_sm12, throw_sm21)
    s21 = cal.calc_S21(throw_sm11, throw_sm22, throw_sm12, throw_sm21)
    s12 = cal.calc_S12(throw_sm11, throw_sm22, throw_sm12, throw_sm21)

    np.testing.assert_allclose(s11, np.zeros_like(s11), rtol=5e-2, atol=5e-2)
    np.testing.assert_allclose(s22, np.zeros_like(s22), rtol=5e-2, atol=5e-2)
    np.testing.assert_allclose(s21, np.ones_like(s21), rtol=5e-2, atol=5e-2)
    np.testing.assert_allclose(s12, np.ones_like(s12), rtol=5e-2, atol=5e-2)
