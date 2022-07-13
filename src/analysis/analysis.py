import networkx as nx
from random import sample
import numpy as np

class NetworkAnalysis:
    def __init__(self, path_to_network):
        self.network = nx.read_gml(path_to_network).to_undirected()
        self.address_analysis = []

    def add_network(self, path_to_network):
        new_network = nx.read_gml(path_to_network).to_undirected()
        self.network = nx.compose(self.network,
                                  new_network)
        self.network.remove_edges_from(nx.selfloop_edges(self.network))

    def analysis_addresses(self, address1, address2):
        self.address_analysis = [address1, address2]

    def graph_network(self, sample_n):
        sample_chains = self._get_shortest_path()
        shortest_path = self._get_shortest_path()
        all_nodes = [*self.network.nodes]
        for i in range(sample_n):
            for critical_node in shortest_path:
                nodes = sample(all_nodes, 1)
                sample_chains = sample_chains + nx.shortest_path(self.network, critical_node, nodes[0])

        sub_g = self.network.subgraph(sample_chains)

        nx.draw(sub_g,
                node_color=["grey" if i not in self._get_shortest_path() else "red" for i in sub_g.nodes],
                node_size=[300 if i in self._get_shortest_path() else 100 for i in sub_g.nodes],
                width=0.5)

    def get_risk_weighting(self, sanctioned_node, chain_cutoff=4):
        if len(self.address_analysis) == 2:
            path = self._get_all_paths(chain_cutoff)
            return round(np.sum([np.product([1/nx.degree(net.network, i) for i in l if i != sanctioned_node])
                           for l in path]), 4)

        else:
            print("Error: Please pass addresses to analyse (use analysis_addresses method)")

    def risk_summary(self, sanctioned_node, chain_cutoff=4):
        if len(self.address_analysis) == 2:
            path = self._get_all_paths(chain_cutoff)
            risk = self.get_risk_weighting(sanctioned_node, chain_cutoff)
            shortest_path = self._get_shortest_path()

            print(f"===================================================================================\n"
                  f"\t***RISK REPORT***\n"
                  f"===================================================================================\n"
                  f"\tSanctioned Address:    {sanctioned_node}\n"
                  f"\tRisk Score:            {risk*100:.2f}%\n"
                  f"\tShortest Chain Length: {len(shortest_path)} degrees of separation\n\n"
                  f"\t------\n"
                  f"\tHigh Risk: >10%, Moderate Risk: 1-10%, Low Risk: 0.1-1%, Minimal Risk: <0.1%\n"
                  f"===================================================================================\n")
            return risk
        else:
            print("Error: Please pass addresses to analyse (use analysis_addresses method)")

    def _has_path(self):
        if len(self.address_analysis) == 2:
            return nx.has_path(self.network,
                               self.address_analysis[0],
                               self.address_analysis[1])
        else:
            print("Error: Please pass addresses to analyse (use analysis_addresses method)")

    def _get_shortest_path(self):
        if len(self.address_analysis) == 2:
            return nx.shortest_path(self.network,
                                    self.address_analysis[0],
                                    self.address_analysis[1])
        else:
            print("Error: Please pass addresses to analyse (use analysis_addresses method)")

    def _get_all_paths(self, cutoff=4):
        if len(self.address_analysis) == 2:
            all_paths =  nx.all_simple_paths(self.network,
                                             self.address_analysis[0],
                                             self.address_analysis[1],
                                             cutoff=cutoff)
            return [*all_paths]
        else:
            print("Error: Please pass addresses to analyse (use analysis_addresses method)")


if __name__ == "__main__":
    sample_addresses = {
        'lp_alt': "0xd3cf54f8876ff28d4312cadb408de7830fa60228",
        'lp': "0xff0bd4aa3496739d5667adc10e2b843dfab5712b",
        'laz': "0x098B716B8Aaf21512996dC57EB0615e2383E2f96".lower(),
        'laz_alt': "0xFbF4CFe1669A402c63Ba0D0a2Ce936949868931A".lower(),
        'laz_alt_2': "0x55999Fd3693E69f5384F32f70FE89C34b29C26a4".lower()}
    # load network to analyze
    net = NetworkAnalysis("data/graphs/laz.gml")
    net.add_network("data/graphs/lp.gml")

    net.analysis_addresses(sample_addresses["laz"],
                           sample_addresses["lp"])

    net.risk_summary(sample_addresses["laz"], 3)
   # net.graph_network(5)
