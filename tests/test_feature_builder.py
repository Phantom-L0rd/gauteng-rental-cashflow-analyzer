import pandas as pd
from src.etl.feature_builder import RentalFeatureBuilder

def test_floor_size_imputation():
    df = pd.DataFrame({
        "location": ["A", "A", "B"],
        "total_rooms": [4, 4, 3],
        "floor_size": [80, None, 120],
        "price": [8000, 8500, 15000]
    })

    builder = RentalFeatureBuilder()
    df_out = builder.smart_imputation(df)

    assert df_out["floor_size"].isnull().sum() == 0
