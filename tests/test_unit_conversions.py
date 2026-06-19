import pytest

from unit_conversions import (
    btu_per_hr_to_watts_input,
    kw_cooling_to_kw_input,
    tons_to_btu_per_hr,
    tons_to_kw_cooling,
)


def test_one_ton_is_12000_btu_per_hr():
    assert tons_to_btu_per_hr(1) == 12000


def test_one_ton_is_3517_kw_cooling():
    assert tons_to_kw_cooling(1) == pytest.approx(3.517)


def test_btu_per_hr_to_watts_input_uses_eer():
    assert btu_per_hr_to_watts_input(12000, 12) == pytest.approx(1000)


def test_kw_cooling_to_kw_input_uses_cop():
    assert kw_cooling_to_kw_input(3.6, 3) == pytest.approx(1.2)
