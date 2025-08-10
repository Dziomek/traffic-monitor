import os
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import argparse
import optuna

parser = argparse.ArgumentParser()
parser.add_argument('--dataset_type', type=int, choices=[5, 10, 15, 20, 25, 30], required=True)
args = parser.parse_args()

INPUT_FOLDER = f"collected_{args.dataset_type}s"
MODEL_PATH = f"model/rf_model_{args.dataset_type}s.pkl"
ENCODER_PATH = f"model/label_encoder_{args.dataset_type}s.pkl"

COLUMNS_TO_DROP = ["src_ip", "dst_ip", "label"]

dataframes = []
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".csv"):
        filepath = os.path.join(INPUT_FOLDER, filename)
        print(f"File: {filename}")
        df = pd.read_csv(filepath)
        dataframes.append(df)

df_all = pd.concat(dataframes, ignore_index=True)
print(f"\nConnected {len(dataframes)} files. {len(df_all)} flows in total.\n")

if "label" not in df_all.columns:
    raise ValueError("Missing 'label' column in data")

X = df_all.drop(columns=COLUMNS_TO_DROP, errors="ignore")
y = df_all["label"]

X = X.fillna(0)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=1900617256)

# optuna
# def objective(trial): 
#     print('starting trial')
#     n_estimators = trial.suggest_int('n_estimators', 1, 200)
#     criterion = trial.suggest_categorical('criterion', ['gini', 'entropy', 'log_loss'])
#     model = RandomForestClassifier(n_estimators=n_estimators, criterion=criterion, random_state=2584215091)
#     score = cross_val_score(model, X_train, y_train, cv=3, scoring='f1_macro').mean()

#     return score

# study = optuna.create_study(direction='maximize')
# study.optimize(objective, n_trials=10)
# best_params = study.best_params
# print(best_params)

# model = RandomForestClassifier(n_estimators=best_params['n_estimators'], 
#                                criterion=best_params['criterion'], random_state=785912901)
model = RandomForestClassifier(random_state=785912901)
model.fit(X_train, y_train)

joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)

print(f"Model saved as: {MODEL_PATH}")
print(f"Label encoder saved as: {ENCODER_PATH}")
print(f"Accuracy (train): {model.score(X_train, y_train):.4f}")
print(f"Accuracy (test): {model.score(X_test, y_test):.4f}")

y_pred = model.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_, cmap="Blues")
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

importances = model.feature_importances_
feature_names = X.columns
feature_importances = pd.DataFrame({
    'feature': feature_names,
    'importance': importances
}).sort_values(by="importance", ascending=False)

print("\nTop 10 most important features:")
print(feature_importances.head(10))


