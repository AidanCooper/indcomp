"""Matching-Adjusted Indirect Comparison (MAIC)

This module enables MAIC analyses to be performed. For theoretical background of MAIC,
see Signorovich et al (2012) (https://doi.org/10.1016/j.jval.2012.05.004).

This implementation mirrors NICE's guidance in DSU Technical Support Document 18.
"""

from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize


class MAIC:
    """A class for conducting MAIC analyses.

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
         - The first string is the statistic to use (options: {'mean', 'std')
         - The second string is the corresponding column name from `df_index`
         - A third string is only required for the 'std' statistic. This should be
         the `df_target` column name that corresponds to the 'mean' of the EM.

    Methods
    -------
    calc_weights()
        Calculate weights using the method of moments approach
    """

    def __init__(
        self,
        df_index: pd.DataFrame,
        df_target: pd.DataFrame,
        match: Dict[str, Tuple[str, str]],
    ):
        """Initialises an instance of `MAIC`"""
        self.df_index = df_index
        self.df_target = df_target
        self.match = match

    def _objfn(self, params: Tuple[float], X: pd.DataFrame) -> float:
        """Function to be optimised during calculation of weights"""
        return np.sum(np.exp(np.matmul(X, params)))

    def _gradfn(self, params: Tuple[float], X: pd.DataFrame) -> np.array:
        """Gradient function to assist with optimisation"""
        return np.dot(np.exp(np.matmul(X, params)), X)

    def calc_weights(self):
        """Calculate weights for each patient in `df_index`"""
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

        # initialise the parameters for optimisation
        x0 = tuple([0.0 for _ in self.X_EM_0.columns])
        self.result_ = minimize(
            self._objfn, x0, args=(self.X_EM_0), method="BFGS", jac=self._gradfn
        )
        self.a1_ = self.result_.x

        # calculate (scaled weights)
        self.weights_ = np.exp(np.matmul(self.X_EM_0, self.a1_))
        self.scaled_weights_ = (
            self.weights_ / np.sum(self.weights_) * len(self.df_index)
        )

        # calculate Effective Sample Size (ESS)
        self.ESS_ = np.sum(self.weights_) ** 2 / np.sum(self.weights_ ** 2)
