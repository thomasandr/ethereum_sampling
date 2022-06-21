import pandas as pd
import requests
import networkx as nx

API_KEY = 'ZW8EDBWKP1EI6DAW7TN567JY17K69DJYCR'
INIT_ADDRESS = '0xff0bd4aa3496739d5667adc10e2b843dfab5712b'


class GetEthereumGraph:
    """Creates a social network graph of ethereum token transfers"""
    def __init__(self, init_address, api_key=API_KEY):
        """
        Returns an initial social graph based on the initial ethereum address.
        :param init_address: The initial ethereum address that the social graph is based on.
        :param api_key: The Ethereum API key.
        """
        self.api_key = api_key
        self.processed_addresses = [init_address]
        self.graph = self._get_social_graph(init_address, self.api_key)

    def _get_ethereum_transactions(self, address, api_key):
        """
        Gets all token transfers from ethereum network.
        :param address: Ethereum address
        :param api_key: Etherscan API key
        :return: pd.DataFrame
        """
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "apikey": api_key
        }
        transactions = requests.get(url, params=params)
        return pd.json_normalize(transactions.json(), record_path=["result"])

    def _get_social_graph(self, address, api_key):
        """
        Returns the social network based on the list of transactions
        :param address: Ethereum address
        :param api_key: Etherscan API key
        :return: netowrkx.graph
        """
        data = self._get_ethereum_transactions(address, api_key)
        return nx.from_pandas_edgelist(data, source="from", target="to", edge_attr=True, create_using=nx.DiGraph())

    def add_step(self):
        """
        Loops through every address and appends the graph of those transactions to the main graph.
        :return: networkx.graph
        """
        for a in self.graph.nodes:
            if a not in self.processed_addresses:
                print(f"Address currently processing: {a}")
                self.graph = nx.union(self.graph,
                                      self._get_social_graph(a, self.api_key))
                self.processed_addresses = self.processed_addresses + [a]


if __name__ == "__main__":
    ether_graph = GetEthereumGraph(INIT_ADDRESS)
    ether_graph.add_step()
    nx.draw(ether_graph.graph)
