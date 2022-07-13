import pandas as pd
import numpy as np
import requests
import networkx as nx
from tqdm import tqdm


class BreadthSearch:
    """
    Uses a breadth first search algorithm that terminates when the sanctioned address is discovered or all nodes have a
    risk score below the defined threshold.

    :param api_key: str, api key provided by etherscan.io
    :param sanctioned: str, the sanctioned address that is being searched for
    :param client: str, the client address we are searching from
    :param risk_limit: float, once a node falls below this limit it is no longer used in the search
    """
    def __init__(self, sanctioned, client, api_key, risk_limit=0.01):
        self.api_key = api_key
        self.sanctioned = sanctioned
        self.client = client
        self.risk_limit = risk_limit
        self.graph = self.get_transactions(self.client)
        self.graph.nodes[self.client]["processed"] = True

    def get_transactions(self, address):
        """
        Gets all transactions associated with a given node. Returns these transactions as a pandas dataframe
        :param address: An ethereum address with ERC20 transactions associated with it
        :return: nx.graph
        """
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "apikey": self.api_key
        }

        transactions = requests.get(url, params=params)
        transactions = pd.json_normalize(transactions.json(), record_path=["result"])
        return nx.from_pandas_edgelist(transactions, source="from", target="to")

    def _found_sanctioned_node(self):
        """
        Indicates if the sanctioned node is in sampled network.
        :return: bool
        """
        return self.graph.has_node(self.sanctioned)

    def _score_nodes(self):
        """
        Determines the risk score of the chain between all nodes and the client node.
        Only scores nodes that have been processed without scores
        :return: float
        """
        # filter to nodes that have been processed
        unscored_nodes = [i[0] for i in self.graph.nodes.data()]

        for node in unscored_nodes:
            # get the shortest path between all nodes and the source node
            shortest_path = nx.shortest_path(self.graph, self.client, node)

            # get the inverse degrees for each node in that path (1/degrees) and multiply together
            score = np.product([1/nx.degree(srch.graph, i) for i in shortest_path])*100

            # add that score to the node attributes
            self.graph.nodes[node]["score"] = score

    def _drop_maxout_nodes(self, maxout=10000):
        """
        Identify nodes with the maximum number of degrees and remove these from the network
        :param maxout: int, the maximum number of degrees allows (10,000 by default; this is the etherscan limit)
        """
        maxout_nodes = [i for i in self.graph if nx.degree(self.graph, i) >= maxout]
        for n in maxout_nodes:
            self.graph.remove_node(n)

    def add_step(self):
        """
        Loops through each node that is not marked as processed and has a score above the minimum.
        Gets transactions for those addresses.
        Finally, checks if the target node was found and displays a message indicating the results
        """
        # filter to all nodes not marked processed or having a score above the minimum
        print("Adding new step")
        pending_nodes = [i[0] for i in self.graph.nodes.data()
                         if "processed" not in i[1] and i[1]["score"] > self.risk_limit]

        # get transactions for those nodes and append them to the network
        for i in tqdm(range(len(pending_nodes))):
            node = pending_nodes[i]
            step = self.get_transactions(node)
            self.graph = nx.compose(self.graph, step)
            self.graph.nodes[node]["processed"] = True

        # check if target node is in the network and display of a message if it is
        return self._found_sanctioned_node()

    def full_search(self, max_iters=10):
        """
        Keeps adding layers until one of three conditions are met:
            1) the target node is found
            2) all nodes have a score below the threshold
            3) the maximum degrees out criteria is met
        prints the termination criteria
        :param max_degrees: int, the most layers that can be added to the network
        :return: nx.graph
        """
        i = 1
        while i < max_iters:
            if self._found_sanctioned_node():
                print("Found it!")
                break
            print(f"Starting Iteration #{i}")
            i = i + 1
            self._score_nodes()
            self.add_step()

    def risk_summary(self):
        """
         Prints a risk report for the connection between the client and sanctioned nodes
        :return: float, risk score for sanctioned node
        """
        # check if there is a path between both nodes (print error if not)
        # display risk report

    def display_graph(self):
        """
        displays a visualization of the network
        :return:
        """

def time_seeking_search(sanctioned, client):
    pass
    # init
    # 1) define a ring of nodes around the sanctioned address (these are the target nodes)
    # 2) define the "mean timestamp" of these edges (this is the target time we will be using in our pseudo distrance)

    # method 1
    # 3) Define a ring of nodes around the client
    # 4) check if any of those nodes match with the target nodes
    # 5) calculate the distance between those edges and the target time (this is our pseudo-distance)

    # method 2
    # 6) select the edge with the smallest pseudo-distance, record it in a "processed list"
    # 7) repeat steps 3-5 using the newly selected node
    # 8) calculate the risk score for the new branch of nodes
    # 9) if the risk score is below the risk cutoff, terminate that branch (add all nodes to the "processed list")

    # method 3 (with loop)
    # 10) select the node with the globally lowest pseudo-distance that is not in the "processed list"
    # 11) repeat steps 7-10 until a target node has been reached or all nodes are included in the "processed list"

    # method 4
    # 12) print report summarizing results

if __name__ == "__main__":
    # Part I: Assess the sanctioned transactions
    # get all transactions associated with the sanctioned address
    # using the laz network
    SANCTIONED_ADDRESS = "0x098b716b8aaf21512996dc57eb0615e2383e2f96"
    CLIENT_ADDRESS = "0xfbf4cfe1669a402c63ba0d0a2ce936949868931a"
    API_KEY = 'ZW8EDBWKP1EI6DAW7TN567JY17K69DJYCR'

    srch = BreadthSearch(sanctioned=SANCTIONED_ADDRESS, client=CLIENT_ADDRESS,
                         api_key=API_KEY)
    srch.full_search(max_iters=5)

