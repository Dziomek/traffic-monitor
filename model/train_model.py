import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

INPUT_FOLDER = "processed"
MODEL_PATH = "model/rf_model.pkl"
ENCODER_PATH = "model/label_encoder.pkl"

dataframes = []
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".csv"):
        filepath = os.path.join(INPUT_FOLDER, filename)
        print(f"📄 Wczytywanie: {filename}")
        df = pd.read_csv(filepath)
        dataframes.append(df)

df_all = pd.concat(dataframes, ignore_index=True)
print(f"\nConnected{len(dataframes)} fles. {len(df_all)} flows in total.\n")

if "label" not in df_all.columns:
    raise ValueError("Missing 'label' column in data")

X = df_all.drop(columns=["src_ip", "dst_ip", "label", "src_port", "dst_port"], errors="ignore")
y = df_all["label"]

X = X.fillna(0)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)

print(f"Model saved as: {MODEL_PATH}")
print(f"Label encoder saved as: {ENCODER_PATH}")
print(f"Accuracy (train): {model.score(X_train, y_train):.4f}")
print(f"Accuracy (test): {model.score(X_test, y_test):.4f}")

