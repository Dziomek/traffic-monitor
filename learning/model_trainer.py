from pathlib import Path
import json, random, time, platform, argparse
from collections import Counter

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    RepeatedStratifiedKFold,
    GridSearchCV,
    RandomizedSearchCV,
)
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from joblib import dump

from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE

DEFAULT_DATASET_FILE = "processed_10s.csv"
DEFAULT_MODEL_NAME = "RandomForest"   # RandomForest | LogisticRegression | SVM
USE_RESAMPLING = True                 # undersampling + SMOTE

CV_SPLITS = 3
CV_REPEATS = 3

# RandomizedSearch iteracje (dla LR/SVM)
LR_N_ITER = 12
SVM_N_ITER = 16

# Resampling caps
UNDER_CAP = 50_000
OVER_TARGET = 5_000

RANDOM_STATE = random.randint(1, 10_000_000)

THIS_DIR = Path(__file__).resolve().parent
BASE_DIR = THIS_DIR.parent
DATA_DIR = BASE_DIR / "dataset" / "processed"
RUNS_DIR = THIS_DIR / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


# ================== UTIL: dane ==================
def load_data(path: Path):
    df = pd.read_csv(path)
    X = df.drop(columns=["label"])
    y = df["label"]
    return df, X, y

def encode_labels(y: pd.Series):
    le = LabelEncoder()
    y_enc = le.fit_transform(y.values)
    return y_enc, le

def under_strategy(y):
    cnt = Counter(y)
    return {cls: min(n, UNDER_CAP) for cls, n in cnt.items()}

def over_strategy(y):
    cnt = Counter(y)
    return {cls: max(n, OVER_TARGET) for cls, n in cnt.items()}

def build_samplers(random_state: int):
    under = RandomUnderSampler(sampling_strategy=under_strategy, random_state=random_state)
    smote = SMOTE(sampling_strategy=over_strategy, random_state=random_state)
    return under, smote


# ================== MODEL CONFIGS ==================
MODEL_CONFIGS = {
    "RandomForest": (
        RandomForestClassifier(
            random_state=RANDOM_STATE,
        ),
        {
            "clf__n_estimators": [100, 300],
            "clf__criterion": ['gini', 'entropy', 'log_loss']
        },
    ),
    "LogisticRegression": (
        LogisticRegression(
            random_state=RANDOM_STATE,
        ),
        {
            "clf__solver": ['lbfgs', 'liblinear', 'saga'],
            "clf__C": [0.5, 1]
        },
    ),
    "SVM": (
        SVC(
            random_state=RANDOM_STATE,
        ),
        {
            "clf__kernel": ["linear", "rbf"],
            "clf__C": np.logspace(-3, 1, 5)
        },
    ),
}


# ================== PIPELINE ==================
def build_pipeline(clf, use_resampling: bool, random_state: int):
    steps = []
    if use_resampling:
        under, smote = build_samplers(random_state)
        steps += [("under", under), ("smote", smote)]

    needs_scaling = isinstance(clf, (LogisticRegression, SVC))
    if needs_scaling:
        steps.append(("scaler", StandardScaler()))

    steps.append(("clf", clf))
    return Pipeline(steps=steps)


# ================== MAIN ==================
def main():
    parser = argparse.ArgumentParser(description="Model learner (choose model via --model, dataset via --dataset).")
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME,
                        choices=list(MODEL_CONFIGS.keys()),
                        help="Which model to train: RandomForest | LogisticRegression | SVM")
    parser.add_argument("--dataset", default=DEFAULT_DATASET_FILE,
                        help="CSV file name in dataset/processed/")
    args = parser.parse_args()

    dataset_path = DATA_DIR / args.dataset

    # --- Load ---
    df, X, y = load_data(dataset_path)
    dataset_counts = df["label"].value_counts().to_dict()

    # --- Encode labels ---
    y_enc, label_encoder = encode_labels(y)

    # # --- Safety: każda klasa >= 2 próbki (wymóg stratify) ---
    # cls_counts = pd.Series(y_enc).value_counts()
    # too_small = cls_counts[cls_counts < 2]
    # if len(too_small):
    #     raise RuntimeError(
    #         f"Zbyt małe klasy (<2 próbki) w danych: {too_small.to_dict()}. "
    #         f"Napraw dane wejściowe lub usuń te klasy."
    #     )

    # --- Train/Test split ---
    Xtr, Xte, ytr, yte = train_test_split(
        X, y_enc, test_size=0.2, stratify=y_enc, random_state=RANDOM_STATE
    )

    if label_encoder is not None:
        ytr_labels = pd.Series(label_encoder.inverse_transform(ytr))
        yte_labels = pd.Series(label_encoder.inverse_transform(yte))
    else:
        ytr_labels = pd.Series(ytr)
        yte_labels = pd.Series(yte)
    train_counts = ytr_labels.value_counts().to_dict()
    test_counts  = yte_labels.value_counts().to_dict()

    # --- Model + param grid ---
    clf_base, param_space = MODEL_CONFIGS[args.model]

    # --- Pipeline ---
    pipe = build_pipeline(clf_base, use_resampling=USE_RESAMPLING, random_state=RANDOM_STATE)

    # CV
    cv = RepeatedStratifiedKFold(
        n_splits=CV_SPLITS, n_repeats=CV_REPEATS, random_state=RANDOM_STATE
    )

    # grid
    search = GridSearchCV(
        estimator=pipe,
        param_grid=param_space,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=1,
    )

    # fit
    t0 = time.time()
    search.fit(Xtr, ytr)
    fit_seconds = time.time() - t0
    best_estimator = search.best_estimator_

    # --- Test evaluation ---
    y_pred = best_estimator.predict(Xte)
    if label_encoder is not None:
        yte_rep  = label_encoder.inverse_transform(yte)
        ypr_rep  = label_encoder.inverse_transform(y_pred)
    else:
        yte_rep, ypr_rep = yte, y_pred

    test_metrics = {
        "accuracy": float(accuracy_score(yte_rep, ypr_rep)),
        "f1_macro": float(f1_score(yte_rep, ypr_rep, average="macro")),
        "f1_weighted": float(f1_score(yte_rep, ypr_rep, average="weighted")),
    }
    report = classification_report(yte_rep, ypr_rep, output_dict=True, zero_division=0)
    cm = confusion_matrix(yte_rep, ypr_rep).tolist()

    # --- Zapisy ---
    run_tag = f"{args.model.lower()}_{Path(args.dataset).stem}_{RANDOM_STATE}"
    run_dir = RUNS_DIR / run_tag
    run_dir.mkdir(parents=True, exist_ok=True)

    dump(best_estimator, run_dir / "model.joblib")
    if label_encoder is not None:
        dump(label_encoder, run_dir / "label_encoder.joblib")

    pd.DataFrame(search.cv_results_).to_csv(run_dir / "cv_results.csv", index=False)

    metrics = {
        "data": {
            "dataset_file": str(dataset_path),
            "dataset_class_distribution": dataset_counts,
            "n_total": int(len(df)),
            "n_train": int(len(ytr)),
            "n_test": int(len(yte)),
            "class_distribution_train": train_counts,
            "class_distribution_test": test_counts
        },
        "cv": {
            "type": "RepeatedStratifiedKFold",
            "n_splits": CV_SPLITS,
            "n_repeats": CV_REPEATS,
            "random_state": RANDOM_STATE,
            "scoring": "f1_macro",
            "best_params": search.best_params_,
            "best_score_mean": float(search.best_score_),
            "search_kind": "GridSearchCV" if isinstance(search, GridSearchCV) else "RandomizedSearchCV",
            "n_iter": int(getattr(search, "n_iter", 0)),
        },
        "test": {
            "random_state_split": RANDOM_STATE,
            "metrics": test_metrics,
            "classification_report": report,
            "confusion_matrix": cm
        },
        "model": {
            "name": args.model,
            "use_resampling": USE_RESAMPLING,
            "class_weight": getattr(best_estimator.named_steps.get("clf"), "class_weight", None),
            "under_cap": UNDER_CAP,
            "over_target": OVER_TARGET
        },
        "env": {
            "python": platform.python_version(),
            "sklearn": __import__("sklearn").__version__,
            "imblearn": __import__("imblearn").__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__
        },
        "timing": {"fit_seconds": float(fit_seconds)}
    }
    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved run to: {run_dir}")
    print(f"     best params: {search.best_params_}")
    print(f"     test macro-F1: {test_metrics['f1_macro']:.4f} | acc: {test_metrics['accuracy']:.4f}")


if __name__ == "__main__":
    main()
