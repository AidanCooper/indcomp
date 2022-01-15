"""Matching-Adjusted Indirect Comparison (MAIC)

This module enables MAIC analyses to be performed. For theoretical background of MAIC,
see Signorovich et al (2012) (https://doi.org/10.1016/j.jval.2012.05.004).

This implementation mirrors NICE's guidance in DSU Technical Support Document 18.
"""

from typing import Dict, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

import indcomp.exceptions as e


class MAIC:
    """A class for conducting Matching-Adjusted Indirect Comparison (MAIC) analyses.

    Attributes
    ----------
    df_index : pd.DataFrame
        Dataframe of Individual Patient Data (IPD). Weights are calculated for each
        patient to yield aggregate statistics that match `df_target`.
    df_target : pd.DataFrame
        Dataframe of aggregate data (i.e. it should be a single row). Data in
        `df_index` is weighted to match the corresonding columns in `df_target` as
        closely as possible, as specified in `match` dictionary.
    match : Dict
        Dictionary that specifies the Effect Modifiers (EMs) that are to be matched.
        Keys correspond to column names in 'df_target'. Values are tuples containing
        two or three strings:
         - The first string is the statistic to use (options: {'mean', 'std'})
         - The second string is the corresponding column name from `df_index`
         - A third string is only required for the 'std' statistic. This should be
         the `df_target` column name that corresponds to the 'mean' of the EM.
    weights_calculated : bool
        Boolean that tracks if weights have been successfully calculated

    Methods
    -------
    calc_weights()
        Calculate weights using the method of moments approach
    """

    def __init__(
        self,
        df_index: pd.DataFrame,
        df_target: pd.DataFrame,
        match: Dict[str, Tuple[str]],
    ):
        self._check_match(match, df_index.columns, df_target.columns)
        self.df_index = df_index
        self.df_target = df_target
        self.match = match
        self.weights_calculated = False

    def _check_match(
        self,
        match_dict: Dict[str, Tuple[str]],
        ind_cols: list[str],
        tar_cols: list[str],
    ):
        """Checks that `match_dict` is correctly configured"""
        for k, v in match_dict.items():
            if type(v) == str:  # only one string provided in dictionary values
                raise e.ConfigException(v)
            if v[0] not in ["mean", "std"]:
                raise e.StatisticException(v[0])
            if v[0] == "mean":
                if len(v) != 2:
                    raise e.MeanConfigException(v)
            if v[0] == "std":
                if len(v) != 3:
                    raise e.StdConfigException(v)
                if v[2] not in tar_cols:
                    raise e.ColumnNotFoundException(v[2], "target")
            if k not in tar_cols:
                raise e.ColumnNotFoundException(k, "target")
            if v[1] not in ind_cols:
                raise e.ColumnNotFoundException(v[1], "index")

    def _objfn(self, params: Tuple[float], X: pd.DataFrame) -> float:
        """Function to be optimised during calculation of weights"""
        return np.sum(np.exp(np.matmul(X, params)))

    def _gradfn(self, params: Tuple[float], X: pd.DataFrame) -> np.array:
        """Gradient function to assist with optimisation"""
        return np.dot(np.exp(np.matmul(X, params)), X)

    def calc_weights(self):
        """Calculate weights for each patient in `df_index`

        Attributes
        ----------
        a1_ : np.array(float)
            The optimised values for alpha1
        weights_ : np.array(float)
            The calculated weights
        weights_scaled_ : np.array(float)
            The calculated weights, rescaled such that they sum to the size of the
            population
        ESS_ : float
            The Effective Sample Size (ESS) of the weighted population
        """
        # compute centred versions of the Effect Modifiers
        self.X_EM_0 = pd.DataFrame()
        for k, v in self.match.items():
            if v[0] == "mean":
                self.X_EM_0[v[1] + "_mean"] = (
                    self.df_index[v[1]] - self.df_target[k].values[0]
                )
            elif v[0] == "std":
                self.X_EM_0[v[1] + "_std"] = (
                    self.df_index[v[1]] ** 2
                    - self.df_target[k].values[0] ** 2
                    - self.df_target[v[2]].values[0] ** 2
                )

        # find optimal alpha1 parameters
        x0 = tuple([0.0 for _ in self.X_EM_0.columns])  # initialise the parameters as 0
        self.alpha1_result_ = minimize(
            self._objfn, x0, args=(self.X_EM_0), method="BFGS", jac=self._gradfn
        )
        self.a1_ = self.alpha1_result_.x

        # calculate (scaled) weights
        self.weights_ = np.exp(np.matmul(self.X_EM_0, self.a1_))
        self.weights_scaled_ = (
            self.weights_ / np.sum(self.weights_) * len(self.df_index)
        )

        # calculate Effective Sample Size (ESS)
        self.ESS_ = np.sum(self.weights_) ** 2 / np.sum(self.weights_ ** 2)

        self.weights_calculated = True

    def compare_populations(
        self, weighted: bool = False, vars: Optional[list[str]] = None, ncols: int = 3
    ) -> plt.Figure:
        """
        Plot the unweighted populations for the variables in `vars`.

        Parameters
        ----------
        weighted : bool
            Whether to compare the weighted or unweighted populations. Defaults to
            False. To compare weighted, `calc_weights()` must be successfully run first.
        vars : Optional[list[str]]
            The names of the variables to compare. These should be specified for the
            target dataset (i.e. they should be they keys in the `match` dictionary).
            Defaults to None, which means the keys in `match` will be used.
        ncols : int
            The number of columns to use in the grid of plots. If `len(vars)` is less
            than `ncols`, this will be used instead. Otherwise, defaults to 3.
        Returns
        -------
        plt.Figure
            A grid of plots for each variable in `vars`, comparing the unweighted index
            and target datasets.
        """

        if not vars:
            vars = list(self.match.keys())

        if weighted and not self.weights_calculated:
            raise e.NoWeightsException()

        # create grid
        ncols = min(ncols, len(vars))
        nrows = len(vars) // ncols
        remainder = len(vars) % ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4, nrows * 4))
        fig.patch.set_facecolor("white")
        axes = axes.flatten()
        for r in range(1, remainder + 1):
            axes[-r].axis("off")

        # plot vars
        for var, ax in zip(vars, axes):
            if self.match[var][0] == "mean":
                if weighted:
                    val_ind = (
                        self.df_index[self.match[var][1]] * self.weights_scaled_
                    ).mean()
                else:
                    val_ind = self.df_index[self.match[var][1]].mean()
            elif self.match[var][0] == "std":
                if weighted:
                    ind_mean = (
                        self.df_index[self.match[var][1]] * self.weights_scaled_
                    ).mean()
                    val_ind = np.sqrt(
                        np.sum(
                            self.weights_
                            / np.sum(self.weights_)
                            * (self.df_index[self.match[var][1]] - ind_mean) ** 2
                        )
                    )
                else:
                    val_ind = self.df_index[self.match[var][1]].std()
            val_tar = self.df_target[var].values[0]
            ax.bar([0, 1], [val_tar, val_ind])
            ax.grid(axis="y")
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["target", "index"])
            ax.set_title(var + " (weighted)" if weighted else var)

            # annotate bars with values
            voffset = min(val_tar, val_ind) * 0.05
            for rect, label in zip(ax.patches, [val_tar, val_ind]):
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    rect.get_height() - voffset,
                    f"{label:.1f}",
                    ha="center",
                    va="top",
                    color="white",
                    size=12,
                    weight="bold",
                )
        plt.close()

        return fig

    def plot_weights(
        self, bins: Optional[Union[int, list[float]]] = None
    ) -> plt.Figure:
        """Plot a histogram of the scaled calculated weights.

        Parameters
        ----------
        bins : Optional[Union[int, list[float]]]
            If `bins` is an integer, it defines the number of equal-width bins to use.
            If `bins` is a list of values, these define the bin edges. Defaults to None,
            which uses matplotlib's default settings.

        Returns
        -------
        plt.Figure
            A histogram of the scaled calculated weights
        """
        if not self.weights_calculated:
            raise e.NoWeightsException()

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("white")
        ax.hist(self.weights_scaled_, bins=bins)
        ax.set_ylabel("count")
        ax.set_xlabel("weight (scaled)")
        ax.grid(axis="y")
        plt.close()

        return fig
