class DeltaCompressor:
    """
    Stores the previous value of each variable
    to detect changes.
    """

    def __init__(self):
        self.previous_values = {}