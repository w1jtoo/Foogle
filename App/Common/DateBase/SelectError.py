class SelectError(KeyError):
    """Raised when can't get select from date base. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)