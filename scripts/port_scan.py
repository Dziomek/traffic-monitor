import os
import pandas as pd

# === PARAMETRY ===
SOURCE_FOLDER = "records"
OUTPUT_FOLDER = "processed"
NEW_LABEL = "PORT_SCAN"

IP_A = "192.168.154.39"
IP_B = "192.168.156.30"

# Utwórz folder wyjściowy
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Pomocnicza funkcja do wykrywania relacji A-B lub B-A
def is_flow_between_ips(row, ip1, ip2):
    src = row["src_ip"]
    dst = row["dst_ip"]
    return (src == ip1 and dst == ip2) or (src == ip2 and dst == ip1)

# Przetwarzaj pliki
for filename in os.listdir(SOURCE_FOLDER):
    if filename.endswith(".csv") and not filename.endswith("_PROC.csv"):
        source_path = os.path.join(SOURCE_FOLDER, filename)
        print(f"🔍 Przetwarzam: {filename}")

        try:
            df = pd.read_csv(source_path)

            if "src_ip" not in df.columns or "dst_ip" not in df.columns or "label" not in df.columns:
                print(f"⚠️  Pomijam {filename}: brak wymaganych kolumn")
                continue

            # Znajdź flowy pomiędzy IP_A i IP_B (w obu kierunkach)
            mask = df.apply(is_flow_between_ips, axis=1, ip1=IP_A, ip2=IP_B)
            count = mask.sum()

            if count > 0:
                df.loc[mask, "label"] = NEW_LABEL
                print(f"✅ Oznaczono {count} flowów jako '{NEW_LABEL}'")
            else:
                print("ℹ️  Brak flowów do oznaczenia")

            # Zapisz plik
            new_filename = filename.replace(".csv", "_PROC.csv")
            output_path = os.path.join(OUTPUT_FOLDER, new_filename)
            df.to_csv(output_path, index=False)
            print(f"💾 Zapisano do: {output_path}\n")

        except Exception as e:
            print(f"❌ Błąd przy pliku {filename}: {e}")
