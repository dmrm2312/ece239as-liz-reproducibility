import os
import json
import yaml
import time
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from text2 import send_telegram as sendText

LEADER_MODE = True

def load_config(yaml_path="config.yaml"):
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def load_dataset(path, feature_cols, label_col):
    df = pd.read_parquet(path)
    X = df[feature_cols]
    y = df[label_col]
    return X, y

def get_top_k_predictions(proba, k):
    return np.argsort(proba, axis=1)[:, -k:][:, ::-1]

def compute_precision_recall_f1_at_k(y_true, y_proba, k):
    top_k_preds = get_top_k_predictions(y_proba, k)
    precision_list = []
    recall_list = []

    for true_label, top_preds in zip(y_true, top_k_preds):
        if true_label in top_preds:
            precision = 1 / (np.where(top_preds == true_label)[0][0] + 1)
            recall = 1.0
        else:
            precision = 0.0
            recall = 0.0
        precision_list.append(precision)
        recall_list.append(recall)

    avg_precision = np.mean(precision_list)
    avg_recall = np.mean(recall_list)
    if avg_precision + avg_recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)

    return avg_precision, avg_recall, f1

def run_top_k_training(k=3):
    config = load_config("config.yaml")
    X_train, y_train = load_dataset(config['train_path'], config['feature_columns'], config['label_column'])
    X_val, y_val = load_dataset(config['val_path'], config['feature_columns'], config['label_column'])

    log_path = "results/sweep_log.csv"
    os.makedirs("final_models", exist_ok=True)
    log_exists = os.path.exists(log_path)
    all_trials = pd.read_csv(log_path) if log_exists else pd.DataFrame()

    if all_trials.empty:
        print("No trials found in the sweep log.")
        return

    top_k_trials = all_trials.sort_values(by="score", ascending=False).head(k)

    for idx, row in top_k_trials.iterrows():
        params = json.loads(row['config_hash'])
        # Overwrite for extended training
        params['iterations'] = 10000
        params['early_stopping_rounds'] = 300
        params['use_best_model'] = True
        params['verbose'] = 100
        params['eval_metric'] = "MultiClass"

        model = CatBoostClassifier(**params)
        start_time = time.time()
        model.fit(X_train, y_train, eval_set=(X_val, y_val))
        duration = time.time() - start_time

        y_pred = model.predict(X_val)
        y_proba = model.predict_proba(X_val)
        overall_f1 = f1_score(y_val, y_pred, average='weighted')
        acc = accuracy_score(y_val, y_pred)

        p1, r1, f1_1 = compute_precision_recall_f1_at_k(y_val.values, y_proba, k=1)
        p5, r5, f1_5 = compute_precision_recall_f1_at_k(y_val.values, y_proba, k=5)
        p30, r30, f1_30 = compute_precision_recall_f1_at_k(y_val.values, y_proba, k=30)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"final_models/model_K{idx+1}_{timestamp}.cbm"
        plot_filename = f"final_models/loss_plot_K{idx+1}_{timestamp}.png"
        metrics_filename = f"final_models/metrics_K{idx+1}_{timestamp}.txt"

        model.save_model(model_filename)

        if hasattr(model, 'get_evals_result'):
            evals_result = model.get_evals_result()
            if 'learn' in evals_result and 'Accuracy' in evals_result['learn']:
                plt.figure(figsize=(10, 4))
                plt.plot(evals_result['learn']['Accuracy'], label='Train Accuracy')
                if 'validation' in evals_result and 'Accuracy' in evals_result['validation']:
                    plt.plot(evals_result['validation']['Accuracy'], label='Validation Accuracy')
                plt.title(f"Model K={idx+1} Training Accuracy")
                plt.xlabel("Iteration")
                plt.ylabel("Accuracy")
                plt.legend()
                plt.tight_layout()
                plt.savefig(plot_filename)
                plt.close()

        with open(metrics_filename, 'w') as f:
            f.write(f"Model K={idx+1} - Trained on {timestamp}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Overall Accuracy: {acc:.4f}\n")
            f.write(f"Overall F1: {overall_f1:.4f}\n")
            f.write(f"Precision@1: {p1:.4f}\nRecall@1: {r1:.4f}\nF1@1: {f1_1:.4f}\n")
            f.write(f"Precision@5: {p5:.4f}\nRecall@5: {r5:.4f}\nF1@5: {f1_5:.4f}\n")
            f.write(f"Precision@30: {p30:.4f}\nRecall@30: {r30:.4f}\nF1@30: {f1_30:.4f}\n")

        if LEADER_MODE:
            message = (
                f"✅ Model K={idx+1} Training Complete\n"
                f"Overall F1: {overall_f1:.4f}, Acc: {acc:.4f}\n"
                f"F1@1: {f1_1:.4f}, F1@5: {f1_5:.4f}, F1@30: {f1_30:.4f}"
            )
            sendText("Model Training Update", message, plot_filename)

if __name__ == "__main__":
    run_top_k_training(k=3)
