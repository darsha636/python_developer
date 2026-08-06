import json
import zlib


def create_delta(previous_state, current_state):
    delta = {
        "added": {},
        "modified": {},
        "deleted": []
    }

    for key, current_value in current_state.items():
        if key not in previous_state:
            delta["added"][key] = current_value
        elif previous_state[key] != current_value:
            delta["modified"][key] = current_value

    for key in previous_state:
        if key not in current_state:
            delta["deleted"].append(key)

    return delta


def compress_delta(delta):
    json_data = json.dumps(
        delta,
        separators=(",", ":")
    ).encode("utf-8")

    return zlib.compress(json_data)


def decompress_delta(compressed_data):
    json_data = zlib.decompress(compressed_data)
    return json.loads(json_data.decode("utf-8"))


def reconstruct_state(previous_state, delta):
    reconstructed = previous_state.copy()

    reconstructed.update(delta["added"])
    reconstructed.update(delta["modified"])

    for key in delta["deleted"]:
        reconstructed.pop(key, None)

    return reconstructed


if __name__ == "__main__":

    previous_state = {
        "name": "Raji",
        "age": 21,
        "city": "Hyderabad"
    }

    current_state = {
        "name": "Raji",
        "age": 22,
        "city": "Hyderabad",
        "salary": 35000
    }

    print("===== Original States =====")
    print("Previous state:")
    print(previous_state)

    print("\nCurrent state:")
    print(current_state)

    delta = create_delta(
        previous_state,
        current_state
    )

    print("\n===== Delta =====")
    print(delta)

    compressed = compress_delta(delta)

    print("\n===== Compression =====")
    print("Compressed size:", len(compressed), "bytes")

    decompressed = decompress_delta(compressed)

    print("\n===== Decompressed Delta =====")
    print(decompressed)

    reconstructed = reconstruct_state(
        previous_state,
        decompressed
    )

    print("\n===== Reconstructed State =====")
    print(reconstructed)

    if reconstructed == current_state:
        print("\nSUCCESS: State reconstructed correctly.")
    else:
        print("\nERROR: State reconstruction failed.")