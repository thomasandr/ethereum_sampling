import pandas as pd
import requests
import networkx as nx
from tqdm import tqdm

API_KEY = 'ZW8EDBWKP1EI6DAW7TN567JY17K69DJYCR'
LP = '0xff0bd4aa3496739d5667adc10e2b843dfab5712b'

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
        counter = 1
        new_transactions = list(set(self.graph.nodes).difference(self.contracts))
        for i in tqdm(range(len(new_transactions))):
            address = new_transactions[i]
            if address not in self.processed_addresses:
                counter = counter + 1

                _t = self._get_transactions(address)
                self._append_graph(_t)
                self.processed_addresses = self.processed_addresses + [address]

    def add_additional_n_layers(self, layers, pruning_threshold):
        for i in range(layers+1):
            print(f"Adding Layer: {i}")
            self.prune_network(pruning_threshold)
            self.add_step()

if __name__=="__main__":
    P = 100
    network = CreateNetwork(LP, KNOWN_CONTRACTS["to_address"].to_list(), API_KEY)
    network.add_additional_n_layers(layers=3, pruning_threshold=100)
    # save network for analysis

    # repeat 5 more times
