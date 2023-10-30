from flask import Flask, render_template
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
from datetime import date
import io
import base64

def webstats_plot(data_table: [tuple], plot_title: str):
    """Genreate plot from one years data.

    Arguments:
        data_table -- A list of tuples, all for the same year in the form
        (year, month, ip_count, download_count)

    Returns:
        _description_
    """

    # exclude the annual total from the graph.
    months, distinct_ips, downloads = map(list, zip(*[t[1:4] for t in data_table if t[1] != 'all']))
    use('agg')
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    # Use log scale for the y-axis
    ax.set_yscale('log')

    light_blue = '#ddddff'
    dark_blue = '#aaaaff'

    # Bar plot for distinct IPs
    bar_width = 0.35
    index = np.arange(len(months))
    ax.bar(index, distinct_ips, bar_width, label='Nb of distinct IPs', color=dark_blue)

    # Bar plot for downloads
    ax.bar(index + bar_width, downloads, bar_width, label='Nb of downloads', color=light_blue)

    # TODO Have y-axis scientific notation, want explicit integers
    # Labeling and formatting
    ax.set_xlabel('Month')
    ax.set_ylabel('Counts (log scale)')
    ax.set_title(plot_title)
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

