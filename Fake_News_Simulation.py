import Class_definitions
import random

# Parameter Instanciation
num_Users = 1000
Coin_Worth = 1
Num_Block_Mined = 1
Time_to_mine_block = 1
ratio_of_good_bad_people = .5

# Create Num User With Ratio
def Create_Num_User_with_ratio(num_users,ratio_of_good_bad_people):
    pass

#Create Num Media Sources

def Create_Num_Rankers(num_users):
    pass

def Create_Num_Miners(num_miners):
    pass


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

def Simulate_number_of_passed(num_hashes,num_rankers,num_miners):
    # Rankers and Miners
    rankers = Create_Num_Rankers(num_rankers)
    miners = Create_Num_Miners(num_miners)
    data = []

    # Run Num_Hash Intervals
    for i in range(num_hashes):
        Simulate_One_Hash_Interval(rankers,miners)
        ndata = Collect_Data(rankers,miners)
        data.append(ndata)

    # Plotting the Data for the simulation
    Plot_Data(data)