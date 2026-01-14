import numpy as np

from port_calibration import OnePortCalibration


def _measured_one_port(D, S, R, gamma):
    return D + (R * gamma) / (1 - S * gamma)


def test_one_port_calibration_recovers_error_terms():
    D = np.array([0.02 + 0.01j, -0.03 + 0.005j, 0.01 - 0.02j])
    S = np.array([0.1 + 0.02j, -0.05 + 0.03j, 0.02 - 0.04j])
    R = np.array([0.9 - 0.1j, 1.05 + 0.05j, 0.8 + 0.2j])

    sm11_open = _measured_one_port(D, S, R, 1)
    sm11_short = _measured_one_port(D, S, R, -1)
    sm11_load = _measured_one_port(D, S, R, 0)

    cal = OnePortCalibration(
        sm11_open=sm11_open,
        sm11_short=sm11_short,
        sm11_load=sm11_load,
        s11_open=1,
        s11_short=-1,
        s11_load=0,
    )
    cal.calculate_calibration()

    np.testing.assert_allclose(cal.cals["D"], D, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.cals["S"], S, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(cal.cals["R"], R, rtol=1e-9, atol=1e-12)


def test_one_port_calibrate_measure_returns_true_gamma():
    D = np.array([0.01 + 0.02j, -0.015 + 0.01j, 0.02 - 0.005j])
    S = np.array([0.08 - 0.01j, 0.05 + 0.015j, -0.03 + 0.02j])
    R = np.array([0.95 + 0.03j, 1.02 - 0.02j, 0.85 + 0.08j])

    sm11_open = _measured_one_port(D, S, R, 1)
    sm11_short = _measured_one_port(D, S, R, -1)
    sm11_load = _measured_one_port(D, S, R, 0)

    cal = OnePortCalibration(
        sm11_open=sm11_open,
        sm11_short=sm11_short,
        sm11_load=sm11_load,
    )
    cal.calculate_calibration()

    gamma_true = np.array([0.2 + 0.1j, -0.3 + 0.05j, 0.1 - 0.2j])
    sm11_measured = _measured_one_port(D, S, R, gamma_true)
    gamma_cal = cal.calibrate_measure(sm11_measured)

    np.testing.assert_allclose(gamma_cal, gamma_true, rtol=1e-9, atol=1e-12)


def test_one_port_with_noisy_standards_recovers_reasonable_gamma():
    rng = np.random.default_rng(0)
    points = 8
    D = 0.02 + 0.01j + rng.normal(scale=0.002, size=points)
    S = 0.06 - 0.02j + rng.normal(scale=0.002, size=points)
    R = 0.95 + 0.03j + rng.normal(scale=0.002, size=points)

    sm11_open = _measured_one_port(D, S, R, 1)
    sm11_short = _measured_one_port(D, S, R, -1)
    sm11_load = _measured_one_port(D, S, R, 0)

    noise = lambda: rng.normal(scale=0.003, size=points) + 1j * rng.normal(
        scale=0.003, size=points
    )
    sm11_open += noise()
    sm11_short += noise()
    sm11_load += noise()

    cal = OnePortCalibration(
        sm11_open=sm11_open,
        sm11_short=sm11_short,
        sm11_load=sm11_load,
    )
    cal.calculate_calibration()

    gamma_true = (
        0.25
        - 0.15j
        + rng.normal(scale=0.01, size=points)
        + 1j * rng.normal(scale=0.01, size=points)
    )
    sm11_measured = _measured_one_port(D, S, R, gamma_true) + noise()
    gamma_cal = cal.calibrate_measure(sm11_measured)

    np.testing.assert_allclose(gamma_cal, gamma_true, rtol=2e-2, atol=2e-2)
