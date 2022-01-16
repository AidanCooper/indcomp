"""Test suite for indcomp
"""


import indcomp.exceptions as e
import pytest
from indcomp import MAIC
from indcomp.datasets import load_NICE_DSU18


def test_maic_checks_one_string():
    """Only supply one string in `match` dictionary values"""
    df_ind, df_tar = load_NICE_DSU18()
    match = {"age.mean": ("age")}
    with pytest.raises(e.ConfigException):
        MAIC(df_ind, df_tar, match)


def test_maic_checks_invalid_statistic():
    """Use unsupported statistic"""
    df_ind, df_tar = load_NICE_DSU18()
    match = {"age.mean": ("sqrt", "age")}
    with pytest.raises(e.StatisticException):
        MAIC(df_ind, df_tar, match)


@pytest.mark.parametrize(
    "values", [("mean", "age", "second"), ("mean", "age", "second", "third")]
)
def test_maic_checks_wrong_mean(values):
    """Supply incorrect number of value strings for mean statistic"""
    df_ind, df_tar = load_NICE_DSU18()
    match = {"age.mean": values}
    with pytest.raises(e.MeanConfigException):
        MAIC(df_ind, df_tar, match)


@pytest.mark.parametrize("values", [("std", "age"), ("std", "age", "second", "third")])
def test_maic_checks_wrong_std(values):
    """Supply incorrect number of value strings for std statistic"""
    df_ind, df_tar = load_NICE_DSU18()
    match = {"age.mean": values}
    with pytest.raises(e.StdConfigException):
        MAIC(df_ind, df_tar, match)


@pytest.mark.parametrize(
    "key, values",
    [
        ("age.sd", ("std", "age", "invalid")),
        ("age.mean", ("mean", "invalid")),
        ("age.sd", ("std", "age_", "age.mean")),
        ("age.wrong", ("std", "age", "age.mean")),
    ],
)
def test_maic_checks_invalid_columns(key, values):
    """Supply incorrect column names that aren't in the input dataframes"""
    df_ind, df_tar = load_NICE_DSU18()
    match = {}
    match[key] = values
    with pytest.raises(e.ColumnNotFoundException):
        MAIC(df_ind, df_tar, match)


def test_maic_checks_pass():
    """Correcly configured `match` dictionary for matching age on mean and std"""
    df_ind, df_tar = load_NICE_DSU18()
    match = {"age.mean": ("mean", "age"), "age.sd": ("std", "age", "age.mean")}
    maic = MAIC(df_ind, df_tar, match)
    assert isinstance(maic, MAIC)
