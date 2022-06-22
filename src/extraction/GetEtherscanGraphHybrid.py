import pandas as pd
import requests
from tqdm import tqdm


API_KEY = 'ZW8EDBWKP1EI6DAW7TN567JY17K69DJYCR'
INIT_ADDRESS = '0xff0bd4aa3496739d5667adc10e2b843dfab5712b'


class GetTokenNetwork:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.url = "https://api.etherscan.io/api"
        self.contracts = pd.read_csv("data/ethcontracts_20220608.csv")

    def get_transactions(self, address):
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "apikey": self.api_key
        }
        transactions = requests.get(self.url, params=params)
        return pd.json_normalize(transactions.json(), record_path=["result"])

    def _in_contract_list(self, address):
        return address in self.contracts["address"]

    def create_attribute_fields(self, transactions, address):
        print("Adding Count Variables")
        transactions["critical_address"] = address
        transactions["total_transaction_count"] = transactions.shape[0]
        transactions["from_transaction_count"] = transactions[transactions["from"]==address].shape[0]
        transactions["to_transaction_count"] = transactions[transactions["to"]==address].shape[0]

        print("Adding 'From ABI' Variable")
        from_transactions = transactions[["from"]].drop_duplicates()
        from_transactions["from_has_abi"] = [self._in_contract_list(t) for t in tqdm(from_transactions["from"])]

        print("Adding 'To ABI' Variable")
        to_transactions = transactions[["to"]].drop_duplicates()
        to_transactions["to_has_abi"] = [self._in_contract_list(t) for t in tqdm(to_transactions["to"])]

        return transactions\
            .merge(from_transactions, on="from")\
            .merge(to_transactions, on="to")

    def create_summary_table(self, transaction_data):
        table = transaction_data["from"].append(transaction_data["to"])
        table = table\
            .groupby(table)\
            .size()\
            .reset_index()\
            .rename(columns={"index": "address", 0: "number_of_transactions"})
        table["has_abi"] = [self._in_contract_list(t) for t in tqdm(table["address"])]
        return table

    def get_transaction_dictionary(self, address_list):
        return {a: self.get_transactions(a) for a in tqdm(address_list)}



if __name__=="__main__":
    network = GetTokenNetwork()
    df = network.get_transactions(INIT_ADDRESS)
    df_summary = network.create_summary_table(df)
    df_summary.loc[df_summary["address"]==INIT_ADDRESS, "degree"] = 0
    df_summary.loc[df_summary["address"]!=INIT_ADDRESS, "degree"] = 1
    addr_list = df_summary\
        [(df_summary["has_abi"]==False) &
         (df_summary["degree"]==1)]\
        ["address"]\
        .tolist()

    second_degree_transactions = network.get_transaction_dictionary(address_list=addr_list)
    transaction_sizes = pd.Series({i: second_degree_transactions[i].shape[0] for i in second_degree_transactions})
    df_summ2 = df_summary\
        .merge(transaction_sizes.reset_index(), how="left", left_on="address", right_on="index") \
        .query("has_abi==False")\
        .rename(columns={0: "transaction_size"})\
        .sort_values("transaction_size")


    # STEP 2:
    degree_2_cutoff = 100
    # get all transacitons for all dataframes with less than 100 transactions
    # repat 1 more time
    attr_list_2 = df_summ2.query(f"transaction_size<={degree_2_cutoff}")["address"]

    first = True
    for i in attr_list_2.tolist():
        print(i)
        if first:
            all_second_degree_transactions = second_degree_transactions[i]
            first = False
        else:
            all_second_degree_transactions = all_second_degree_transactions.append(second_degree_transactions[i])

    df_summary2 = network.create_summary_table(all_second_degree_transactions)
    # remove abi records
    df_summary2 = df_summary2[df_summary2["has_abi"]==False]
    df_summary2_narrow = df_summary2[(~df_summary2["address"].isin([INIT_ADDRESS])) &
                (~df_summary2["address"].isin(df_summary["address"].tolist()))]

#    third_degree_transactions = network.get_transaction_dictionary(address_list=df_summary2_narrow["address"].tolist())

    # combine transactions together
    final_network = df.copy()
    for d in second_degree_transactions.values():
        final_network = final_network.append(d)

#    for d in third_degree_transactions.values():
#        final_network = final_network.append(d)

    # clean up final network
    final_network = final_network.drop_duplicates()

    # join on summary tables
    abi = df_summary[["address", "has_abi"]].append(df_summary2[["address", "has_abi"]])

    final_network = final_network\
        .merge(abi, how="left", left_on="to", right_on="address")\
        .merge(abi, how="left", left_on="from", right_on="address", suffixes=("_to", "_from"))

    # define abi for null values
    """
    print("Doing this hard part now")
    final_network.loc[final_network["has_abi_to"].isna(), "has_abi_to"] = final_network\
        .loc[final_network["has_abi_to"].isna(), "to"]\
        .apply(lambda x: network._has_abi(x))

    final_network.loc[final_network["has_abi_from"].isna(), "has_abi_from"] = final_network\
        .loc[final_network["has_abi_from"].isna(), "from"]\
        .apply(lambda x: network._has_abi(x))
"""
    final_network.to_csv("attr_sampling/data/final_network_v2.csv", index=False)
