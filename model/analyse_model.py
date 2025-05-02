import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

MODEL_PATH = "model/rf_model.pkl"
ENCODER_PATH = "model/label_encoder.pkl"
DATA_PATH = "processed"

dataframes = []
for filename in os.listdir(DATA_PATH):
    if filename.endswith(".csv"):
        filepath = os.path.join(DATA_PATH, filename)
        df = pd.read_csv(filepath)
        dataframes.append(df)

df_all = pd.concat(dataframes, ignore_index=True)

X = df_all.drop(columns=["src_ip", "dst_ip", "label", "src_port", "dst_port"], errors="ignore").fillna(0)
y = df_all["label"]

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

y_true_encoded = encoder.transform(y)
y_pred_encoded = model.predict(X)

print("\nClassification report:\n")
print(classification_report(y_true_encoded, y_pred_encoded, target_names=encoder.classes_))

conf_matrix = confusion_matrix(y_true_encoded, y_pred_encoded)
conf_matrix = conf_matrix / conf_matrix.sum(axis=0)
plt.figure(figsize=(10, 7))
sns.heatmap(conf_matrix, annot=True, fmt='.04f', xticklabels=encoder.classes_, yticklabels=encoder.classes_, cmap="Blues")
plt.xlabel("Predicted label")
plt.ylabel("True label")
plt.title("Confusion matrix")
plt.tight_layout()
plt.show()

feature_importances = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

print("\nFeature importances:\n")
print(feature_importances.to_string(index=False))
