import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# === PARAMETRY ===
INPUT_FOLDER = "processed"
MODEL_PATH = "rf_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

# === Wczytaj i połącz wszystkie CSV ===
dataframes = []
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".csv"):
        filepath = os.path.join(INPUT_FOLDER, filename)
        print(f"📄 Wczytywanie: {filename}")
        df = pd.read_csv(filepath)
        dataframes.append(df)

# Połącz dane
df_all = pd.concat(dataframes, ignore_index=True)
print(f"\n✅ Połączono {len(dataframes)} plików. Razem {len(df_all)} flowów.\n")

# === Przygotuj dane ===
if "label" not in df_all.columns:
    raise ValueError("Brakuje kolumny 'label' w danych!")

# Oddziel cechy od etykiety
X = df_all.drop(columns=["src_ip", "dst_ip", "label"], errors="ignore")
y = df_all["label"]

# Zamień NaN na 0
X = X.fillna(0)

# Zakoduj etykiety
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# === Podział na train/test ===
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# === Trenuj model ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === Zapisz model i encoder ===
joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)

print(f"🎉 Model zapisany jako: {MODEL_PATH}")
print(f"🎉 Label encoder zapisany jako: {ENCODER_PATH}")
print(f"🎯 Accuracy (train): {model.score(X_train, y_train):.4f}")
print(f"🧪 Accuracy (test): {model.score(X_test, y_test):.4f}")

