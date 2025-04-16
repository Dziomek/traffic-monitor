import os
import pandas as pd
import ipaddress

# === PARAMETRY ===
SOURCE_FOLDER = "records"
OUTPUT_FOLDER = "processed"
TARGET_PROTOCOL = 1
NEW_LABEL = "ICMP flood"

# Zdefiniowane dozwolone podsieci (dla atakującego i ofiary)
allowed_subnets = [
    ipaddress.ip_network("192.168.154.39"),
    ipaddress.ip_network("192.168.156.30")
]

# Utwórz folder wyjściowy, jeśli nie istnieje
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(SOURCE_FOLDER):
    if filename.endswith(".csv") and not filename.endswith("_PROC.csv"):
        source_path = os.path.join(SOURCE_FOLDER, filename)
        print(f"🔍 Przetwarzam: {filename}")

        try:
            df = pd.read_csv(source_path)

            if "protocol" not in df.columns or "label" not in df.columns or "src_ip" not in df.columns:
                print(f"⚠️  Pomijam {filename}: brak wymaganych kolumn ('protocol', 'src_ip', 'label')")
                continue

            # Konwersja protokołu
            df["protocol"] = pd.to_numeric(df["protocol"], errors="coerce").round().astype("Int64")

            # Sprawdź które IP należą do dozwolonych podsieci
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
                print(f"✅ Oznaczono {count} flowów jako '{NEW_LABEL}'")
            else:
                print("ℹ️  Brak pasujących flowów do oznaczenia")

            # Zapisz wynik
            new_filename = filename.replace(".csv", "_PROC.csv")
            output_path = os.path.join(OUTPUT_FOLDER, new_filename)
            df.to_csv(output_path, index=False)
            print(f"💾 Zapisano do: {output_path}\n")

        except Exception as e:
            print(f"❌ Błąd przy pliku {filename}: {e}")

