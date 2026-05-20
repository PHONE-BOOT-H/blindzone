from src.train import train_and_save


def test_training_produces_reasonable_metrics():
    metrics = train_and_save()
    assert metrics["r2"] > 0.5
    assert metrics["mae"] < 0.1
