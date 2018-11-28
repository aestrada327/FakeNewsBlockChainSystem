import hashlib
import random
from hashlib import sha256
import bisect
### THIS FILE DEFINES ALL THE RELEVANT CLASSES FOR the Fake News Reputation System Simulation ####

# The Network class takes care of passing messages between nodes and is in charge of connecting different nodes
class Network:
    def __init__(self,*users):
        if all(map(lambda x: isinstance(x,User), users)):
            self.users = list(users)
        else:
            raise Exception("Invalid input: Network only admits a service")
        self.miners = []
        self.rankers = []
        self.websites = []
        for user in users:
            if isinstance(x,Miner):
                self.miners.append(user)
            if isinstance(x,Ranker):
                self.rankers.append(user)

    #add users to the network
    def add_users(self,user_lst):
        if all(map(lambda x: isinstance(x,User),user_lst)):
            for user in user_lst:
                self.users.append(user)
                if isinstance(x, Miner):
                    self.miners.append(user)
                if isinstance(x, Ranker):
                    self.rankers.append(user)

    # adds a website to the network
    def add_website(self,website):
        if isinstance(website,Website):
            self.websites.append(website)

    #sends a rating to all the miners in the network
    def send_rating_to_miners(self,user,rating):
        for miner in self.miners:
            if not(miner is user):
                miner.recieve(rating)

    # sends a new block to everyone in the network
    def send_block(self,user,block):
        for curr_user in self.users:
            if not(curr_user is user):
                curr_user.recieve_block(block)

    def get_new_IP_Address(self):
        pass

#Stores current documents and makes documents accessible to readers
class Website:
    def __init__(self,network):
        self.network = network
        if isinstance(self.network,Network):
            self.network.add_website(self)

    def change_network(self,network):
        if isinstance(network,Network):
            self.network =network
            self.network.add_website(self)

class Document_Website(Website):
    def __init__(self,network,documents = []):
        super.__init__(self,network)
        self.topics_dict = {}
        self.add_documents(documents)

    def add_documents(self,documents):
        if all(map(lambda x: isinstance(x,Document),documents)):
            for document in documents:
                if document.topic in self.topics_dict:
                    if document.source in self.topics_dict[document.topic]:
                        self.topics_dict[document.topic][document.source].append(document)
                    else:
                        self.topics_dict[document.topic]= {}
                        self.topics_dict[document.topic][document.source] = [document]
                else:
                    self.topics_dict[document.topic] = {}
                    self.topics_dict[document.topic][document.source] = [document]

class Certificate_Website(Website):
    def __init__(self,network):
        super.__init__(network)
        self.public_keys = []
        self.certificates = {}

    def __make_certificate(self,IP,PK):
        self.certificates[IP] = PK

    def __Valid_Public_Key(self,PK):
        # binary search for public key
        index = bisect.bisect_left(self.public_keys,PK)
        if self.public_keys[index] == PK:
            return True
        else:
            return False

    def __add_Public_Key(self,PK):
        bisect.insort_right(self.public_keys,PK)

    def check_valid_certificate(self,IP,PK):
        return ((IP in self.certificates) and self.certificates[IP] == PK)

    def submit_PK(self,IP,PK):
        if self.__Valid_Public_Key(PK):
            self.__add_Public_Key(PK)
            self.__make_certificate(IP,PK)

#Generic user of website
class User:
    def __init__(self,private_key,public_key,network,money = 0, blockchain = None):
        self.money = money
        self.blockchain = blockchain
        self.private_key = private_key
        self.public_key = public_key
        self.network = network
        self.IP_Address = network.get_new_IP_address()

    #adds block to its current block chain iff the block is a valid block for a blockchain
    def recieve_block(self,block):
        if User.Valid_Block(block,self.blockchain):
            self.blockchain.add(block)
        else:
            return False
        return True

    # checks to see if valid block to add to blockchain
    @staticmethod
    def Valid_Block(block,blockchain):
        if isinstance(block,Block) and isinstance(blockchain,BlockChain):
            #ensures that the current block has the previous hash
            if block.header == blockchain.get_last_hash() and User.__Valid_Ratings(block.rating_lst):
                return True
        return False

    # checks if the ratings in a block list are correctly defined
    #TODO
    @staticmethod
    def __Valid_Ratings(rating_lst):
        pass

    # defines how a user will recieve an object passed in from the network
    def recieve(self,object):
        pass
#TODO
class Miner(User):
    def __init__(self):
        pass
    def mine(self):
        pass
    def add_block_to_blockchain(self):
        pass
    def send_block_to_users(self):
        pass

# users that rank documents
#TODO
class Ranker(User):
    def __init__(self,private_key,public_key,doc_list,money = 0, blockchain = None):
        super.__init__(self,private_key,public_key,money, blockchain)
        self.doc_list = {}

    def get_new_doc(self):
        pass

    def give_ranking(self,doc):
        pass

    def publish_ranking(self):
        pass

# incase a user is a ranker and a miner
class Miner_Ranker(User,Miner,Ranker):
    pass

#A source that exclusively makes new documents
#TODO
class Media_Source:

    #trustworthiness metrics
    min_trust = 0
    max_trust = 10

    def __init__(self, document_lst = [],trustworthiness = -1):
        if all(map(lambda x: isinstance(x,Document),document_lst)):
            self.document_lst = document_lst
        else:
            self.document_lst = []
        if Media_Source.min_trust<=trustworthiness<=Media_Source.max_trust:
            self.__trustworthiness = trustworthiness
        else:
            self.__trustworthiness = random.randint(Media_Source.min_trust,Media_Source.max_trust)

    #generates a new document that is not Fake news with a probability of Trust/(max_trust-min_trust)
    def make_new_Doc(self):
        r = random.randint(Media_Source.min_trust,Media_Source.max_trust)
        if r<= self.__trustworthiness:
            self.document_lst.append(Document(False,self))
        else:
            self.document_lst.append(Document(True,self))

    #sends document to the whole network
    def publishDoc(self):
        pass

# defines a news article/document
class Document:
    def __init__(self,Is_Fake_news, source,Title = None,topic = None):
        self.__Is_Fake_news = Is_Fake_news
        self.Title = Title
        self.topic = topic
        self.source = source

# defines a rating generated by a user for a document
# TODO
class Rating:
    def __init__(self,doc,media_source,rating,rater, hashed_signature):
        self.doc = doc
        self.media_source = media_source
        self.rating = rating
        self.rater = rater
        self.hashed_signature = hashed_signature

# A Block that is placed in the block chain
class Block:
    #class variables
    max_num_ratings = 100

    def __init__(self,prefix,footer,rating_lst):
        self.prefix = prefix
        self.rating_lst = []
        self.footer = footer

        for rating in rating_lst:
            if len(rating) < Block.max_num_ratings:
                if isinstance(rating,Rating):
                    self.rating_lst.append(rating)
            else:
                break

    def add_ratings(self,rating_lst):
        for rating in rating_lst:
            if len(rating) < Block.max_num_ratings:
                if isinstance(rating,Rating):
                    self.rating_lst.append(rating)
            else:
                break

    def change_footer(self,footer):
        self.footer = footer

    def change_header(self,header):
        self.header = header

    # replaces the ratings information with the new information
    def replace_ratings(self,rating_lst):
        first = -1
        for i,rating in enumerate(rating_lst):
            if len(self.rating_lst) < Block.max_num_ratings:
                if isinstance(rating,Rating):
                    self.rating_lst.append(rating)
            elif first == -1:
                first = i
            else:
                if i - first >= len(rating_lst) - 1:
                    first = i
                self.rating_lst[i-first] = rating

#Block Chain class type
class BlockChain:
    def __init__(self,block_lst = []):
        if all(map(lambda x: isinstance(x,Block), block_lst)):
            self.block_lst = block_lst
        else:
            self.block_lst = []

    def add_block(self,block):
        if isinstance(block,Block):
            self.block_lst.append(block)

    #gets the hash of the last block in the block_chain
    def get_last_hash(self):
        length = len(self.block_lst)
        if length == 0:
            return None
        else:
            last_block = self.block_lst[length]
            return last_block.footer