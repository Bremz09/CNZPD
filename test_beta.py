import pandas as pd
df = pd.read_csv("your_file.csv")  # replace with your actual filename
print(df.groupby("Andrews")["race_id_name"].count().describe())