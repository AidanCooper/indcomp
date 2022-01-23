"""The `indcomp.exceptions` module includes all custom exceptions.
"""


class NoWeightsException(Exception):
    """Raised if a class method that requires weights is invoked, before weights have
    been calculated
    """

    def __init__(self, *args):
        super().__init__()

    def __str__(self):
        return (
            "This instance has not had weights calculated yet. Call `calc_weights`"
            + " before using this method."
        )


class ColumnNotFoundException(Exception):
    """Raised if provided column name not found in dataframe"""

    def __init__(self, *args):
        super().__init__()
        self.col = args[0]
        self.source = args[1]

    def __str__(self):
        return f"Column name '{self.col}' not found in {self.source} dataframe"


class StatisticException(Exception):
    """Raised if match dictionary is configured with an unsupported statistic"""

    def __init__(self, *args):
        super().__init__()
        self.statistic = args[0]

    def __str__(self):
        return (
            "Supported statistics are ('mean', 'std'), provided as the first item in"
            + f" the match dictionary values. '{self.statistic}' provided."
        )


class MeanConfigException(Exception):
    """Raised if match dictionary is incorrectly configured for mean statistic"""

    def __init__(self, *args):
        super().__init__()
        self.vals = args[0]

    def __str__(self):
        return (
            "Configuring for 'mean' requires two items in the match dictionary values."
            + f" {len(self.vals)} provided: {self.vals}"
        )


class StdConfigException(Exception):
    """Raised if match dictionary is incorrectly configured for std statistic"""

    def __init__(self, *args):
        super().__init__()
        self.vals = args[0]

    def __str__(self):
        return (
            "Configuring for 'std' requires three items in the match dictionary values."
            + f" {len(self.vals)} provided: {self.vals}"
        )


class ConfigException(Exception):
    """Raised if match dictionary values provided with only one string"""

    def __init__(self, *args):
        super().__init__()
        self.vals = args[0]

    def __str__(self):
        return (
            "Match dictionary values require two items for 'mean', or three items for"
            + f" 'std'. Provided: '{self.vals}'"
        )
