import pickle
import zlib


def create_delta(previous_state, current_state):
    """
    Create a delta containing only the changes between two states.
    """

    delta = {
        "added": {},
        "modified": {},
        "deleted": {}
    }

    # Detect added and modified variables
    for key, current_value in current_state.items():

        if key not in previous_state:
            delta["added"][key] = current_value

        elif previous_state[key] != current_value:
            delta["modified"][key] = current_value

    # Detect deleted variables
    for key in previous_state:

        if key not in current_state:
            delta["deleted"][key] = previous_state[key]

    return delta


def compress_delta(delta):
    """
    Serialize and compress the delta.
    """

    serialized = pickle.dumps(delta)

    compressed = zlib.compress(serialized)

    return compressed


def decompress_delta(compressed_data):
    """
    Decompress and deserialize the delta.
    """

    serialized = zlib.decompress(compressed_data)

    delta = pickle.loads(serialized)

    return delta


def reconstruct_state(previous_state, delta):
    """
    Reconstruct the current state using the previous state and delta.
    """

    reconstructed = previous_state.copy()

    # Add new variables
    for key, value in delta["added"].items():
        reconstructed[key] = value

    # Apply modified variables
    for key, value in delta["modified"].items():
        reconstructed[key] = value

    # Remove deleted variables
    for key in delta["deleted"]:
        reconstructed.pop(key, None)

    return reconstructed


if __name__ == "__main__":

    previous_state = {
        "name": "samhitha",
        "age": 21,
        "city": "Hyderabad",
        "salary": 35000
    }

    current_state = {
        "name": "samhitha",
        "age": 22,
        "city": "Hyderabad",
        "salary": 40000
    }

    print("Previous state:")
    print(previous_state)

    print("\nCurrent state:")
    print(current_state)

    delta = create_delta(previous_state, current_state)

    print("\nDelta:")
    print(delta)

    compressed = compress_delta(delta)

    print("\nOriginal delta size:", len(pickle.dumps(delta)), "bytes")
    print("Compressed delta size:", len(compressed), "bytes")

    decompressed = decompress_delta(compressed)

    print("\nDecompressed delta:")
    print(decompressed)

    reconstructed = reconstruct_state(
        previous_state,
        decompressed
    )

    print("\nReconstructed state:")
    print(reconstructed)

    if reconstructed == current_state:
        print("\nSUCCESS: State reconstructed correctly.")
    else:
        print("\nERROR: State reconstruction failed.")