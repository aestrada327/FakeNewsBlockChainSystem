from Class_definitions import Ranker,Network,Miner,Block,Block_Item,BlockChain,User,Media_Source
from Class_definitions import Document, Rating, Transaction, Block_Node, Website, Miner_Ranker,Evil_Ranker
import random
from matplotlib import pyplot as plt
import sys

# Parameter Instantiation
num_rankers= 10
num_miners = 10
num_media_sources = 10
Coin_Worth = 1
Num_Block_Mined = 1
Time_to_mine_block = 1
Percent_Of_GOOD = .7

num_iterations = 10
num_simulations = 10

def flush():
    sys.stdout.flush()

# Create Num User With Ratio
def Create_Num_Rankers_with_ratio(num_rankers,percent_good,network):
    num_good = int(round(percent_good * num_rankers))
    rankers = []
    # creating good users
    for i in range(num_good):
        n_email = ''.join(["ranker", str(i + 1), "@gmail.com"])
        n_ranker = Ranker(n_email, network)
        rankers.append(n_ranker)

    #creating bad users
    for i in range(num_rankers - num_good):
        n_email = ''.join(["ranker", str(i + 1 + num_good), "@gmail.com"])
        n_ranker = Evil_Ranker(n_email,network)
        rankers.append(n_ranker)

    return rankers

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
    if len(MS_to_rating) != 0:
        aggregate_acc[time_i] += float(acc_ratings)/float(len(MS_to_rating))

    #TODO Get average money per user
    return aggregate_acc

def Plot_Data(accuracy,num_iterations):
    iterations = range(1,num_iterations+1)
    plt.plot(iterations,accuracy,color = 'green', marker = 'o', linestyle = 'solid')
    plt.title("Average Accuracy per iteration of blockchain")
    plt.ylabel("Average Accuracy")
    plt.show()

def Plot_Data_Ratio(accuracy,num_iterations):
    iterations = range(0,num_iterations)
    iterations = map(lambda i: i*(1.0/num_iterations),iterations)
    plt.plot(iterations,accuracy,color = 'green', marker = 'o', linestyle = 'solid')
    plt.title("Average Accuracy vs. Percent of Good Agents")
    plt.ylabel("Average Accuracy")
    plt.xlabel("Percent of Good Agents")
    plt.show()


def Print_Ledger(rankers):
    r = random.randint(0,len(rankers)-1)
    rand_ranker = rankers[r]
    print "start of Ledger"
    sys.stdout.flush()
    print rand_ranker.get_Ledger()
    sys.stdout.flush()
    print "end of Ledger"
    sys.stdout.flush()

# reinitializes all the miners
def reinitialize_all_miners(miners):
    for miner in miners:
        miner.reinitialize_block()

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

    #makes all the miners let go of previous block they were working on
    reinitialize_all_miners(miner_lst)

# Simulate Code
def simulate_num_intervals(num_hashes,num_rankers,num_miners,num_media_sources,percent_good = 1):
    network = Network()
    # Rankers and Miners
    rankers = Create_Num_Rankers_with_ratio(num_rankers,percent_good,network)
    miners = Create_Num_Miners(num_miners,network)
    sources = Create_Num_Media_Sources(num_media_sources,network)

    #aggregate values for accuracy and
    acc = [0] * num_hashes
    avg_money = [0] * num_hashes

    # Run Num_Hash Intervals
    for i in range(num_hashes):
        print i+1
        simulate_One_Hash_Interval(rankers,miners)
        acc = Collect_Data(rankers,miners,sources,acc,avg_money,i)
    #getting Ledger information
    Print_Ledger(rankers)
    return acc

# Doing Num Simulations
def main_function():
    agg_acc = [0]*num_iterations
    for i in range(num_simulations):
        #printing simulation
        print "starting simulation {}".format(i+1)
        sys.stdout.flush()

        acc = simulate_num_intervals(num_iterations,num_rankers,num_miners,num_media_sources)
        agg_acc = [x + y for x, y in zip(agg_acc, acc)]
    agg_acc = map(lambda x: x/num_simulations, agg_acc)
    Plot_Data(agg_acc,num_iterations)

def bad_actors_simulation():
    agg_acc = [0] * num_iterations
    for i in range(num_simulations):
        # printing simulation
        print "starting simulation {}".format(i + 1)
        sys.stdout.flush()
        acc = simulate_num_intervals(num_iterations, num_rankers, num_miners, num_media_sources,Percent_Of_GOOD)
        agg_acc = [x + y for x, y in zip(agg_acc, acc)]
    agg_acc = map(lambda x: x / num_simulations, agg_acc)
    Plot_Data(agg_acc, num_iterations)

def simulate_GB_ratio_change(num_simulations,chain_length,num_miners,num_rankers,num_sources,percent_good):
    agg_acc = []
    for sim in range(num_simulations):
        acc = simulate_num_intervals(chain_length,num_rankers,num_miners,num_media_sources,percent_good)
        agg_acc.append(acc[-1])
    return sum(agg_acc)/(float(len(agg_acc)))

def good_bad_ratio_simulation_change(num_intervals):
    chain_length = 10
    num_simulations = 10
    agg_acc = [0] * num_intervals
    num_sources = 10
    num_rankers = 50
    num_miners = 10

    # For each ratio of good to bad
    for i in range(num_intervals):
        print "interval {}".format(i)
        flush()
        curr_ratio = i*(1.0/num_intervals)
        agg_acc[i] = simulate_GB_ratio_change(num_simulations,chain_length,num_miners,num_rankers,num_sources,curr_ratio)

    Plot_Data_Ratio(agg_acc,num_iterations)

good_bad_ratio_simulation_change(20)