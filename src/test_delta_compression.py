from delta_compression import (
    create_delta,
    compress_delta,
    decompress_delta,
    reconstruct_state
)


# Previous execution state
previous_state = {
    "name": "samhi",
    "age": 21,
    "city": "Hyderabad"
}


# Current execution state
current_state = {
    "name": "samhi",
    "age": 22,
    "city": "Hyderabad"
}


# Create delta
delta = create_delta(previous_state, current_state)

print("Delta:")
print(delta)


# Compress delta
compressed = compress_delta(delta)

print("\nCompressed size:")
print(len(compressed), "bytes")


# Decompress
decompressed = decompress_delta(compressed)

print("\nDecompressed delta:")
print(decompressed)


# Reconstruct state
reconstructed = reconstruct_state(
    previous_state,
    decompressed
)

print("\nReconstructed state:")
print(reconstructed)


# Validate
if reconstructed == current_state:
    print("\nSUCCESS: State reconstructed correctly.")
else:
    print("\nERROR: State reconstruction failed.")