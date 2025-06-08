import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure
fig = plt.figure(figsize=(8, 14))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')

# Define helper to add rectangle with text
def add_rect(x, y, w, h, label, color):
    rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor=color,
                             facecolor='none')
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=10)

# Header
add_rect(0, 13, 10, 1, 'Header (Logo • Date Picker • Search • Theme)', 'navy')

# Today's games
add_rect(0, 9.5, 6, 3, "Today's Games & Predictions", 'green')

# Standings
add_rect(6.2, 9.5, 3.8, 3, 'Standings (Division grid)', 'purple')

# Recent Games & Accuracy
add_rect(0, 8, 10, 1, 'Recent Games & Model Accuracy', 'orange')

# Team Cards Grid
add_rect(0, 4.5, 10, 3, 'Team Pages Grid (30 team cards)', 'teal')

# Model Info
add_rect(0, 3.5, 10, 1, 'Model Explanation & Metrics', 'brown')

# Footer
add_rect(0, 2.8, 10, 0.7, 'Footer (Disclaimer • GitHub • Credits)', 'gray')

# Mobile note
ax.text(0, 1.5, 'Sections collapse to vertical stack / horizontal carousels on mobile.',
        fontsize=8, va='center')

# Show plot
plt.show()
