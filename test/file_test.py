import tkinter
from tkinter import filedialog, Tk
from pandas import read_csv
import sys
import os
from pandas import DataFrame
from datetime import datetime

Tk().withdraw()
# file = filedialog.askopenfile(mode='r', filetypes=[("CSV Files", " .csv")])
# print(file.readline())
# if not file:
#     print("XD")
#     sys.exit()
# print(file)
# df = read_csv(file)
# print(df.head())
# col_names = [c for c in df.columns]
# print(col_names)
# print(col_names == ['t [s]', 'Bx [mT]', 'By [mT]', 'Bz [mT]'] )
# print(type(df.columns))


f = filedialog.asksaveasfile(initialfile=datetime.now().strftime('%d-%m-%Y_%H_%M_%S.csv'), filetypes=[("CSV Files", ".csv")])
print(f)
print(f)
df = DataFrame({'dupa': [1,2], 'dupa2' : [3,4]})
df.to_csv(f)