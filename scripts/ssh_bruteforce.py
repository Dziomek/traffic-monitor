import os
import pandas as pd

SOURCE_FOLDER = "records"
OUTPUT_FOLDER = "processed"
ATTACKER_IP = "192.168.156.30"
columns_to_drop = ["src_ip", "dst_ip"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for fname in os.listdir(SOURCE_FOLDER):
    if fname.endswith(".csv"):
        path = os.path.join(SOURCE_FOLDER, fname)
        df = pd.read_csv(path)

        # Krok 1: Nadpisz label dla flowów od atakującego
        if "src_ip" in df.columns and "label" in df.columns:
            df.loc[df["src_ip"] == ATTACKER_IP, "label"] = "SSH_BRUTEFORCE"

        # Krok 2: Usuń zbędne kolumny
        dropped = [col for col in columns_to_drop if col in df.columns]
        df = df.drop(columns=dropped)

        # Krok 3: Zapisz jako *_stripped.csv
        new_name = fname.replace(".csv", "_PROC.csv")
        new_path = os.path.join(OUTPUT_FOLDER, new_name)
        df.to_csv(new_path, index=False)

        print(f"✅ {new_name} zapisany ({len(df.columns)} kolumn). Usunięto: {dropped}")
