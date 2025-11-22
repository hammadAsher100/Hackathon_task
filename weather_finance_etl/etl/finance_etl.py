import pandas as pd

def transform_finance(raw):
    if raw is None:
        return None

    ts_key = None
    for key in raw.keys():
        if "Time Series" in key:
            ts_key = key
            break

    if ts_key is None:
        return None

    df = (
        pd.DataFrame.from_dict(raw[ts_key], orient="index")
        .rename(columns=lambda c: c.split(". ")[1])
    )

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    return df
