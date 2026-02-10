import pandas as pd
from pathlib import Path

force_sheet_index = pd.read_csv(r"data\aero force sheet idx.csv")
print(force_sheet_index)
print(force_sheet_index.iloc[0, 1])