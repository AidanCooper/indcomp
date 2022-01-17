"""Utility functions
"""

from typing import List


def get_colour_palette() -> List[str]:
    """Function for retrieving indcomp colour palette as a list of hexcodes

    For comparison of 'target' (aggregate patient data) and 'index' (individual patient
    data) trials, list index 0 should be used for the target trial and list index 1
    should be used for the index trial
    """
    return ["#458CFF", "#63A7FF"]
