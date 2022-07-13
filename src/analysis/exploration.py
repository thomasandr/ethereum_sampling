import networkx as nx
from random import sample

# load data
print("LP")
lp = nx.read_gml("data/graphs/lp.gml")
print("LP Alt")
lp_alt = nx.read_gml("data/graphs/lp_alt.gml")
print("Laz")
laz = nx.read_gml("data/graphs/laz.gml")
print("Laz alt")
laz_alt = nx.read_gml("data/graphs/laz_alt.gml")

sample_addresses = {
'lp_alt': "0xd3cf54f8876ff28d4312cadb408de7830fa60228",
'lp': "0xff0bd4aa3496739d5667adc10e2b843dfab5712b",
'laz': "0x098B716B8Aaf21512996dC57EB0615e2383E2f96".lower(),
'laz_alt': "0xFbF4CFe1669A402c63Ba0D0a2Ce936949868931A".lower(),
'laz_alt_2': "0x55999Fd3693E69f5384F32f70FE89C34b29C26a4".lower()}


# deteimine shortest paths
lp_full = nx.compose(laz, laz_alt).to_undirected()

# determine if path between nodes exists
nx.has_path(lp_full,
            sample_addresses["laz"],
            sample_addresses["laz_alt"])

# get shortest path
shortest_path = nx.shortest_path(lp_full,
            sample_addresses["laz_alt"],
            sample_addresses["laz"])

all_paths = nx.all_simple_paths(lp_full,
            sample_addresses["laz_alt"],
            sample_addresses["laz"],
            cutoff=4)

# get random sub graph
sub_g_nodes = lp_full.edge_subgraph(sample(lp_full.edges,100))
nx.draw(sub_g_nodes)

# random chain
# end points
sample_chains = shortest_path
for i in range(25):
    nodes = sample(lp_full.nodes, 2)
    sample_chains = sample_chains + nx.shortest_path(lp_full, nodes[0], nodes[1])
sub_g = lp_full.subgraph(sample_chains)

nx.draw(sub_g, node_color=["red" if i in shortest_path else "grey" for i in sub_g.nodes])
