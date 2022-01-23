"""Test suite for the `indcomp._maic` module.
"""

import indcomp.exceptions as e
import numpy as np
import pytest
from indcomp import MAIC
from indcomp.datasets import load_NICE_DSU18
from matplotlib.pyplot import Figure
from pytest_steps import optional_step, test_steps


@pytest.fixture
def data_NICE_DSU18():
    """Retrieve simulated NICE DSU18 data"""
    df_ind, df_tar = load_NICE_DSU18()
    return (df_ind, df_tar)


@pytest.fixture(
    params=[
        {"age.mean": ("mean", "age")},
        {"age.mean": ("mean", "age"), "age.sd": ("std", "age", "age.mean")},
    ]
)
def correct_config_maic(request, data_NICE_DSU18):
    """Return a correctly configued MAIC instance"""
    df_ind, df_tar = data_NICE_DSU18
    return MAIC(
        df_ind,
        df_tar,
        request.param,
    )


def test_maic_checks_one_string(data_NICE_DSU18):
    """Only supply one string in `match` dictionary values"""
    df_ind, df_tar = data_NICE_DSU18
    match = {"age.mean": ("age")}
    with pytest.raises(e.ConfigException):
        MAIC(df_ind, df_tar, match)


def test_maic_checks_invalid_statistic(data_NICE_DSU18):
    """Use unsupported statistic"""
    df_ind, df_tar = data_NICE_DSU18
    match = {"age.mean": ("sqrt", "age")}
    with pytest.raises(e.StatisticException):
        MAIC(df_ind, df_tar, match)


@pytest.mark.parametrize(
    "values", [("mean", "age", "second"), ("mean", "age", "second", "third")]
)
def test_maic_checks_wrong_mean(data_NICE_DSU18, values):
    """Supply incorrect number of value strings for mean statistic"""
    df_ind, df_tar = data_NICE_DSU18
    match = {"age.mean": values}
    with pytest.raises(e.MeanConfigException):
        MAIC(df_ind, df_tar, match)


@pytest.mark.parametrize("values", [("std", "age"), ("std", "age", "second", "third")])
def test_maic_checks_wrong_std(data_NICE_DSU18, values):
    """Supply incorrect number of value strings for std statistic"""
    df_ind, df_tar = data_NICE_DSU18
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
def test_maic_checks_invalid_columns(data_NICE_DSU18, key, values):
    """Supply incorrect column names that aren't in the input dataframes"""
    df_ind, df_tar = data_NICE_DSU18
    match = {}
    match[key] = values
    with pytest.raises(e.ColumnNotFoundException):
        MAIC(df_ind, df_tar, match)


def test_maic_checks_pass(data_NICE_DSU18):
    """Correcly configured `match` dictionary for matching age on mean and std"""
    df_ind, df_tar = data_NICE_DSU18
    match = {"age.mean": ("mean", "age"), "age.sd": ("std", "age", "age.mean")}
    maic = MAIC(df_ind, df_tar, match)
    assert isinstance(maic, MAIC)


@test_steps(
    "compare_unweighted",
    "weights_exception1",
    "weights_exception2",
    "calculate_weights",
    "plot_weights",
    "compare_weighted",
)
def test_maic_methods(correct_config_maic):
    """Test methods of a correctly configured MAIC instance"""
    # compare_unweighted
    maic = correct_config_maic
    fig = maic.compare_populations()
    assert isinstance(fig, Figure)
    yield

    # weights_exception1
    with optional_step("weights_exception1") as weights_exception1:
        with pytest.raises(e.NoWeightsException):
            maic.plot_weights()
    yield weights_exception1

    # weights_exception2
    with optional_step("weights_exception2") as weights_exception2:
        with pytest.raises(e.NoWeightsException):
            maic.compare_populations(weighted=True)
    yield weights_exception2

    # calculate_weights
    with optional_step("calculate_weights") as calculate_weights:
        maic.calc_weights()
        assert np.isclose(maic.ESS_, 178.56, atol=0.01) or np.isclose(
            maic.ESS_, 188.89, atol=0.01
        )
    yield calculate_weights

    # plot_weights
    with optional_step("plot_weights", depends_on=calculate_weights) as plot_weights:
        fig = maic.plot_weights()
        assert isinstance(fig, Figure)
    yield plot_weights

    # compare_weighted
    with optional_step("compare_weighted", depends_on=plot_weights) as compare_weighted:
        fig = maic.compare_populations(weighted=True)
        assert isinstance(fig, Figure)
    yield compare_weighted
