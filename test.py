
import pandas as pd

force_sheet_index = pd.read_csv(r"data\aero force sheet idx.csv")
force_sheet_index.columns = force_sheet_index.columns.str.strip()
print(force_sheet_index)
print(len(force_sheet_index["rows"]))

for i, row in enumerate(force_sheet_index["rows"]):
    print(row, force_sheet_index.iloc[i, 2])