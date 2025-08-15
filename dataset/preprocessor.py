# preprocessor.py
import pandas as pd
import numpy as np
from pathlib import Path

# Ścieżki
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
COLLECTED_DIR = DATASET_DIR / "collected"
PROCESSED_DIR = DATASET_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

# Kolumny do usunięcia
DROP_COLS = ["src_ip", "dst_ip", "src_port", "dst_port"]

def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Usunięcie kolumn z identyfikatorami
    for col in DROP_COLS:
        if col in df.columns:
            df = df.drop(columns=[col])

    # 2. Zamiana inf / -inf na NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    # 3. Imputacja braków medianą dla kolumn numerycznych
    for col in df.select_dtypes(include=[np.number]).columns:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    return df

def process_one_dataset(folder_name: str):
    folder_path = COLLECTED_DIR / folder_name
    csv_files = list(folder_path.glob("*.csv"))

    if not csv_files:
        print(f"[WARN] Brak plików w {folder_path}")
        return

    # Wczytanie wszystkich CSV i połączenie
    df_list = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(df_list, ignore_index=True)

    # Czyszczenie
    df_clean = basic_clean(df)

    # Zapis
    output_file = PROCESSED_DIR / f"processed_{folder_name.split('_')[1]}.csv"
    df_clean.to_csv(output_file, index=False)
    print(f"[OK] Zapisano {output_file} ({len(df_clean)} rekordów)")

def main():
    collected_folders = [
        f.name for f in COLLECTED_DIR.iterdir()
        if f.is_dir() and f.name.startswith("collected_")
    ]

    for folder in collected_folders:
        process_one_dataset(folder)

if __name__ == "__main__":
    main()
