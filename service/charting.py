import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


def plot_mfi_price_for_divergence(x, mfi, closing_price, title, xlabel, plot_file_path, mfi_sma_period=13, sma_low=8, sma_high=13):
    """
    Plots MFI and closing price on a chart and saves the plot to a file.

    :param x: The x-axis data.
    :param mfi: The MFI data.
    :param closing_price: The closing price data.
    :param title: The chart title.
    :param xlabel: The x-axis label.
    :param plot_file_path: The path where the plot image will be saved.
    :param mfi_sma_period: The period for the MFI SMA (default is 13).
    :param sma_low: The period for the lower Price SMA (default is 8).
    :param sma_high: The period for the higher Price SMA (default is 13).
    :return: True if most recently there is a divergence between MFI and closing price, False otherwise.
    """

    alpha = 0.5

    # Calculate SMA for MFI
    mfi_sma = np.convolve(mfi, np.ones(mfi_sma_period)/mfi_sma_period, mode='valid')

    # Calculate SMA_Low for Price
    price_sma_low = np.convolve(closing_price, np.ones(sma_low)/sma_low, mode='valid')

    # Calculate SMA_High for Price
    price_sma_high = np.convolve(closing_price, np.ones(sma_high)/sma_high, mode='valid')

    fig, ax1 = plt.subplots(figsize=(14, 8))  # Increase the figure height

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel("MFI", color="blue")
    ax1.plot(x[mfi_sma_period-1:], mfi_sma, label=f"MFI SMA_{mfi_sma_period}", color="blue", zorder=1)  # Plot MFI SMA
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
    ax2.plot(x[sma_low-1:], price_sma_low, label=f"Price SMA_{sma_low}", color="red", zorder=2)  # Plot Price SMA_Low
    ax2.plot(x[sma_high-1:], price_sma_high, label=f"Price SMA_{sma_high}", color="orange", zorder=2)  # Plot Price SMA_High
    ax2.tick_params(axis='y', labelcolor="red")

    # Set the y-axis limits for ax2 based on the minimum and maximum values of closing_price
    price_min, price_max = min(closing_price), max(closing_price)
    ax2.set_ylim(price_min - 0.1 * (price_max - price_min), price_max + 0.1 * (price_max - price_min))

    # Align mfi_sma and price_sma_low arrays
    aligned_length = min(len(mfi_sma), len(price_sma_low))
    mfi_sma_aligned = mfi_sma[-aligned_length:]
    price_sma_low_aligned = price_sma_low[-aligned_length:]

    # Calculate differences between consecutive MFI SMA and closing_price SMA_Low values
    mfi_sma_diff = np.diff(mfi_sma_aligned)
    price_sma_low_diff = np.diff(price_sma_low_aligned)

    # Extend the differences by one element to align with x values
    mfi_sma_diff = np.insert(mfi_sma_diff, 0, 0)
    price_sma_low_diff = np.insert(price_sma_low_diff, 0, 0)

    # Calculate the average price
    avg_price = np.mean(closing_price[-aligned_length:])

    # Find indices where MFI SMA is increasing, closing_price SMA_Low is decreasing, and price is below average
    bullish_diverging = (mfi_sma_diff > 0) & (price_sma_low_diff < 0) & (price_sma_low_aligned < avg_price)
    # Find indices where MFI SMA is decreasing, closing_price SMA_Low is increasing, and price is above average
    bearish_diverging = (mfi_sma_diff < 0) & (price_sma_low_diff > 0) & (price_sma_low_aligned > avg_price)
    diverging = bullish_diverging | bearish_diverging

    # Highlight divergence
    plt.fill_between(x[-aligned_length:], mfi_sma_aligned, price_sma_low_aligned, where=bullish_diverging, color="green", alpha=alpha, interpolate=True,
                     zorder=3)
    plt.fill_between(x[-aligned_length:], mfi_sma_aligned, price_sma_low_aligned, where=bearish_diverging, color="red", alpha=alpha, interpolate=True,
                     zorder=3)

    # Align price_sma_low and price_sma_high arrays
    aligned_length = min(len(price_sma_low), len(price_sma_high))
    price_sma_low_aligned = price_sma_low[-aligned_length:]
    price_sma_high_aligned = price_sma_high[-aligned_length:]

    # Find the indices where SMA_Low crosses above or below SMA_High
    sma_low_crosses_above = (price_sma_low_aligned[:-1] <= price_sma_high_aligned[:-1]) & (price_sma_low_aligned[1:] > price_sma_high_aligned[1:])
    sma_low_crosses_below = (price_sma_low_aligned[:-1] >= price_sma_high_aligned[:-1]) & (price_sma_low_aligned[1:] < price_sma_high_aligned[1:])

    # Add "B" and "S" labels at the crossing points
    buy_signal = False
    sell_signal = False
    for idx in np.where(sma_low_crosses_above)[0]:
        ax2.annotate("B", (x[sma_high-1+idx], price_sma_low_aligned[idx]), fontsize=12, color="green", fontweight="bold")
        if idx == len(price_sma_low_aligned) - 2:  # Check if it's the latest moment
            buy_signal = True
    for idx in np.where(sma_low_crosses_below)[0]:
        ax2.annotate("S", (x[sma_high-1+idx], price_sma_low_aligned[idx]), fontsize=12, color="red", fontweight="bold")
        if idx == len(price_sma_low_aligned) - 2:  # Check if it's the latest moment
            sell_signal = True

    # Create legends
    legend_patches = [
        plt.Line2D([0], [0], color="blue", lw=2, label=f"MFI SMA_{mfi_sma_period}"),
        plt.Line2D([0], [0], color="red", lw=2, label=f"Price SMA_{sma_low}"),
        plt.Line2D([0], [0], color="orange", lw=2, label=f"Price SMA_{sma_high}"),
        Patch(facecolor="green", edgecolor='black', label='Bullish Divergence'),
        Patch(facecolor="red", edgecolor='black', label='Bearish Divergence')
    ]
    plt.legend(handles=legend_patches, loc='lower right', bbox_to_anchor=(1.15, -0.3),
               borderaxespad=0)  # Adjust bbox_to_anchor

    fig.suptitle(title, fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the rectangle in which to fit the subplots
    plt.subplots_adjust(right=0.85)  # Adjust the right margin to make space for the legend
    plt.show()

    # Save the plot to a file
    fig.savefig(plot_file_path, bbox_inches='tight')

    # Create a dictionary to store the boolean values
    result = {
        "bullish_divergence": bullish_diverging[-1],
        "bearish_divergence": bearish_diverging[-1],
        "buy_signal": buy_signal,
        "sell_signal": sell_signal
    }

    return result

def detect_bullish_divergence_with_mfi(x, mfi, closing_price, title, xlabel, plot_file_path):
    """
    Plots MFI and closing price on a chart and saves the plot to a file.
    Detects bullish divergence based on MFI and closing price conditions.

    :param x: The x-axis data.
    :param mfi: The MFI data.
    :param closing_price: The closing price data.
    :param title: The chart title.
    :param xlabel: The x-axis label.
    :param plot_file_path: The path where the plot image will be saved.
    :return: True if there is a bullish divergence based on the specified conditions, False otherwise.
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
    # plt.show()

    # Save the plot to a file
    fig.savefig(plot_file_path, bbox_inches='tight')

    # Check if the last MFI data point is above 50 and the last closing price is below the average
    if not mfi.empty and not closing_price.empty:
        last_mfi = mfi.iloc[-1]
        last_closing_price = closing_price.iloc[-1]
        average_closing_price = closing_price.mean()
        return diverging[-1] and last_mfi > 50 and last_closing_price < average_closing_price
    else:
        return False
