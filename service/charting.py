import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


def plot_mfi_price_for_divergence(x, mfi, closing_price, title, xlabel, plot_file_path):
    """
    Plots MFI and closing price on a chart and saves the plot to a file.

    :param x: The x-axis data.
    :param mfi: The MFI data.
    :param closing_price: The closing price data.
    :param title: The chart title.
    :param xlabel: The x-axis label.
    :param plot_file_path: The path where the plot image will be saved.
    :return: True if most recently there is a divergence between MFI and closing price, False otherwise.
    """

    divergence_color = '#FFD700'
    alpha = 0.5

    fig, ax1 = plt.subplots(figsize=(14, 8))  # Increase the figure height

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel("MFI", color="blue")
    ax1.plot(x, mfi, label="MFI", color="blue", zorder=1)
    ax1.tick_params(axis='y', labelcolor="blue")
    ax1.set_ylim(0, 100)  # Set fixed label from 0 to 100 for MFI
    ax1.axhline(50, color='black', linewidth=2)  # Add a bold line at 50 for highlight

    # Add light pink background for MFI ranges 80-100 and 0-20
    ax1.axhspan(80, 100, facecolor='lightpink', alpha=0.5)
    ax1.axhspan(0, 20, facecolor='lightpink', alpha=0.5)

    # Add grid lines using the MFI axis
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Closing Price", color="red")
    ax2.plot(x, closing_price, label="Closing Price", color="red", zorder=2)
    ax2.tick_params(axis='y', labelcolor="red")

    # Set the y-axis limits for ax2 based on the minimum and maximum values of closing_price
    price_min, price_max = min(closing_price), max(closing_price)
    ax2.set_ylim(price_min - 0.1 * (price_max - price_min), price_max + 0.1 * (price_max - price_min))

    # Calculate differences between consecutive MFI and closing_price values
    mfi_diff = np.diff(mfi)
    price_diff = np.diff(closing_price)

    # Extend the differences by one element to align with x values
    mfi_diff = np.insert(mfi_diff, 0, 0)
    price_diff = np.insert(price_diff, 0, 0)

    # Find indices where MFI is increasing and closing_price is decreasing, and vice versa
    diverging_up = (mfi_diff > 0) & (price_diff < 0)
    diverging_down = (mfi_diff < 0) & (price_diff > 0)
    diverging = diverging_up | diverging_down

    # Highlight divergence
    plt.fill_between(x, mfi, closing_price, where=diverging, facecolor=divergence_color, alpha=alpha, interpolate=True,
                     zorder=3)

    # Create legends
    legend_patches = [
        plt.Line2D([0], [0], color="blue", lw=2, label="MFI"),
        plt.Line2D([0], [0], color="red", lw=2, label="Closing Price"),
        Patch(facecolor=divergence_color, edgecolor='black', label='Divergence')
    ]
    plt.legend(handles=legend_patches, loc='lower right', bbox_to_anchor=(1.15, -0.2),
               borderaxespad=0)  # Adjust bbox_to_anchor

    fig.suptitle(title, fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the rectangle in which to fit the subplots
    plt.subplots_adjust(right=0.85)  # Adjust the right margin to make space for the legend
    plt.show()

    # Save the plot to a file
    fig.savefig(plot_file_path, bbox_inches='tight')

    return diverging[-1]
