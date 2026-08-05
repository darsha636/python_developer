from delta_compression import (
    create_delta,
    compress_delta,
    decompress_delta,
    reconstruct_state
)

from storage import (
    store_compressed_delta,
    retrieve_compressed_delta
)


def run_week3_integration():

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

    print("=" * 50)
    print("PYCHRONICLE WEEK 3 INTEGRATION")
    print("=" * 50)

    print("\nPrevious state:")
    print(previous_state)

    print("\nCurrent state:")
    print(current_state)

    # Create delta
    delta = create_delta(
        previous_state,
        current_state
    )

    print("\nDelta:")
    print(delta)

    # Compress
    compressed = compress_delta(delta)

    print("\nCompressed delta size:")
    print(len(compressed), "bytes")

    # Store
    record_id = store_compressed_delta(
        compressed,
        line_number=1
    )

    print("\nStored record ID:")
    print(record_id)

    # Retrieve
    retrieved = retrieve_compressed_delta(
        record_id
    )

    print("\nRetrieved compressed data:")
    print(len(retrieved), "bytes")

    # Decompress
    decompressed = decompress_delta(
        retrieved
    )

    print("\nDecompressed delta:")
    print(decompressed)

    # Reconstruct
    reconstructed = reconstruct_state(
        previous_state,
        decompressed
    )

    print("\nReconstructed state:")
    print(reconstructed)

    # Validate
    print("\nValidation:")

    if reconstructed == current_state:
        print("SUCCESS: Reconstruction matches original state.")
    else:
        print("ERROR: Reconstruction does not match original state.")


if __name__ == "__main__":
    run_week3_integration()