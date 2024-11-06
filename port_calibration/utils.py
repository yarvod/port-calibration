import json
import numpy as np
from typing import Tuple

from .two_port import TwoPortCalibration


def load_json_data(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)
    

def load_two_port_cals(
    open_dir: str,
    short_dir: str,
    load_dir: str,
    through_dir: str,
    s11_load=0.01,
    s11_open=0.99,
    s11_short=-0.99
) -> Tuple[TwoPortCalibration, dict]:
    # open
    open_raw_sm11 = load_json_data(f"{open_dir}/s11.json")['data']
    open_sm11 = np.array(open_raw_sm11['real']) + np.array(open_raw_sm11['imag']) * 1j
    open_raw_sm22 = load_json_data(f"{open_dir}/s22.json")['data']
    open_sm22 = np.array(open_raw_sm22['real']) + np.array(open_raw_sm22['imag']) * 1j

    # short
    short_raw_sm11 = load_json_data(f"{short_dir}/s11.json")['data']
    short_sm11 = np.array(short_raw_sm11['real']) + np.array(short_raw_sm11['imag']) * 1j
    short_raw_sm22 = load_json_data(f"{short_dir}/s22.json")['data']
    short_sm22 = np.array(short_raw_sm22['real']) + np.array(short_raw_sm22['imag']) * 1j

    # load
    load_raw_sm11 = load_json_data(f"{load_dir}/s11.json")['data']
    load_sm11 = np.array(load_raw_sm11['real']) + np.array(load_raw_sm11['imag']) * 1j
    load_raw_sm22 = load_json_data(f"{load_dir}/s22.json")['data']
    load_sm22 = np.array(load_raw_sm22['real']) + np.array(load_raw_sm22['imag']) * 1j
    load_raw_sm12 = load_json_data(f"{load_dir}/s12.json")['data']
    load_sm12 = np.array(load_raw_sm12['real']) + np.array(load_raw_sm12['imag']) * 1j
    load_raw_sm21 = load_json_data(f"{load_dir}/s21.json")['data']
    load_sm21 = np.array(load_raw_sm21['real']) + np.array(load_raw_sm21['imag']) * 1j

    # throw
    throw_raw_sm11 = load_json_data(f"{through_dir}/s11.json")['data']
    throw_sm11 = np.array(throw_raw_sm11['real']) + np.array(throw_raw_sm11['imag']) * 1j
    throw_raw_sm22 = load_json_data(f"{through_dir}/s22.json")['data']
    throw_sm22 = np.array(throw_raw_sm22['real']) + np.array(throw_raw_sm22['imag']) * 1j
    throw_raw_sm12 = load_json_data(f"{through_dir}/s12.json")['data']
    throw_sm12 = np.array(throw_raw_sm12['real']) + np.array(throw_raw_sm12['imag']) * 1j
    throw_raw_sm21 = load_json_data(f"{through_dir}/s21.json")['data']
    throw_sm21 = np.array(throw_raw_sm21['real']) + np.array(throw_raw_sm21['imag']) * 1j

    two_cal = TwoPortCalibration(
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
        s11_load=s11_load,
        s11_open=s11_open,
        s11_short=s11_short
    )
    two_cal.calibrate()

    return two_cal, {
        "open_sm11": open_sm11,
        "open_sm22": open_sm22,
        "short_sm11": short_sm11,
        "short_sm22": short_sm22,
        "load_sm11": load_sm11,
        "load_sm22": load_sm22,
        "load_sm12": load_sm12,
        "load_sm21": load_sm21,
        "throw_sm11": throw_sm11,
        "throw_sm22": throw_sm22,
        "throw_sm12": throw_sm12,
        "throw_sm21": throw_sm21,
    }
