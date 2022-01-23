"""The `indcomp.datasets` module contains tools for loading example datasets.
"""

import pathlib
from typing import Tuple

import pandas as pd

ROOT_DIR = pathlib.Path(__file__).parent.parent.absolute()


def load_NICE_DSU18() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and return data as prepared in NICE DSU Technical Support Document 18.

    Two datasets are returned:
     1. Simulated Individual Patient Data (IPD) for a hypothetical trial, AB:
          n patients    : 500 (250A, 250B)
          Rows          : 500
          Columns       : 5
          Outcome       : Column 'y', binary. Value counts: {0: 238, 1: 262}
     2. Simulated Aggregated Data (AgD) or a hypothetical trial, AC:
          n patients    : 300 (150A, 150C)
          Rows          : 1
          Columns       : 10
          Outcome       : For A patients, sum(y)=125; for C patients, sum(y)=21
    """
    df_AB_IPD = pd.read_csv(f"{ROOT_DIR}/data/AB_IPD.csv")
    df_AC_AgD = pd.read_csv(f"{ROOT_DIR}/data/AC_AgD.csv")
    return (df_AB_IPD, df_AC_AgD)
