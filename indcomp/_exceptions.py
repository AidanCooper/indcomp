class NoWeightsException(Exception):
    """Raised if a class method that requires weights is invoked, before weights have
    been calculated
    """

    def __init__(self, *args):
        super().__init__()
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        return (
            "This instance has not had weights calculated yet. Call `calc_weights`"
            + " before using this method."
        )
