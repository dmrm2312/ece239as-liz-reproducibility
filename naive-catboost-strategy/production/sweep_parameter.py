import os
import json
import yaml
import time
import traceback
import datetime
import pandas as pd
import optuna
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.model_selection import train_test_split
from text2 import send_telegram as sendText
import matplotlib.pyplot as plt


def load_config(yaml_path="config.yaml"):
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def load_dataset(path, feature_cols, label_col):
    df = pd.read_parquet(path)
    X = df[feature_cols]
    y = df[label_col]
    return X, y


def score_model(model, X_val, y_val):
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)
    acc = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, average="weighted")
    loss = log_loss(y_val, y_proba, labels=list(range(y_proba.shape[1])))
    return acc, f1, loss


def score_function(acc, f1, loss, duration, iterations):
    efficiency = iterations / max(duration, 1e-5)
    return 0.4 * acc + 0.4 * f1 - 0.1 * loss + 0.1 * (efficiency / 1000)


def run_sweep():
    config = load_config("config.yaml")
    X_train, y_train = load_dataset(config['train_path'], config['feature_columns'], config['label_column'])
    X_val, y_val = load_dataset(config['val_path'], config['feature_columns'], config['label_column'])

    log_path = "results/sweep_log.csv"
    os.makedirs("results", exist_ok=True)
    log_exists = os.path.exists(log_path)
    all_trials = pd.read_csv(log_path) if log_exists else pd.DataFrame(columns=[
        "trial", "config_hash", "score", "accuracy", "f1", "log_loss", "duration", "timestamp"])

    best_score = -999.0
    last_heartbeat = time.time()
    trial_idx = 0

    def objective(trial):
        nonlocal best_score, trial_idx, all_trials, last_heartbeat

        params = {
            "iterations": trial.suggest_int("iterations", 100, 1000),
            "depth": trial.suggest_int("depth", 4, 11),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1e-3, 10.0, log=True),
            "random_strength": trial.suggest_float("random_strength", 1e-3, 5.0, log=True),
            "eval_metric": "Accuracy",
            "loss_function": "MultiClass",
            "task_type": "GPU",
            "verbose": 0
        }

        model = CatBoostClassifier(**params)
        start = time.time()

        valid_mask = y_val.isin(y_train.unique())
        X_val_filtered = X_val[valid_mask]
        y_val_filtered = y_val[valid_mask]

        try:
            model.fit(X_train, y_train, eval_set=(X_val_filtered, y_val_filtered), use_best_model=True)
        except Exception as fit_err:
            tb = traceback.format_exc()
            sendText("CUDA Error", f"Trial {trial_idx} failed.\nDepth={params['depth']} Iter={params['iterations']} L2={params['l2_leaf_reg']:.5f}\nError: {str(fit_err)[:240]}")
            raise optuna.exceptions.TrialPruned()

        acc, f1, loss = score_model(model, X_val_filtered, y_val_filtered)
        duration = time.time() - start
        final_score = score_function(acc, f1, loss, duration, model.tree_count_)

        config_hash = json.dumps(params, sort_keys=True)

        if not all_trials.empty and config_hash in all_trials['config_hash'].values:
            raise optuna.exceptions.TrialPruned()

        now = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        all_trials.loc[len(all_trials)] = [trial_idx, config_hash, final_score, acc, f1, loss, duration, now]
        all_trials.to_csv(log_path, index=False)

        if final_score > best_score:
            best_score = final_score

        date = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        config_id = f"{date}_score{final_score:.4f}"
        with open(os.path.join("results", f"{config_id}_config.json"), 'w') as f:
            json.dump(params, f, indent=2)

        if (time.time() - last_heartbeat) > 1800/2:
            now = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

            # Filter for last 4 hours
            all_trials['timestamp'] = pd.to_datetime(all_trials['timestamp'], format="%y-%m-%d %H:%M:%S")
            cutoff = pd.Timestamp.now() - pd.Timedelta(hours=4)
            recent = all_trials[all_trials['timestamp'] > cutoff]

            # Plot recent scores
            plt.figure(figsize=(10, 4))
            plt.plot(recent['timestamp'], recent['score'], marker='o', label="All Scores")
            if not recent.empty:
                best_recent = recent['score'].cummax()
                plt.plot(recent['timestamp'], best_recent, linestyle='--', label="Best Score")
            plt.xticks(rotation=45, ha='right')
            plt.title("Sweep Scores - Last 4 Hours")
            plt.xlabel("Timestamp")
            plt.ylabel("Score")
            plt.legend()
            plt.tight_layout()
            plot_path = "results/heartbeat_score_plot.png"
            plt.savefig(plot_path)
            plt.close()

            # Determine score delta
            delta_msg = ""
            if not recent.empty:
                delta = best_recent.iloc[-1] - best_recent.iloc[0]
                delta_msg = f"Best score change in last 4hr: {delta:+.4f}"

            sendText("Sweep Heartbeat", f"Best score: {best_score:.4f} at {now}\n{delta_msg}", plot_path)
            last_heartbeat = time.time()

        trial_idx += 1
        return final_score

    try:
        print("Starting hyperparameter sweep with resume support...")
        storage_path = "sqlite:///results/optuna_study.db"
        study_name = "catboost_sweep"

        study = optuna.create_study(
            direction="maximize",
            study_name=study_name,
            storage=storage_path,
            load_if_exists=True
        )

        study.optimize(objective, n_trials=99999)

    except KeyboardInterrupt:
        now = datetime.datetime.now().strftime("%y%m%d_%H:%M:%S")
        sendText("Sweep Interrupted", f"Stopped manually. Best score: {best_score:.4f} at {now}")

    except Exception as e:
        tb = traceback.format_exc()
        sendText("Sweep Crashed", tb[-500:])
        raise

    else:
        now = datetime.datetime.now().strftime("%y%m%d_%H:%M:%S")
        sendText("Sweep Finished", f"Completed successfully at {now}. Best score: {best_score:.4f}")


if __name__ == "__main__":
    run_sweep()
