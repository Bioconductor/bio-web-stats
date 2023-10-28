from flask import Flask, render_template
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
from datetime import date
import io
import base64

def webstats_plot():
    
    use('agg')
    # Sample data
    reference_year = 2023
    package = 'affy'
    months = [date(reference_year, m + 1, 1).strftime('%b') for m in range(12)]
    distinct_IPs = np.random.randint(4000, 8000, 12)  # Replace with your data
    downloads = np.random.randint(6000, 10000, 12)  # Replace with your data

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    # Use log scale for the y-axis
    ax.set_yscale('log')

    # Bar plot for distinct IPs
    bar_width = 0.35
    index = np.arange(len(months))
    ax.bar(index, distinct_IPs, bar_width, label='Nb of distinct IPs', color='blue', alpha=0.7)

    # Bar plot for downloads
    ax.bar(index + bar_width, downloads, bar_width, label='Nb of downloads', color='blue')

    # Labeling and formatting
    ax.set_xlabel('Month')
    ax.set_ylabel('Counts (log scale)')
    ax.set_title('affy 2023')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(months)
    ax.legend()
    ax.grid(axis='y', which='both', linestyle='--', linewidth=0.5)
    ax.set_facecolor('white')

    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    
    # Convert the BytesIO object to a base64 string
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()  # Close the matplotlib plot to free memory
    
    # Pass the base64 string to the Jinja template
    # return render_template('plot_template.html', plot_img="data:image/png;base64," + img_base64)
    return img_base64

