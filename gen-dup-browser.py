#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
from typing import List, Tuple, Set, Iterable, Dict
import argparse
import json
import jinja2
import networkx
import shutil
import tqdm
import worddiff
import collections
import archetype_extraction

__script_dir__ = os.path.dirname(os.path.realpath(__file__))
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))

def get_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('-ij', '--input--json', required=True, type=str)
    p.add_argument('-od', '--output--dir', type=str, default='report')
    p.add_argument('-ie', '--input--enc', type=str, default='utf-8')
    return p.parse_args()


def html_diff(s1: str, s2: str) -> str:
    return worddiff.get_html(s1, s2)


def load_graph(json_file: str, input_encoding: str) -> networkx.DiGraph:
    with open(json_file, 'r', encoding=input_encoding) as jf:
        digraph = json.load(jf)['digraph']
        gr = networkx.DiGraph()

        limit = 500

        for vertex, i in zip(digraph, range(limit)):
            gr.add_node(i, name=vertex['vertexName'], comment=vertex['comment'], label=vertex['vertexLabel'])

        for source_vertex, source_id in zip(digraph, range(limit)):
            if 'children' in source_vertex:
                for chi in source_vertex['children']:
                    target_name = chi['name']
                    target_ids = [n for n, d in gr.nodes(data=True) if d['name'] == target_name]
                    if len(target_ids):
                        target_id = target_ids[0]
                        gr.add_edge(source_id, target_id)

        return gr


def render_graph_component(component: networkx.Graph, output_dir: str) -> None:
    component_texts = [component.nodes[nd]['comment'] for nd in component.nodes]
    archetype = ' '.join(archetype_extraction.possible_n_tuples_lcs(tuple(tuple(worddiff.words(sss)) for sss in component_texts)))

    rt = env.get_template("one_graph.html").render(
        nodes=[{
            'id': n, 'label': component.nodes[n]['label']
        } for n in component.nodes],

        edges=[{
            'u': u, 'v': v
        } for u, v in component.edges],

        codes=[{
            'id':n, 'header': component.nodes[n]['name'],
            'body': html_diff(archetype, component.nodes[n]['comment'])
        } for n in component.nodes],

        diffs=[{
            'id1': u, 'header1': component.nodes[u]['name'], 'body1': component.nodes[u]['comment'],
            'id2': v, 'header2': component.nodes[v]['name'], 'body2': component.nodes[v]['comment'],
            'diff': html_diff(component.nodes[u]['comment'], component.nodes[v]['comment'])
        } for u, v in component.edges]
    )

    with open(os.path.join(output_dir, "%04d.html" % min(component)), 'w', encoding='utf-8') as wh:
        print(rt, file=wh)


def render_component_catalogue(components: Iterable[networkx.Graph], output_dir) -> None:
    rt = env.get_template("component_catalogue.html").render(
        comps = [{
            'power': len(c), 'id': "%04d" % (min(n for n in c)),
            'head': c.node[min(n for n in c)]['label'],
            'sample': c.node[min(n for n in c)]['comment']
        } for c in components]
    )

    with open(os.path.join(output_dir, "catalogue.html"), 'w', encoding='utf-8') as wh:
        print(rt, file=wh)


def get_components(gr: networkx.DiGraph) -> List[networkx.Graph]:
    comps = [gr.subgraph(c) for c in networkx.connected_components(networkx.Graph(gr))]
    comps.sort(key=len, reverse=True)
    return comps


if __name__ == '__main__':
    args = get_args()

    graph = load_graph(args.input__json, args.input__enc)

    os.makedirs(args.output__dir, exist_ok=True)

    for filename in glob.glob(os.path.join(__script_dir__, 'resources', '*')):
        shutil.copy(filename, args.output__dir)
    components = get_components(graph)

    print(f"Largest component: {min(components[0])}")

    size_stats = collections.defaultdict(lambda: 0)
    for c in components:
        size_stats[len(c)] += 1
    print("Component size | count:")
    for s in size_stats:
        print(s, ':', size_stats[s])

    render_component_catalogue(components, args.output__dir)
    print("Rendering components...")
    for comp in tqdm.tqdm(components):
        render_graph_component(comp, args.output__dir)
