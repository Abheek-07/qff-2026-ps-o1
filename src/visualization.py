"""Figures for corrected A/B comparison."""
from pathlib import Path
import matplotlib.pyplot as plt

def bar_comparison(df, column, path):
    fig,ax=plt.subplots(figsize=(6,4))
    ax.bar(df['processor'],df[column])
    ax.set_ylabel(column.replace('_',' ').title())
    ax.set_xlabel('Processor')
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=180)
    plt.close(fig)
