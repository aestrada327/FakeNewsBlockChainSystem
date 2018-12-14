from Class_definitions import Ranker,Network,Miner,Block,Block_Item,BlockChain,User,Media_Source
from Class_definitions import Document, Rating, Transaction, Block_Node, Website, Miner_Ranker
import random

# Parameter Instantiation
num_rankers= 1000
num_miners = 100
num_media_sources = 100
Coin_Worth = 1
Num_Block_Mined = 1
Time_to_mine_block = 1
ratio_of_good_bad_people = .5

num_iterations = 1000
num_simulations = 1000
# Create Num User With Ratio
def Create_Num_User_with_ratio(num_users,ratio_of_good_bad_people):
    pass

# Create Num Rankers and adds them to the network
def Create_Num_Rankers(num_rankers,network):
    rankers = []
    for i in range(num_rankers):
        n_email = ''.join(["ranker",str(i+1),"@gmail.com"])
        n_ranker = Ranker(n_email,network)
        rankers.append(n_ranker)
    return rankers

# Creates Miners and places them inside the network
def Create_Num_Miners(num_miners,network):
    miners = []
    for i in range(num_miners):
        n_email = ''.join(["miner", str(i+1), "@gmail.com"])
        n_miner = Miner(n_email,network)
        miners.append(n_miner)
    return miners

# Creates Media Sources and adds them to the network
def Create_Num_Media_Sources(num_sources,network):
    sources = []
    for i in range(num_sources):
        n_name = ''.join(["MediaSource",str(i+1)])
        n_source = Media_Source(network,n_name)
    network.add_mediasources(sources)
    return sources

def Collect_Data(rankers,miners):
    pass

def Plot_Data(data):
    pass

# Simulate One Hash interval
def Simulate_One_Hash_Interval(ranker_lst,miner_lst):
    # Get One Ranker to Rank Per Time Interval
    for i in range(Time_to_mine_block):
        r = random.randint(0,len(ranker_lst))
        rand_ranker = ranker_lst[r]
        rand_ranker.run()

    # Choose One Random Miner to Mine the next Block
    r = random.randint(0,len(miner_lst))
    rand_miner = miner_lst[r]
    rand_miner.run()

def simulate_num_intervals(num_hashes,num_rankers,num_miners,num_media_sources):
    network = Network()
    # Rankers and Miners
    rankers = Create_Num_Rankers(num_rankers,network)
    miners = Create_Num_Miners(num_miners,network)
    sources = Create_Num_Media_Sources(num_media_sources,network)
    data = []

    # Run Num_Hash Intervals
    for i in range(num_hashes):
        Simulate_One_Hash_Interval(rankers,miners)
        ndata = Collect_Data(rankers,miners)
        data.append(ndata)

    # Plotting the Data for the simulation
    Plot_Data(data)

# Doing Num Simulations
def main_function():
    for i in range(num_simulations):
        simulate_num_intervals(num_iterations,num_rankers,num_miners,num_media_sources)
