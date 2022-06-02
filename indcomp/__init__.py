"""
indcomp is a package for conducting indirect treatment comparison (ITC) analyses.

Currently supported methods:
 - Matching-Adjusted Indirect Comparison (MAIC)

Coming soon:
 - Simulated Treatment Comparison (STC)
"""

from pdoc import __pdoc__

__pdoc__["_maic"] = True
__version__ = "0.2.0"

from ._maic import MAIC
