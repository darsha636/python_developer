from src.delta_compression import DeltaCompressor


def test_same_value_skip():
    compressor = DeltaCompressor()

    assert compressor.should_store("age", 20) == True
    assert compressor.should_store("age", 20) == False


def test_changed_value_store():
    compressor = DeltaCompressor()

    compressor.should_store("age", 20)

    assert compressor.should_store("age", 25) == True


def test_multiple_variables():
    compressor = DeltaCompressor()

    assert compressor.should_store("name", "Darsha") == True
    assert compressor.should_store("age", 22) == True
    assert compressor.should_store("city", "Vadodara") == True