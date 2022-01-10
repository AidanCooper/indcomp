"""
indcomp is a package for conducting indirect treatment comparison (ITC) analyses.

Currently supported methods:
 - Matching-Adjusted Indirect Comparison (MAIC)

Coming soon:
 - Simulated Treatment Comparison (STC)
"""

__version__ = "0.1.0"

from ._maic import MAIC
