import os
import pandas as pd

SOURCE_FOLDER = "records"
OUTPUT_FOLDER = "processed"
ATTACKER_IP = "192.168.156.30"
NEW_LABEL = "FTP_BRUTEFORCE"

COLUMNS_TO_DROP = ["src_ip", "dst_ip"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(SOURCE_FOLDER):
    if filename.endswith(".csv") and not filename.endswith("_PROC.csv"):
        source_path = os.path.join(SOURCE_FOLDER, filename)
        print(f"Processing: {filename}")

        try:
            df = pd.read_csv(source_path)

            if not {"src_ip", "label"}.issubset(df.columns):
                print(f"Skipping {filename}: required columns missing")
                continue

            mask = df["src_ip"] == ATTACKER_IP
            count = mask.sum()

            if count > 0:
                df.loc[mask, "label"] = NEW_LABEL
                print(f"Labeled {count} flows as '{NEW_LABEL}'")
            else:
                print("No matching flows found")

            # df = df.drop(columns=[col for col in COLUMNS_TO_DROP if col in df.columns])

            new_filename = filename.replace(".csv", "_PROC.csv")
            output_path = os.path.join(OUTPUT_FOLDER, new_filename)
            df.to_csv(output_path, index=False)
            print(f"Saved to: {output_path}\n")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
