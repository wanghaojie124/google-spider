import pandas as pd

df = pd.read_csv("name-count.csv", index_col=0)

df.sort_values(by="item_num", inplace=True, ascending=False)
df.to_csv("name-count.csv", index=False)
