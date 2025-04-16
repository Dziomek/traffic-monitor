import os
import pandas as pd

SOURCE_FOLDER = "processed"
OUTPUT_FOLDER = "processed_stripped"

columns_to_drop = ["src_ip", "dst_ip"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for fname in os.listdir(SOURCE_FOLDER):
    if fname.endswith(".csv"):
        path = os.path.join(SOURCE_FOLDER, fname)
        df = pd.read_csv(path)

        dropped = [col for col in columns_to_drop if col in df.columns]
        df = df.drop(columns=dropped)

        new_name = fname.replace(".csv", "_stripped.csv")
        new_path = os.path.join(OUTPUT_FOLDER, new_name)
        df.to_csv(new_path, index=False)

        print(f"{new_name} saved({len(df.columns)} columns). Deleted: {dropped}")
