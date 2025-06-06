import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Load dataset (simulated file2-1.csv)
df = pd.read_csv('/mnt/data/file2-1.csv')

# Simulate 'open_port_count' since it's missing in file2-1
np.random.seed(0)
df['open_port_count'] = np.random.randint(20, 41, size=len(df))

# Label high diversity hosts using 80th percentile
threshold = np.percentile(df['service_to_port_ratio'], 80)
df['high_diversity'] = (df['service_to_port_ratio'] > threshold).astype(int)

# Stratified split: Train / Val / Test
train, temp = train_test_split(df, test_size=0.30, stratify=df['high_diversity'], random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp['high_diversity'], random_state=42)

# Count classes in each split
datasets = ['Train', 'Validation', 'Test']
counts = [len(train), len(val), len(test)]
pos_counts = [train['high_diversity'].sum(), val['high_diversity'].sum(), test['high_diversity'].sum()]
neg_counts = [c - p for c, p in zip(counts, pos_counts)]

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(datasets))
width = 0.35

ax.bar(x, neg_counts, width, label='Low Diversity Hosts')
ax.bar(x, pos_counts, width, bottom=neg_counts, label='High Diversity Hosts')

ax.set_ylabel('Number of Hosts')
ax.set_xlabel('Dataset Split')
ax.set_title('Train / Validation / Test Split Sizes with Class Distribution')
ax.set_xticks(x)
ax.set_xticklabels(datasets)
ax.legend()

plt.tight_layout()
plt.show()
