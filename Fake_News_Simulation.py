from Class_definitions import Ranker,Network,Miner,Block,Block_Item,BlockChain,User,Media_Source
from Class_definitions import Document, Rating, Transaction, Block_Node, Website, Miner_Ranker
import random
from matplotlib import pyplot as plt

# Parameter Instantiation
num_rankers= 10
num_miners = 10
num_media_sources = 10
Coin_Worth = 1
Num_Block_Mined = 1
Time_to_mine_block = 1
ratio_of_good_bad_people = .5

num_iterations = 10
num_simulations = 10
# Create Num User With Ratio
def Create_Num_User_with_ratio(num_users,ratio_of_good_bad_people):
    pass

# Create Media Source with Ratio
def Create_Num_Media_source_with_ratio(num_sources,ratio_of_good_bad):
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
        sources.append(n_source)
    network.add_mediasources(sources)
    return sources

def Collect_Data(rankers,miners,media_sources,aggregate_acc,aggregate_money,time_i):
    # Getting a random ranker
    r = random.randint(0,len(rankers)-1)
    ranker = rankers[r]

    # Getting the average accuracy
    user_dict = ranker.blockchain.users
    MS_to_rating = ranker.blockchain.get_all_ratings(user_dict)
    acc_ratings = 0
    for source in media_sources:
        url = source.url
        if url in MS_to_rating:
            if MS_to_rating[url] != source.isfakenews:
                acc_ratings += 1
    aggregate_acc[time_i] += acc_ratings/len(media_sources)

    #TODO Get average money per user
    return aggregate_acc

def Plot_Data(accuracy,num_iterations):
    iterations = range(1,num_iterations+1)
    plt.plot(accuracy,iterations,color = 'green', marker = 'o', linestyle = 'solid')
    plt.title("Average Accuracy per iteration of blockchain")
    plt.ylabel("Average Accuracy")
    plt.show()


# Simulate One Hash interval
def simulate_One_Hash_Interval(ranker_lst,miner_lst):
    # Get One Ranker to Rank Per Time Interval
    for i in range(Time_to_mine_block):
        r = random.randint(0,len(ranker_lst) -1)
        rand_ranker = ranker_lst[r]
        rand_ranker.run()

    # Choose One Random Miner to Mine the next Block
    r = random.randint(0,len(miner_lst)-1)
    rand_miner = miner_lst[r]
    rand_miner.run()

def simulate_num_intervals(num_hashes,num_rankers,num_miners,num_media_sources):
    network = Network()
    # Rankers and Miners
    rankers = Create_Num_Rankers(num_rankers,network)
    miners = Create_Num_Miners(num_miners,network)
    sources = Create_Num_Media_Sources(num_media_sources,network)

    #aggregate values for accuracy and
    acc = [0] * num_hashes
    avg_money = [0] * num_hashes

    # Run Num_Hash Intervals
    for i in range(num_hashes):
        simulate_One_Hash_Interval(rankers,miners)
        acc = Collect_Data(rankers,miners,sources,acc,avg_money,i)

    return acc

# Doing Num Simulations
def main_function():
    agg_acc = [0]*num_iterations
    for i in range(num_simulations):
        print "starting simulation "
        acc = simulate_num_intervals(num_iterations,num_rankers,num_miners,num_media_sources)
        agg_acc = [x + y for x, y in zip(agg_acc, acc)]
    agg_acc = map(lambda x: x/num_simulations, agg_acc)

    Plot_Data(agg_acc,num_iterations)

main_function()