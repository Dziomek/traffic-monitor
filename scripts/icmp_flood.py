import os
import pandas as pd
import ipaddress

SOURCE_FOLDER = "records"
OUTPUT_FOLDER = "processed_stripped"
TARGET_PROTOCOL = 1
NEW_LABEL = "ICMP flood"

allowed_subnets = [
    ipaddress.ip_network("192.168.154.39"),
    ipaddress.ip_network("192.168.156.30")
]

COLUMNS_TO_DROP = ["src_ip", "dst_ip"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(SOURCE_FOLDER):
    if filename.endswith(".csv") and not filename.endswith("_PROC.csv"):
        source_path = os.path.join(SOURCE_FOLDER, filename)
        print(f"Processing: {filename}")

        try:
            df = pd.read_csv(source_path)

            if "protocol" not in df.columns or "label" not in df.columns or "src_ip" not in df.columns:
                print(f"Skipping {filename}: required columns missing")
                continue

            df["protocol"] = pd.to_numeric(df["protocol"], errors="coerce").round().astype("Int64")

            def is_ip_in_subnets(ip_str):
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    return any(ip_obj in subnet for subnet in allowed_subnets)
                except ValueError:
                    return False

            subnet_mask = df["src_ip"].apply(is_ip_in_subnets)
            proto_mask = df["protocol"] == TARGET_PROTOCOL
            combined_mask = proto_mask & subnet_mask

            count = combined_mask.sum()

            if count > 0:
                df.loc[combined_mask, "label"] = NEW_LABEL
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


