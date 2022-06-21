import pandas as pd
import requests
import datetime
from tqdm import tqdm

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
        self.transactions = self._get_ethereum_transactions(init_address, self.api_key)

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

    def add_step(self):
        """
        Loops through every address and appends the graph of those transactions to the main graph.
        :return: pandas.DataFrame
        """
        addresses = self.transactions["from"].append(self.transactions["to"]).unique()
        for i in tqdm(range(len(addresses))):
            a = addresses[i]
            if a not in self.processed_addresses:
                self.transactions = pd.concat(
                    [self.transactions,
                     self._get_ethereum_transactions(a, self.api_key)],
                    axis=1
                )
                self.processed_addresses = self.processed_addresses + [a]
        self.transactions = self.transactions.drop_duplicates()


if __name__ == "__main__":
    ether_graph = GetEthereumGraph(INIT_ADDRESS)
    ether_graph.add_step()
