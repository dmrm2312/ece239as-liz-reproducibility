# ECE239AS-Liz-Reproducibility

This repository contains all code, scripts, notebooks, and datasets necessary to reproduce results for the final project in **ECE 239AS: Internet Measurement and Security** at UCLA.

---

## Project Overview

The goal of the project is to explore service classification and behavior of "superhosts"—IPv4 addresses that expose many open ports. This repository contains two subprojects:

1. **Bucket Model** (supervised analysis and clustering)
2. **Naive CatBoost Strategy** (multi-class supervised classification)

In addition, the `figures/` directory includes code and images used in static dataset analysis.

---

## Repository Structure

```bash
├── bucket-model/               # Unsupervised clustering + learning algorithm
│   ├── *.png                   # Intermediate visualizations
│   ├── *.ipynb                 # Jupyter notebooks (preprocessing, training)
│   └── readme.md               # Instructions for running bucket model
│
├── figures/                    # SQL and image-based figures analyzing dataset
│   ├── figureX/*.sql           # Queries
│   ├── figureX/*.png           # Associated plots
│
├── naive-catboost-strategy/   # Supervised CatBoost classifier + dataset generation
│   ├── encodings/              # Encoded label maps and OTHER lists
│   ├── final_models/           # Trained CatBoost models + metrics
│   ├── processed/              # Parquet-format datasets
│   ├── production/             # Sweep and training scripts
│   ├── results/                # Heartbeat plots, sweep logs, optuna study
│   ├── config.yaml             # Global path + column config
│   ├── README.md               # How to run this subproject
│
├── LICENSE
├── sample.env
├── requirements.txt
└── README.md                   # (This file)
```

---

## 🔧 Getting Started

Install all dependencies:

```bash
pip install -r requirements.txt
```

> ⚠️ All CatBoost experiments were tested on an **RTX Titan (24GB VRAM)**. Lower-memory GPUs may crash on large splits.

---

## 🧪 Reproducing Results

### 1. Run the Bucket Model

```bash
cd bucket-model
```

Follow the instructions in [`bucket-model/readme.md`](./bucket-model/readme.md) to reproduce figures using unsupervised methods.

### 2. Run the Naive CatBoost Classifier

```bash
cd naive-catboost-strategy
```

Follow the instructions in [`naive-catboost-strategy/README.md`](./naive-catboost-strategy/README.md) to preprocess datasets, run Optuna sweeps, and evaluate top-k models.

### 3. Explore Dataset Visualizations

The [`figures/`](./figures/) folder contains both:

* SQL queries for figure generation
* PNG exports of those figures

These include port distributions, honeypot service counts, and visualization of metadata frequency.

---

## Regenerating from Scratch

* To regenerate the bucket model: run both `preprocessing.ipynb` and `training.ipynb` inside the `bucket-model/` directory
* To rerun a sweep: `rm -rf naive-catboost-strategy/results/*`
* To regenerate encoded datasets: run scripts in `naive-catboost-strategy/production/`

---

## Acknowledgments


All team members contributed reproducible pipelines, encoding standards, and labeled metadata exploration for a better understanding of superhosts in internet-scale scan datasets.

This project was completed as part of UCLA's **ECE 239AS: Internet Measurement and Security**.
