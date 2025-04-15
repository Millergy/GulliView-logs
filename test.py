import matplotlib.pyplot as plt
import numpy as np

# Example data
data = {
    "Category A": {"values": [1, 2, 3, 4, 5]},
    "Category B": {"values": [2, 3, 4, 5, 6]},
    "Category C": {"values": [3, 4, 5, 6, 7]},
}

# Prepare data for boxplot
categories = list(data.keys())
values = [data[cat]["values"] for cat in categories]

# Aggregate data (calculate percentiles)
aggregated_values = [np.percentile(cat_values, [0, 25, 50, 75, 100]) for cat_values in values]

print(aggregated_values)

# Extract aggregated statistics
mins = [agg[0] for agg in aggregated_values]
q1s = [agg[1] for agg in aggregated_values]
medians = [agg[2] for agg in aggregated_values]
q3s = [agg[3] for agg in aggregated_values]
maxs = [agg[4] for agg in aggregated_values]

print(mins)

agg_data = zip(mins, q1s, medians, q3s, maxs)

# Create the boxplot using aggregated data
fig, ax = plt.subplots(figsize=(8, 6))
for i, (min_val, q1, median, q3, max_val) in enumerate(agg_data, start=1):
    # Draw the box
    ax.plot([i, i], [q1, q3], color="blue", linewidth=10, alpha=0.5)  # Box
    # Draw the median
    ax.plot([i - 0.2, i + 0.2], [median, median], color="red", linewidth=2)  # Median
    # Draw the whiskers
    ax.plot([i, i], [min_val, q1], color="black", linestyle="--")  # Lower whisker
    ax.plot([i, i], [q3, max_val], color="black", linestyle="--")  # Upper whisker

# Customize the plot
ax.set_xticks(range(1, len(categories) + 1))
ax.set_xticklabels(categories)
ax.set_title("Aggregated Boxplot")
ax.set_ylabel("Values")
ax.grid(True)

# Show the plot
plt.tight_layout()
plt.show()