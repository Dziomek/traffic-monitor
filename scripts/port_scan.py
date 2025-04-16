import os
import pandas as pd

SOURCE_FOLDER = "records"
OUTPUT_FOLDER = "processed_stripped"
NEW_LABEL = "PORT_SCAN"

IP_A = "192.168.154.39"
IP_B = "192.168.156.30"

COLUMNS_TO_DROP = ["src_ip", "dst_ip"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def is_flow_between_ips(row, ip1, ip2):
    src = row["src_ip"]
    dst = row["dst_ip"]
    return (src == ip1 and dst == ip2) or (src == ip2 and dst == ip1)

for filename in os.listdir(SOURCE_FOLDER):
    if filename.endswith(".csv") and not filename.endswith("_PROC.csv"):
        source_path = os.path.join(SOURCE_FOLDER, filename)
        print(f"Processing: {filename}")

        try:
            df = pd.read_csv(source_path)

            if "src_ip" not in df.columns or "dst_ip" not in df.columns or "label" not in df.columns:
                print(f"Skipping {filename}: required columns not found")
                continue

            mask = df.apply(is_flow_between_ips, axis=1, ip1=IP_A, ip2=IP_B)
            count = mask.sum()

            if count > 0:
                df.loc[mask, "label"] = NEW_LABEL
                print(f"Labeled {count} flows as '{NEW_LABEL}'")
            else:
                print("No matching flows found")

            df = df.drop(columns=[col for col in COLUMNS_TO_DROP if col in df.columns])

            new_filename = filename.replace(".csv", "_stripped.csv")
            output_path = os.path.join(OUTPUT_FOLDER, new_filename)
            df.to_csv(output_path, index=False)
            print(f"Saved to: {output_path}\n")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

