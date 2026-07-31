import json
import zlib


def create_delta(previous_state, current_state):
    """
    Create a delta containing only the values that changed.
    """

    delta = {}

    all_keys = set(previous_state) | set(current_state)

    for key in all_keys:

        old_value = previous_state.get(key)
        new_value = current_state.get(key)

        if old_value != new_value:
            delta[key] = new_value

    return delta


def compress_delta(delta):
    """
    Convert the delta to JSON and compress it using zlib.
    """

    json_data = json.dumps(delta).encode("utf-8")

    compressed_data = zlib.compress(json_data)

    return compressed_data


def decompress_delta(compressed_data):
    """
    Decompress the delta and convert it back to a dictionary.
    """

    json_data = zlib.decompress(compressed_data).decode("utf-8")

    return json.loads(json_data)


def reconstruct_state(previous_state, delta):
    """
    Apply the delta to the previous state
    and reconstruct the current state.
    """

    reconstructed_state = previous_state.copy()

    reconstructed_state.update(delta)

    return reconstructed_state