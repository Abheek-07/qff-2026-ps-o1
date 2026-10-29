#!/usr/bin/env python3
"""Standalone supplementary SYNTHETIC demonstration; NEVER the official PS-O1 instance.
Requires Python >=3.10, matplotlib and networkx. No Qiskit required.
"""
from pathlib import Path
import csv, itertools, json, random, statistics, time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
ROOT=Path(__file__).resolve().parent

def load():
    with (ROOT/'synthetic_sectors.csv').open(newline='') as f: sectors=list(csv.DictReader(f))
    with (ROOT/'synthetic_conflicts.csv').open(newline='') as f: edges=list(csv.DictReader(f))
    assert len(sectors)==6 and len({r['sector_id'] for r in sectors})==6
    assert all(r['synthetic_only']=='YES' for r in sectors+edges)
    assert all(int(e['weight'])==int(e['conflict_strength_1_to_5'])*(int(e['source_priority'])+int(e['target_priority'])) for e in edges)
    return sectors,edges

def evaluate(bits,edges,index):
    cut=sum(int(e['weight']) for e in edges if bits[index[e['source']]]!=bits[index[e['target']]])
    same=sum(int(e['weight']) for e in edges if bits[index[e['source']]]==bits[index[e['target']]])
    return cut,same

def main():
    sectors,edges=load();index={r['sector_id']:i for i,r in enumerate(sectors)}
    total=sum(int(e['weight']) for e in edges)
    t0=time.perf_counter_ns()
    all_scores=[]
    for bits in itertools.product((0,1),repeat=len(sectors)):
        c,s=evaluate(bits,edges,index)
        assert c+s==total
        all_scores.append((c,bits,s))
    elapsed_ns=time.perf_counter_ns()-t0
    best=max(r[0] for r in all_scores)
    opt=[row for row in all_scores if row[0]==best]
    rng=random.Random(2026)
    # 1000 independently drawn uniform assignments (WITH replacement), seeded for reproducibility
    baseline=[evaluate(tuple(rng.randrange(2) for _ in sectors),edges,index)[0] for _ in range(1000)]
    baseline_mean=statistics.mean(baseline)
    exact_random_mean=statistics.mean(v[0] for v in all_scores)
    assert exact_random_mean==total/2
    chosen=min((bits for c,bits,s in opt))
    data=dict(dataset='SYNTHETIC SUPPLEMENTARY ONLY - NOT OFFICIAL PS-O1',num_sectors=len(sectors),num_edges=len(edges),assignments_evaluated=len(all_scores),total_weight=total,optimal_cut_weight=best,optimal_same_channel_conflict=total-best,optimal_assignments_count=len(opt),optimal_assignments=[''.join(map(str,bits)) for c,bits,s in opt],chosen_assignment=''.join(map(str,chosen)),runtime_exhaustive_search_ns=elapsed_ns,runtime_exhaustive_search_ms=elapsed_ns/1e6,random_baseline_seed=2026,random_baseline_draws=1000,random_baseline_sample_mean_cut=baseline_mean,random_baseline_sample_std_cut=statistics.stdev(baseline),uniform_random_exact_mean_cut=exact_random_mean,improvement_vs_sample_random_cut=best-baseline_mean,optimality_fraction=best/total)
    (ROOT/'results.json').write_text(json.dumps(data,indent=2)+'\n')
    with (ROOT/'results_table.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['method','cut_weight','same_channel_conflict','evaluation_note'])
        w.writerow(['exhaustive_optimum',best,total-best,'64 exact assignments; measured runtime in results.json'])
        w.writerow(['uniform_random_exact_expectation',exact_random_mean,total-exact_random_mean,'expectation over all 64 assignments'])
        w.writerow(['random_sample_1000_seed_2026',round(baseline_mean,3),round(total-baseline_mean,3),'sample mean; random with replacement'])
    G=nx.Graph();
    for r in sectors:G.add_node(r['sector_id'],pos=(float(r['schematic_x_km']),float(r['schematic_y_km'])))
    for e in edges:G.add_edge(e['source'],e['target'],weight=int(e['weight']))
    pos=nx.get_node_attributes(G,'pos')
    fig,axs=plt.subplots(1,2,figsize=(13.5,5.7),gridspec_kw={'width_ratios':[1.6,1]})
    ax=axs[0]; colors=['#1964ad' if chosen[index[n]]==0 else '#ed8a26' for n in G.nodes()]
    nx.draw_networkx_nodes(G,pos,ax=ax,node_color=colors,node_size=1000,edgecolors='#162333',linewidths=1.5)
    nx.draw_networkx_labels(G,pos,ax=ax,font_weight='bold',font_color='white')
    cross=[(u,v) for u,v in G.edges() if chosen[index[u]]!=chosen[index[v]]]
    same=[(u,v) for u,v in G.edges() if chosen[index[u]]==chosen[index[v]]]
    nx.draw_networkx_edges(G,pos,edgelist=cross,ax=ax,width=2.2,edge_color='#2a9d65')
    nx.draw_networkx_edges(G,pos,edgelist=same,ax=ax,width=1.6,edge_color='#b23c51',style='dashed')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=nx.get_edge_attributes(G,'weight'),ax=ax,font_size=9,bbox={'facecolor':'white','edgecolor':'none','alpha':0.85,'pad':0.08})
    ax.set_title('SYNTHETIC: six sectors and weighted conflicts\nBlue = A | Orange = B | Green = separated | Red dashed = shared',fontsize=11)
    ax.set_xlabel('schematic x (km) - NOT surveyed coordinates');ax.set_ylabel('schematic y (km)')
    ax.axis('on');ax.set_aspect('equal');ax.grid(alpha=.12)
    axs[1].bar(['Uniform random\n(expected)','Uniform random\n(sampled)','Exhaustive\noptimum'],[exact_random_mean,baseline_mean,best],color=['#8a98a8','#aebac8','#278f71'])
    axs[1].set_ylabel('Weighted cut value (synthetic units)');axs[1].set_ylim(0,total*1.08)
    axs[1].set_title('Comparison against random assignment')
    for i,val in enumerate([exact_random_mean,baseline_mean,best]):axs[1].text(i,val+1,f'{val:.2f}',ha='center',fontsize=11)
    fig.suptitle('Supplementary model only — NOT official QFF PS-O1 benchmark',fontweight='bold')
    fig.tight_layout();fig.savefig(ROOT/'network_diagram.png',dpi=200,bbox_inches='tight');fig.savefig(ROOT/'network_diagram.pdf',bbox_inches='tight');plt.close(fig)
    print(json.dumps(data,indent=2))
if __name__=='__main__': main()
