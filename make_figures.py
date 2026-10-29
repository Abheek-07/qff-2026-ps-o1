"""Generate truthful graphs from locked data and (if available) measured results."""
import json,csv
from pathlib import Path
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
out=R/'results'/'figures';out.mkdir(parents=True,exist_ok=True)
d=json.loads((R/'data/instances.json').read_text())['PS-O1'];edges=d['weighted_edges']
G=nx.Graph();G.add_nodes_from(range(6));G.add_weighted_edges_from(edges)
optimal='001011'
assert sum(w for i,j,w in edges if optimal[i]!=optimal[j])==22
pos=nx.spring_layout(G,seed=42)
fig,ax=plt.subplots(figsize=(7,5));nx.draw_networkx_nodes(G,pos,ax=ax,node_size=1100,node_color=['#2563eb' if optimal[i]=='0' else '#0d9488' for i in G.nodes()]);nx.draw_networkx_labels(G,pos,ax=ax,font_color='white',font_weight='bold');nx.draw_networkx_edges(G,pos,ax=ax,width=[2.8 if optimal[i]!=optimal[j] else 0.8 for i,j in G.edges()],edge_color=['#f59e0b' if optimal[i]!=optimal[j] else '#9ca3af' for i,j in G.edges()]);nx.draw_networkx_edge_labels(G,pos,edge_labels=nx.get_edge_attributes(G,'weight'),ax=ax);ax.set_title('Official PS-O1 graph — optimal cut = 22 (gold edges)');ax.axis('off');fig.tight_layout();fig.savefig(out/'official_maxcut.png',dpi=170);plt.close(fig)
p=json.loads((R/'processors/processor_D.json').read_text()); D=nx.Graph();D.add_nodes_from(range(p['num_qubits']));D.add_edges_from(p['edges']); pos=nx.spring_layout(D,seed=42)
fig,ax=plt.subplots(figsize=(6,4.5));nx.draw(D,pos,ax=ax,with_labels=True,node_color='#2563eb',font_color='white',font_weight='bold',node_size=900,width=2.3);ax.set_title('HACKSMITHS Processor D: 6 qubits / 8 couplings');fig.tight_layout();fig.savefig(out/'processor_D_topology.png',dpi=170);plt.close(fig)
res=R/'results'/'tables'/'results.csv'
if res.exists():
 with res.open(newline='') as f: rows=list(csv.DictReader(f))
 usable=[x for x in rows if x['processor'] in ('B','D') and x['executable'].lower()=='true']
 if len(usable)==4:
  labels=[x['processor']+' '+x['condition'] for x in usable];scores=[float(x['quality_value']) for x in usable]
  fig,ax=plt.subplots(figsize=(7,4));ax.bar(labels,scores);ax.set_ylim(0,1);ax.set_ylabel('Mean cut / classical optimum');ax.set_title('Measured QAOA approximation ratios (4096 shots)');fig.tight_layout();fig.savefig(out/'processor_approx_ratio.png',dpi=170);plt.close(fig)
print('Generated available evidence-based figures in',out)
