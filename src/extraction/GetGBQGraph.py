import pandas as pd
from tqdm import tqdm
import os

INIT_ADDRESS = '0xff0bd4aa3496739d5667adc10e2b843dfab5712b'


class GetEthereumGraph:
    """Creates a social network graph of ethereum token transfers"""
    def __init__(self, init_address):
        """
        Returns an initial social graph based on the initial ethereum address.
        :param init_address: The initial ethereum address that the social graph is based on.
        :param api_key: The Ethereum API key.
        """
        self.contracts = self._get_contracts()
        self.processed_addresses = [init_address]
        self.transactions = self._get_ethereum_transactions([init_address])

    def _get_contracts(self, path='data/ethcontracts_20220608.csv'):
        return pd.read_csv(path)

    def _get_ethereum_transactions(self, addresses):
        address_list = ', '.join(["'" + a + "'" for a in addresses])
        query = f'''
        SELECT from_address, to_address, block_timestamp
        FROM `bigquery-public-data.crypto_ethereum.token_transfers` t
        where 1=1
          and (from_address != '0x0000000000000000000000000000000000000000' and
               to_address != '0x0000000000000000000000000000000000000000')
          and (from_address in ({address_list}) or 
               to_address in ({address_list}))'''
        transactions = pd.read_gbq(query, project_id='red-dominion-345521', reauth=True)
        transactions["is_contract_from"] = transactions["from_address"].isin(self.contracts["address"])
        transactions["is_contract_to"] = transactions["to_address"].isin(self.contracts["address"])
        return transactions



    def add_step(self):
        """
        Loops through every address and appends the graph of those transactions to the main graph.
        :return: pandas.DataFrame
        """
        from_addresses = self.transactions.query("is_contract_from==False")["from_address"]
        to_addresses = self.transactions.query("is_contract_to==False")["to_address"]
        addresses = from_addresses.append(to_addresses).unique()

        self.transactions = self.transactions.append(self._get_ethereum_transactions(addresses))
        self.transactions = self.transactions.drop_duplicates()



if __name__ == "__main__":
    # initialize graph
    ether_graph = GetEthereumGraph(INIT_ADDRESS)
    ether_graph.transactions
    # add step to graph
    ether_graph.add_step()
#    ether_graph.head()
