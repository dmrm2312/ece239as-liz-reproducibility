import matplotlib.pyplot as plt

# Load the previously created dataset
df = pd.read_csv("/mnt/data/file3-1.csv")

# Plot: Count of Service-Port Pairs by ASN Type
plt.figure(figsize=(10, 6))
df['service_port_pair'] = df['service'] + '-' + df['port'].astype(str)
grouped = df.groupby(['asn_type', 'service_port_pair']).size().unstack(fill_value=0)

grouped.T.plot(kind='bar', stacked=True, figsize=(12, 6))
plt.title('Distribution of Service-Port Pairs by ASN Type')
plt.xlabel('Service-Port Pair')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(axis='y', alpha=0.3)
plt.show()
