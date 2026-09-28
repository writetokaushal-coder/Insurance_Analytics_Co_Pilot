import pandas as pd

from pathlib import Path

from src.database import engine


PROJECT_DIR = Path(
    __file__
).resolve().parents[1]

CURATED_DIR = (
    PROJECT_DIR
    / "data"
    / "curated"
)


TABLES = {
    "renewal_model_dataset.csv":
        "renewal_model_features",

    "fraud_model_dataset.csv":
        "fraud_model_features",

    "underwriting_model_dataset.csv":
        "underwriting_model_features",
}


for file_name, table_name in TABLES.items():

    path = (
        CURATED_DIR
        / file_name
    )

    if not path.exists():

        print(
            "[SKIP]",
            file_name,
            "not found."
        )

        continue

    df = pd.read_csv(
        path,
        low_memory=False
    )

    df.to_sql(
        name=table_name,
        con=engine,
        schema="analytics",
        if_exists="replace",
        index=False,
        chunksize=1000,
    )

    print(
        "[OK]",
        file_name,
        "->",
        f"analytics.{table_name}",
        df.shape,
    )
