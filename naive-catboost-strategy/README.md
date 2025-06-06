# Naive CatBoost Strategy for Multi-Class Port Classification

This project explores a naive classification strategy using CatBoost to predict services running on IPv4 hosts across 65,535 ports. It uses tabular WHOIS metadata and regional information without network topology, packet-level data, or advanced embeddings.

## Environment
- **Tested on**: Ubuntu system with NVIDIA RTX Titan (24GB VRAM)
- **VRAM usage**: Training on full datasets may exceed VRAM limits on smaller GPUs.

## Directory Structure

```bash
├── encodings/                  # Mapping JSONs + rare label lists (e.g. OTHER.txt)
├── final_models/               # Trained CatBoost models + evaluation metrics
├── processed/                  # Full and split datasets (parquet format)
├── production/                 # Scripts for training, sweeping, evaluation
├── results/                    # Sweep logs, heartbeat plots, Optuna study
├── config.yaml                 # Global config (paths + columns)
├── sample.env                  # Example environment variables
├── requirements.txt            # Python enviroment requirements
├── README.md                   
```

## Dataset Splits (in `./processed/`)
| File                         | Description                       |
|------------------------------|-----------------------------------|
| `train_superhost.parquet`    | Training set                      |
| `val_superhost.parquet`      | Validation set                    |
| `test_superhost.parquet`     | Test set                          |

Download files at: https://ucla.box.com/s/tjsgjn61s8xcpih6tj4xn9rwopjp4zgg 

This folder will be hosted till 6/15/25

## How to Use

### 1. Configure
Update `config.yaml` with:
- Paths to parquet datasets
- Columns for input features and labels

### 2. Run Sweep
```bash
python production/sweep_parameter.py
```
- Optuna will search for top configurations
- To restart cleanly, **delete all files inside `results/`**

### 3. Train Top K Configs
```bash
python production/train_top_k_configs.py
```
- Uses top `K` configs from `results/sweep_log.csv`
- Saves loss plots, final model, and performance metrics to `final_models/`

## Metrics
Includes:
- Overall accuracy and F1
- Precision/Recall/F1 @ 1, 5, and 30
- Early stopping via CatBoost's native overfitting detection

## To Reset Sweep
To begin a new hyperparameter search:
```bash
rm -rf results/*
```
This clears logs, Optuna state, and generated plots.

---

For long-running sweeps or distributed setup (e.g., multi-GPU swarm mode), additional PostgreSQL + Docker setup is recommended.