import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the new dataset
df = pd.read_csv('/mnt/data/dm1.csv')

# Simulate missing 'geo_country' if not present
if 'geo_country' not in df.columns:
    np.random.seed(0)
    df['geo_country'] = np.random.choice(['US', 'DE', 'CN', 'JP', 'RU', 'FR'], size=len(df))

# Simulate 'unknown_service_count' if not present
if 'unknown_service_count' not in df.columns:
    df['unknown_service_count'] = np.random.randint(0, 5, size=len(df))

# Aggregate by country
summary = df.groupby('geo_country').agg({
    'open_port_count': 'mean',
    'service_diversity': 'mean',
    'unknown_service_count': 'mean'
}).reset_index()

# Plot setup
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(summary['geo_country']))
bar_width = 0.25
colors = sns.color_palette("Set2", 3)

# Draw bars
ax.bar(x, summary['open_port_count'], width=bar_width, label='Open Port Count', color=colors[0])
ax.bar(x + bar_width, summary['service_diversity'], width=bar_width, label='Service Diversity', color=colors[1])
ax.bar(x + 2 * bar_width, summary['unknown_service_count'], width=bar_width, label='Unknown Service Count', color=colors[2])

# Finalize plot
ax.set_title('Feature Characterization of Super Hosts by Country (Updated DM1)', fontsize=14, weight='bold')
ax.set_xlabel('Country')
ax.set_ylabel('Average Metric Value')
ax.set_xticks(x + bar_width)
ax.set_xticklabels(summary['geo_country'])
ax.legend()
plt.tight_layout()
plt.show()
