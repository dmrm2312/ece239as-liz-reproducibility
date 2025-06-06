import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Dataset 2
df = pd.read_csv('dm2.csv')

# Label containerized vs non-containerized if not already present
if 'deployment_type' not in df.columns:
    df['deployment_type'] = (
        (df['service_diversity'] <= 2) & (df['open_port_count'] >= 120)
    ).map({True: 'Containerized', False: 'Non-Containerized'})

# Fallback for missing unknown_service_count
if 'unknown_service_count' not in df.columns:
    df['unknown_service_count'] = 0

# Aggregate
summary = df.groupby('deployment_type').agg({
    'open_port_count': 'mean',
    'service_diversity': 'mean',
    'unknown_service_count': 'mean'
}).reset_index()

# Plot
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(10, 6))
summary.set_index('deployment_type').plot(kind='bar', ax=ax, color=sns.color_palette("Set2", 3))

# Labeling
ax.set_title('Containerization Effects on Super Host Characteristics (Updated DM2)', fontsize=14, weight='bold')
ax.set_xlabel('Host Type')
ax.set_ylabel('Average Metric Value')
ax.legend(["Open Port Count", "Service Diversity", "Unknown Service Count"])
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
