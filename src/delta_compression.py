class DeltaCompressor:

    def __init__(self):
        self.previous_values = {}

    def should_store(self, variable_name, current_value):
        # Check if variable exists and value is same
        if variable_name in self.previous_values:
            if self.previous_values[variable_name] == current_value:
                return False   # Skip storing

        # Value changed or first time value
        self.previous_values[variable_name] = current_value
        return True   # Store value