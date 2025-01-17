import pandas as pd

def read_jsonl(file_path):
    return pd.read_json(file_path, lines=True)