#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
from typing import List, Tuple, Set
import argparse
import json
import jinja2
import networkx
import io
import itertools
import shutil
import tqdm

__script_dir__ = os.path.dirname(os.path.realpath(__file__))

def get_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('-ij', '--input--json', required=True, type=str)
    p.add_argument('-od', '--output--dir', type=str, default='report')
    p.add_argument('-ie', '--input--enc', type=str, default='utf-8')
    return p.parse_args()


def html_diff(s1, s2):
    # TODO: implement
    return f"{s1} DIFF {s2}"


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
                        gr.add_edge(source_id, target_id, diff=html_diff(
                            gr.nodes[source_id]['comment'], gr.nodes[target_id]['comment']
                        ))

        return gr


def render_graph_component(component: networkx.Graph, output_dir: str):
    nsio = io.StringIO()
    esio = io.StringIO()

    for n in component.nodes:
        print(
            f"""node_{n} [shape="rectangle", label="{component.nodes[n]['label']}", """
            f"""href="#node_{n}"];""",
            file=nsio
        )

    for u, v in component.edges:
        print(
            f"""node_{u} -> node_{v} [label="diff", """
            f"""href="#edge_{u}_{v}"]; """,
            file=esio
        )

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))
    rt = env.get_template("one_graph.html").render(
        nodes=str(nsio.getvalue()),
        edges=str(esio.getvalue()),
        codes="Nothing here yet"
    )

    with open(os.path.join(output_dir, "%04d.html" % min(component)), 'w', encoding='utf-8') as wh:
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
    print("Rendering components...")
    for comp in tqdm.tqdm(components):
        render_graph_component(comp, args.output__dir)