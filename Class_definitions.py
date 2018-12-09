import hashlib
import random
import time
from hashlib import sha256
import bisect
from os import chmod
from Crypto.PublicKey import RSA
import OpenSSL
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from Crypto.PublicKey import RSA
from Crypto import Random

### THIS FILE DEFINES ALL THE RELEVANT CLASSES FOR the Fake News Reputation System Simulation ####

# The Network class takes care of passing messages between nodes, providing users access to different websites
# and assigning IP_addresses to each user
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

    #gives new_IP address to each user
    def get_new_IP_Address(self):
        pass

#Generic website that makes has a network
class Website:
    def __init__(self,network):
        self.network = network
        if isinstance(self.network,Network):
            self.network.add_website(self)

    def change_network(self,network):
        if isinstance(network,Network):
            self.network =network
            self.network.add_website(self)

#Website that provides documents to the users, and collects documents from each media source in the network
class Document_Website(Website):
    def __init__(self,network,documents = []):
        super.__init__(self,network)
        self.topics_dict = {}
        self.add_documents(documents)

    # adds documents to its storage system
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

    # Collects all the Documents with Source and topic specifications
    def get_documents(self,source = None, topic = None):
        if topic in self.topics_dict:
            if source in self.topics_dict[topic]:
                return self.topics_dict[source][topic]
        return None

# Website that Acts as Certificate Authority providing correct public and private key information
class Certificate_Website(Website):
    def __init__(self,network):
        super.__init__(network)
        self.public_keys = []
        self.certificates = {}

    # Makes certificate using
    #TODO: Update to ensure new encryption method is included
    def __make_certificate(self,IP,PK):
        self.certificates[IP] = PK

    # Searches to see if PK is in the list
    def __Valid_Public_Key(self,PK):
        # binary search for public key
        index = bisect.bisect_left(self.public_keys,PK)
        return self.public_keys[index] == PK

    # adds public key in a sorted fashion
    def __add_Public_Key(self,PK):
        bisect.insort_right(self.public_keys,PK)

    def check_valid_certificate(self,IP,PK):
        return ((IP in self.certificates) and self.certificates[IP] == PK)

    #way for users to submit a Public Key to the Certificate Authority
    def submit_PK(self,IP,PK):
        if self.__Valid_Public_Key(PK):
            self.__add_Public_Key(PK)
            self.__make_certificate(IP,PK)

#Generic user of website
class User:
    def __init__(self,network,private_key = None,public_key = None,money = 0, blockchain = None):
        self.money = money
        self.blockchain = blockchain
        self.network = network
        self.IP_Address = network.get_new_IP_address()

        #generating private/public key pairs
        if private_key == None or public_key == None:
            self.private_key = self.generate_private_key()
            self.public_key = self.private_key.publickey()
        else:
            self.private_key = private_key
            self.public_key = public_key

    def generate_private_key(self):
        random_generator = Random.new().read
        return RSA.generate(1024, random_generator)

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
            if block.prefix == blockchain.get_last_hash() and User.__Valid_Ratings(block.rating_lst):
                return True
        return False

    # checks if the ratings in a block list are correctly defined
    @staticmethod
    def __Valid_Ratings(rating_lst):
        return all(map(lambda rating: User.__Valid_Rating(rating), rating_lst))

    #TODO # work out once encryption is finished
    @staticmethod
    def __Valid_Rating():
        pass

    # defines how a user will recieve an object passed in from the network
    #TODO
    def recieve(self,object):
        pass

#TODO
class Miner(User):
    # average time (secs) for hash
    avg_time_hash = 60

    def __init__(self,private_key,public_key,network,money = 0, blockchain = None,ratings = []):
        super.__init__(private_key,public_key,network,money, blockchain)
        # creating empty Block with previous hash
        self.__block = Block(blockchain.get_last_hash())
        self.mined_hash = None

    #searches for correct hash value
    #TODO # currently on sleeping for avg_time
    def Mine_Hash_Val(self):
        time.sleep(Miner.avg_time_hash)

    def Add_block_to_blockchain(self):
        pass

    def Send_block_to_users(self):
        pass

    def recieve_rating(self):
        pass

    def recieve_ratings(self):
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

    def __init__(self,network, document_lst = [],trustworthiness = -1):
        self.network = network
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

    def change_network(self,network):
        self.network = network

# defines a news article/document
class Document:
    def __init__(self,Is_Fake_news, source,Title = None,topic = None):
        self.__Is_Fake_news = Is_Fake_news
        self.Title = Title
        self.topic = topic
        self.source = source

# defines a rating generated by a user for a document
# TODO # needs encrypption method
class Rating:
    def __init__(self,doc,media_source,rating,rater, hashed_signature):
        self.doc = doc
        self.media_source = media_source
        self.rating = rating
        self.rater = rater
        self.hashed_signature = hashed_signature

    #TODO Converts the rating into a string, needed for Block Hash_Values
    def toString(self):
        pass

# A Block that includes Transactions, Ratings, Generational Hash, Nonce Value, Cryptography
class Block:
    #class variables
    max_num_ratings = 100

    def __init__(self,prefix,miner_PK, nonce, footer = None,rating_lst = []):
        self.prefix = prefix
        self.rating_lst = []
        self.nonce = nonce
        self.generation_transaction = miner_PK
        self.add_ratings(rating_lst)
        self.footer = self.__generatehashval()

    # adds ratings to block until max_num_ratings per block is reached
    def add_ratings(self,rating_lst):
        if all(map(lambda rating: isinstance(rating,Rating))):
            for rating in rating_lst:
                if len(self.rating_lst) < Block.max_num_ratings:
                    self.rating_lst.append(rating)
                else:
                    break

    #changes the previous hash value for block by calculating the hash
    def update_footer(self):
        self.footer = self.__generatehashval()

    # changes the nonce value and changes the footer hash as well
    def change_nonce(self,nonce):
        self.nonce = nonce
        self.update_footer()

    #changes the prefix
    def change_prefix(self,prefix):
        self.prefix = prefix

    # replaces the ratings information with the new ratings
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

    #getting the string representation of all the ratings and accumulating them onto a string
    def __accumulate_strings_of_ratings(self):
        str_lst = []
        for rating in self.rating_lst:
            str_lst.append(rating.toString())
        return (''.join(str_lst))

    #hashes with the sha256 the nonce value, the previous hash, and the transactions in the block respectively
    def __generatehashval(self):
        hasher = sha256()
        hashvals = [str(self.nonce),self.prefix,self.__accumulate_strings_of_ratings()]
        hasher.update(''.join(hashvals))
        return hasher.hexdigest()

# a Doubly Linked list of Block classes
class Block_Node:
    def __init__(self,block,prev = None,nxt = None,forked = None):
        self.prev = prev
        self.nxt = nxt
        self.forked = forked
        self.block = block

    def change_nxt(self,nxt):
        self.nxt = nxt

    def change_forked(self,forked_val):
        self.forked = forked_val

#Block Chain that keeps track of a Block_Nodes to enable easy forking abilities
class BlockChain:
    #class variable
    # maximum difference for two block chains to be different in length until one is dropped
    max_diff = 5

    def __init__(self,first_b,last_b):
        self.first_b = first_b
        self.last_b = last_b
        self.total_length = self.__get_length(self.first_b,self.last_b)
        self.forked_b = None
        self.forked_length = 0
        self.forked_last_val = None

    # gets length by working backwards from last to first
    def __get_length(self,first,last):
        counter = 0
        curr_b = last
        while curr_b != None and counter < 100000:
            if curr_b is first:
                return counter + 1
            else:
                curr_b = curr_b.prev
                counter += 1
        return None

    def add_block_end(self,block):
        if isinstance(block,Block_Node):
            block.prev = self.last_b
            self.last_b.change_nxt(block)
            self.last_b = block
            self.total_length += 1
            return True
        return False

    def add_block_end_forked(self,block):
        if isinstance(block,Block_Node) and self.forked_last_val != None:
            block.prev = self.forked_last_val
            self.forked_last_val.nxt = block
            self.forked_last_val = block
            self.forked_length += 1
            return True
        return False

    #Adds a block to the block chain ensuring prefix manner, Includes prefix
    #returns boolean statement stating if block was added to the chain or not
    def add_block_prefix_matching(self,block):
        #ensuring proper data_structure was passed in
        if isinstance(block,Block):
            n_block = Block_Node(block)
        elif isinstance(Block_Node,block):
            n_block = block
        else:
            return False
        #finding valid block
        [valid_block,is_forked] = self.__search_for_block_with_hash(n_block.block.prefix)

        # checking to see if a block was found
        if valid_block == None:
            return False
        elif is_forked:
            # adding block to the end of the forked value
            if valid_block is self.forked_last_val:
                self.add_block_end_forked(valid_block)
                return True
            return False
        else:

            if valid_block is self.last_b:
                self.add_block_end(n_block)
                return True

            # getting length of new block chain
            length_valid = self.__get_length(self.first_b,valid_block) + 1
            # changing forked value to new block if length of new block chain is greater than previous
            if length_valid > self.forked_length :
                self.__update_forked_vals(valid_block,n_block)
                return True
            return False

    # Forks Blockchain at Forked_b with forked_b value
    #returns  True or False if forking is possibly
    def __update_forked_vals(self,forked_b,first_fork_b):
        # ensuring both args ars Block Nodes and Valid Blocks to Fork
        if isinstance(forked_b,Block_Node) and isinstance(first_fork_b,Block_Node)\
                and forked_b != None and first_fork_b != None and not (forked_b is self.last_b):
            self.__reset_forked_vals()
            self.forked_b = forked_b
            self.forked_b.forked = first_fork_b
            first_fork_b.prev = self.forked_b
            self.forked_last_val = first_fork_b
            self.forked_length = self.__get_length(self.first_b, self.forked_last_val)
            return True
        return False

    # resets forked values to initial starting positions
    # removing any forked values from Linked List
    def __reset_forked_vals(self):
        if self.forked_b != None:
            self.forked_b.forked = None
        self.forked_b = None
        self.forked_last_val = None
        self.forked_length = 0

    def change_forked_b(self,forked_b,forked_val):
        self.forked_b = forked_b
        self.forked_b.forked = forked_val
        self.forked_last_val = forked_val
        self.forked_length = self.__get_length(self.first_b,self.forked_last_val)

    #Changes blockchain to keep longest block_chain (chooses either forked value or original blockchain)
    # if both chains are the same length: keeps original chain and erases forked value
    def Update_BlockChain(self):
        if self.forked_length > self.total_length:
            #changing forked chain as original
            self.total_length = self.forked_length
            self.last_b = self.forked_last_val
        #resetting forked vals
        self.__reset_forked_vals()

    #search for block that is less than max_diff away from end and also has same prefix value
    #returns a list with elements: 1. the Found Valid Block 2. is the block a forked value
    def __search_for_block_with_hash(self,prev_hash):
        # searching for correct prefix in unforked chain
        primary_search_val = self.__search(BlockChain.max_diff,prev_hash,self.last_b)
        if primary_search_val != None:
            return [primary_search_val,False]
        elif self.forked_last_val != None:
            # searching through forked blockchain
            forked_search_val = self.__search(BlockChain.max_diff,prev_hash,self.forked_last_val)
            return [forked_search_val,True]

    # searches through linked list starting end value to find prev_hash value
    # looks up to distance of max length from end
    def __search(self,max_length,prev_hash,last_block):
        counter = max_length
        temp_block = last_block
        for i in range(counter):
            if temp_block == None:
                return None
            elif temp_block.block.footer == prev_hash:
                return temp_block
            elif temp_block.prev != None:
                temp_block = temp_block.prev
            else:
                return None
        return None

    #gets the hash of the last block in the block_chain
    def get_last_hash(self):
        if self.last_b == None:
            return None
        return self.last_b.block.footer

    #gets the hash of the forked value
    def get_last_forked_hash(self):
        if self.forked_last_val == None:
            return None
        return self.forked_last_val.block.footer

    # returns the original and forked blockchain last hashes
    def get_last_hashes(self):
        return [self.get_last_hash(),self.get_last_forked_hash()]