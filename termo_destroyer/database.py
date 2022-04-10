import pandas as pd
import requests
import os


def get_database():
    """Loads the database from IME USP. Big thanks to professor Paulo Feofiloff!"""

    data_url = "https://www.ime.usp.br/~pf/dicios/br-utf8.txt"
    data = requests.get(data_url).text.split("\n")

    # Creating dataframe and counting letters
    df = pd.DataFrame(data, columns=["id"])
    df["n_letters"] = df["id"].apply(lambda x: len(x))

    # Exporting to temp directory
    df.to_csv(os.path.join(os.environ["TEMP"], "data_TD.csv"), index=False)


def read_database(path, n_letters):
    """Reads the database from the given path."""

    # Reading by chunks, we don't want to load the whole file in memory
    iter_csv = pd.read_csv(
        path, iterator=True, chunksize=1000, dtype={"id": str, "n_letters": int}
    )
    df = pd.concat(
        [chunk[chunk["n_letters"] == n_letters] for chunk in iter_csv]
    )
    df.reset_index(drop=True, inplace=True)
    return df
