# Schedule.py Pulls forecast data from the BOM each day and saves it in an SQL db.
import pandas as pd  # Structure and Dataframes
# Charting
import seaborn as sns
from matplotlib import pyplot as plt

#################################
# Heatmap
################################

def load_data():
    tf = pd.read_csv('../static/data/forecast_dataframe.csv', index_col=0)  # Whole csv. Much faster than accessing db.
    fac = pd.read_csv('../static/data/accuracy_dataframe.csv', index_col=0)  # Whole csv. Much faster than accessing db.
    persistence = pd.read_csv('../static/data/persistence_dataframe.csv', index_col=0)
    return tf, fac, persistence, 

# Heatmap Function
def heat_map(data, title):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax = sns.heatmap(data, annot=True, center=True, cmap='coolwarm', cbar_kws={'label': 'Degrees Celsius'})
    ax.set_title(title, loc='center', fontsize=18)
    ax.set_xticklabels(ax.xaxis.get_ticklabels(), fontsize=14, rotation=-20, ha="left" )
    ax.set_yticklabels(ax.yaxis.get_ticklabels(), fontsize=14, rotation=0)
    ax.figure.axes[-1].yaxis.label.set_size(14)
    ax.figure.axes[0].yaxis.label.set_size(14)
    ax.figure.axes[0].xaxis.label.set_size(14)
    print('--> Heatmap Created')


def generate_heatmaps():
    tf, fac, persistence = load_data()
    plt.figure() # Push new figure on stack
    heat_map(tf, "7 Day Forecasts From BOM (Descending to the left)")
    plt.savefig('../static/charts/heatmap_forecast.png');
    
    plt.figure() # Push new figure on stack
    heat_map(fac, "Forecast Variation (0 = 100% Accurate)")
    plt.savefig('../static/charts/heatmap_accuracy.png');
    
    plt.figure() # Push new figure on stack
    heat_map(persistence, "Persistence (far left) vs Forecast")
    plt.savefig('../static/charts/heatmap_persistence.png');
    
    print('LOG: Heatmaps generated and stored without errors.', '\n')
