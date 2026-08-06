import json
import zlib


def create_delta(previous_state, current_state):

    delta = {
        "added": {},
        "modified": {},
        "deleted": []
    }

    for key, value in current_state.items():

        if key not in previous_state:
            delta["added"][key] = value

        elif previous_state[key] != value:
            delta["modified"][key] = value

    for key in previous_state:

        if key not in current_state:
            delta["deleted"].append(key)

    return delta


def reconstruct_state(previous_state, delta):

    state = previous_state.copy()

    state.update(delta["added"])
    state.update(delta["modified"])

    for key in delta["deleted"]:
        state.pop(key, None)

    return state


def compress_delta(delta):

    data = json.dumps(
        delta,
        separators=(",", ":")
    ).encode("utf-8")

    return zlib.compress(data)


def run_test(test_name, previous_state, current_state):

    print("\n" + "=" * 60)
    print(test_name)
    print("=" * 60)

    full_state_data = json.dumps(
        current_state
    ).encode("utf-8")

    delta = create_delta(
        previous_state,
        current_state
    )

    delta_data = json.dumps(
        delta,
        separators=(",", ":")
    ).encode("utf-8")

    compressed_delta = compress_delta(delta)

    reconstructed = reconstruct_state(
        previous_state,
        delta
    )

    print("Original state:")
    print(current_state)

    print("\nDelta:")
    print(delta)

    print("\nOriginal state size:")
    print(len(full_state_data), "bytes")

    print("Delta size:")
    print(len(delta_data), "bytes")

    print("Compressed delta size:")
    print(len(compressed_delta), "bytes")

    if len(full_state_data) > 0:

        reduction = (
            (len(full_state_data) - len(compressed_delta))
            / len(full_state_data)
        ) * 100

    else:

        reduction = 0

    print(
        "Storage reduction:",
        round(reduction, 2),
        "%"
    )

    if reconstructed == current_state:
        print("Reconstruction: PASS")
    else:
        print("Reconstruction: FAIL")


def main():

    # Test 1
    previous = {
        "name": "samhitha",
        "age": 21,
        "city": "Hyderabad"
    }

    current = {
        "name": "samhitha",
        "age": 22,
        "city": "Hyderabad"
    }

    run_test(
        "TEST 1 - Modified Variable",
        previous,
        current
    )

    # Test 2
    previous = {
        "name": "samhitha",
        "age": 21
    }

    current = {
        "name": "samhitha",
        "age": 22,
        "salary": 35000,
        "city": "Hyderabad"
    }

    run_test(
        "TEST 2 - Multiple Changes",
        previous,
        current
    )

    # Test 3
    previous = {
        "name": "samhitha",
        "age": 21,
        "city": "Hyderabad"
    }

    current = {
        "name": "samhitha",
        "age": 21
    }

    run_test(
        "TEST 3 - Deleted Variable",
        previous,
        current
    )


if __name__ == "__main__":
    main()