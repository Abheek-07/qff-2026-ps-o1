"""All visualizations created from generated results; never hard-coded benchmarks."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

def save(fig,name):
    path=Path(__file__).resolve().parents[1]/'results'/'figures'/name
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=170,bbox_inches='tight')
    plt.close(fig)
    return path

def plot_weighted_graph(g):
    fig,ax=plt.subplots(figsize=(7,4.8))
    pos=nx.spring_layout(g,seed=42)
    nx.draw_networkx(g,pos=pos,ax=ax,node_color='#b4d9f0',edge_color='#718096',node_size=850,font_weight='bold',width=1.7)
    nx.draw_networkx_edge_labels(g,pos=pos,ax=ax,edge_labels=nx.get_edge_attributes(g,'weight'),font_color='#b91c1c')
    ax.set_title('PS-O1: original SIX-vertex weighted Max-Cut instance');ax.axis('off')
    return save(fig,'weighted_graph.png')

def plot_topologies(configs):
    fig,axs=plt.subplots(1,2,figsize=(11,4.7))
    for ax,(name,cfg) in zip(axs,configs.items()):
        g=nx.Graph();g.add_nodes_from(range(cfg['num_qubits']));g.add_edges_from(cfg['coupling_map'])
        pos=nx.spring_layout(g,seed=42)
        nx.draw_networkx(g,pos,ax=ax,node_color='#a3d4f7' if name=='A' else '#a4e4c1',node_size=700,
                         font_weight='bold',font_size=10,width=2,edge_color='#4b5563')
        ax.set_title(f'Processor {name} · {cfg["num_qubits"]} physical qubits · {len(cfg["coupling_map"])} couplings')
        ax.axis('off')
    fig.suptitle('Participant-defined connectivity graphs (undirected couplings)',y=1.04)
    return save(fig,'processor_topologies.png')

def plot_metrics(df):
    fig,axs=plt.subplots(1,3,figsize=(12,3.6))
    for ax,key,unit in zip(axs,['depth','cx_count','swap_diagnostic_count'],['Circuit depth','Native CX gates','Routing diagnostic SWAPs']):
        ax.bar(df['processor'],df[key],color=['#457b9d','#52b788'])
        ax.set_title(unit)
        ax.set_ylim(bottom=0)
        for j,v in enumerate(df[key]):ax.text(j,v,f'{v:.0f}',ha='center',va='bottom')
    fig.suptitle('Compiled resources (level 1, seed 42, fixed starting layout)')
    return save(fig,'architecture_resources.png')

def plot_noise(df):
    fig,ax=plt.subplots(figsize=(6.6,4.2))
    ax.bar(df['processor'],df['mean_cut'],color=['#457b9d','#52b788'],yerr=df['standard_error'],capsize=5)
    ax.set_ylabel('Weighted cut, 4096 shots per trial')
    ax.set_title('Noisy benchmark: mean across simulator seeds')
    ax.set_ylim(0,max(df['mean_cut'])*1.15)
    return save(fig,'noisy_cut.png')

def plot_sensitivity(df):
    fig,ax=plt.subplots(figsize=(6.6,4.2))
    for processor,part in df.groupby('processor'):
        ax.plot(part['cx_error'],part['mean_cut'],marker='o',label=f'Processor {processor}')
    ax.set_xlabel('Two-qubit depolarizing probability')
    ax.set_ylabel('Average weighted cut')
    ax.set_title('Sensitivity: fixed 1q/readout noise; CX noise varied')
    ax.legend()
    return save(fig,'noise_sensitivity.png')
