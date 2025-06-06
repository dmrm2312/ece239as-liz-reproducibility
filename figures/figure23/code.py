import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the uploaded file
df = pd.read_csv("/mnt/data/file4-1.csv")

# Plotting: service_to_port_ratio vs open_port_count, colored by high_diversity
plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    df['open_port_count'],
    df['service_to_port_ratio'],
    c=df['high_diversity'],
    cmap='coolwarm',
    edgecolor='k',
    alpha=0.75
)

plt.xlabel('Open Port Count')
plt.ylabel('Service-to-Port Ratio')
plt.title('SuperHost Diversity Classification')
plt.grid(True)
plt.legend(*scatter.legend_elements(), title="High Diversity")
plt.tight_layout()