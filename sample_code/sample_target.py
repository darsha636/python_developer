from src.delta_compression import DeltaCompressor


compressor = DeltaCompressor()

states = [
    ("age", 20),
    ("age", 20),
    ("age", 25),
    ("age", 25)
]


for name, value in states:
    result = compressor.should_store(name, value)

    if result:
        print(f"Store: {name} = {value}")
    else:
        print(f"Skip: {name} = {value}")