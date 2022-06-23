import pandas as pd
import requests
import networkx as nx
from tqdm import tqdm

API_KEY = 'ZW8EDBWKP1EI6DAW7TN567JY17K69DJYCR'
KNOWN_CONTRACTS = pd.read_csv('data/ethereum_contracts_20220622.csv')

class CreateNetwork:
    def __init__(self, init_address, contracts, api_key):
        self.api_key = api_key
        self.init_address = init_address
        self.contracts = contracts

        self.graph = self._get_transactions(init_address)
        self.processed_addresses = [init_address]

    def _get_transactions(self, address):
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "apikey": self.api_key
        }
        transactions = requests.get(url, params=params)
        transactions = pd.json_normalize(transactions.json(), record_path=["result"])
        return nx.from_pandas_edgelist(transactions, source="to", target="from",
                                       edge_attr=True, create_using=nx.DiGraph())

    def _append_graph(self, new_graph):
        self.graph = nx.compose(self.graph, new_graph)

    def prune_network(self, pruning_threshold):
        nodes_to_prune = pd.DataFrame(self.graph.degree, columns=["address", "degrees"])\
            .query(f"degrees>={pruning_threshold}")\
            .query(f"address!='{self.init_address}'")\
            ["address"]

        edge_list = pd.DataFrame(self.graph.edges, columns=["from", "to"])
        edge_list = edge_list\
            [(edge_list["from"].isin(nodes_to_prune)) | (edge_list["to"].isin(nodes_to_prune))]
        branchlets = edge_list["from"].append(edge_list["to"]).unique()
        self.processed_addresses = self.processed_addresses + list(branchlets)


    def add_step(self, include_contracts=False, max_out_degrees=100):
        new_transactions = list(set(self.graph.nodes)\
                                .difference(self.contracts)\
                                .difference(self.processed_addresses))
        for i in tqdm(range(len(new_transactions))):
            address = new_transactions[i]
            _t = self._get_transactions(address)
            self._append_graph(_t)
            self.processed_addresses = self.processed_addresses + [address]

    def add_additional_n_layers(self, layers, pruning_threshold):
        for i in range(layers):
            print(f"Adding Layer: {i+1}")
            self.prune_network(pruning_threshold)
            self.add_step()

    def save_graph(self, path):
        nx.write_gml(self.graph, path)

if __name__=="__main__":
    P = 100
    ADDITIONAL_LAYERS = 3

    # Logan Paul
    network = CreateNetwork('0xff0bd4aa3496739d5667adc10e2b843dfab5712b',
                            KNOWN_CONTRACTS["to_address"].to_list(),
                            API_KEY)
    network.add_additional_n_layers(layers=ADDITIONAL_LAYERS, pruning_threshold=100)
    network.save_graph("data/lp.gml")
    # save network for analysis

    # Logan Paul Alias
    network = CreateNetwork('0xd3cf54f8876ff28d4312cadb408de7830fa60228',
                            KNOWN_CONTRACTS["to_address"].to_list(),
                            API_KEY)
    network.add_additional_n_layers(layers=ADDITIONAL_LAYERS, pruning_threshold=100)
    network.save_graph("data/lp_alt.gml")

    # Lazurus Group
    network = CreateNetwork('0x098B716B8Aaf21512996dC57EB0615e2383E2f96',
                            KNOWN_CONTRACTS["to_address"].to_list(),
                            API_KEY)
    network.add_additional_n_layers(layers=ADDITIONAL_LAYERS, pruning_threshold=100)
    network.save_graph("data/laz.gml")

    # Laz Connected
    network = CreateNetwork('0xFbF4CFe1669A402c63Ba0D0a2Ce936949868931A',
                            KNOWN_CONTRACTS["to_address"].to_list(),
                            API_KEY)
    network.add_additional_n_layers(layers=ADDITIONAL_LAYERS, pruning_threshold=100)
    network.save_graph("data/laz_alt.gml")
