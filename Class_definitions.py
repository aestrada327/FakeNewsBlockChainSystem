import random
import time
from hashlib import sha256
from collections import Counter
import bisect
from os import chmod
from Crypto.PublicKey import RSA
import OpenSSL
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from Crypto.PublicKey import RSA
from Crypto import Random
import sys

# THIS FILE DEFINES ALL THE RELEVANT CLASSES FOR the Fake News Reputation System Simulation ####

# The Network class takes care of passing messages between nodes, providing users access to different websites
# and assigning IP_addresses to each user
class Network:
    def __init__(self,*users):
        if all(map(lambda user: isinstance(user,User), users)):
            self.users = list(users)
        else:
            raise Exception("Invalid input: Network only admits a service")
        self.miners = []
        self.rankers = []
        self.websites = []
        self.emails = []
        self.media_sources = []
        self.emails_to_IPs = {}
        self.MAC_to_IPs = {}
        self.MAC_to_users = {}
        for user in users:
            if isinstance(user,User):
                self.emails.append(user.email)
                self.emails_to_IPs[user.email] = user.IP_Address
                self.MAC_to_users[user.MAC_ADDRESS] = user
            if isinstance(user,Miner):
                self.miners.append(user)
            if isinstance(user,Ranker):
                self.rankers.append(user)

    def add_mediasources(self,media_source_lst):
        if all(map(lambda source: isinstance(source,Media_Source),media_source_lst)):
            self.media_sources += media_source_lst
        else:
            for source in media_source_lst:
                if isinstance(source,Media_Source):
                    self.media_sources.append(source)

    #Randomly picks a media source until a media source is not found
    def get_new_source(self,visited_url_dict):
        # Checking if visited_url has been found
        if len(visited_url_dict) > len(self.media_sources):
            return None
        # finding new media source
        rand = random.randint(0,len(self.media_sources) - 1)
        rand_MS = self.media_sources[rand]
        while rand_MS.url in visited_url_dict:
            rand = random.randint(0,len(self.media_sources) - 1)
            rand_MS = self.media_sources[rand]
        return self.media_sources[rand]

    #add users to the network
    def add_users(self,user_lst):
        if all(map(lambda user: isinstance(user,User),user_lst)):
            for user in user_lst:
                self.users.append(user)
                if isinstance(user, Miner):
                    self.miners.append(user)
                if isinstance(user, Ranker):
                    self.rankers.append(user)

    # adds a website to the network
    def add_website(self, website):
        if isinstance(website, Website):
            self.websites.append(website)

    # sends a rating to all the miners in the network
    def send_rating_to_miners(self, sender, rating):
        for miner in self.miners:
            if not (miner is sender):
#                print "recieving rating"
#                sys.stdout.flush()
                miner.recieve_rating(rating)

    def send_ratings_to_miners(self,sender,ratings):
        for miner in self.miners:
            if not (miner is sender):
                miner.recieve_ratings(ratings)

    # sends a new block to everyone in the network
    def send_block(self,user,block):
        for curr_user in self.users:
            if not(curr_user is user):
                curr_user.recieve_block(block)

    # gives new_IP address to a user, only gives one IP Address per MAC_Address
    #TODO store mac_addresses in a sorted fassion
    def get_IP_Address(self, mac_address):
        if mac_address not in self.MAC_to_IPs:
            self.MAC_to_IPs[mac_address] = len(self.MAC_to_IPs) + 1
        return self.MAC_to_IPs[mac_address]

    # publishes documents in the document lst
    def publish_documents(self,document_lst):
        doc_web_found = False
        for website in self.websites:
            if isinstance(website, Document_Website):
                website.add_documents(document_lst)
                doc_web_found = True
        return doc_web_found

    #publishes a public key to the Certificate Website
    def publish_public_key(self,public_key,MAC_Address,IP_address):
        CA_found = False
        for website in self.websites:
            if isinstance(website, Certificate_Website):
                website.submit_PK(IP_address,public_key)
                CA_found = True
        return CA_found

# Generic website that makes has a network
class Website:
    def __init__(self,network):
        self.network = network
        if isinstance(self.network,Network):
            self.network.add_website(self)

    def change_network(self,network):
        if isinstance(network,Network):
            self.network =network
            self.network.add_website(self)

# Website that provides documents to the users, and collects documents from each media source in the network
class Document_Website(Website):
    def __init__(self,network,documents = []):
        Website.__init__(self,network)
        self.topics_dict = {}
        self.add_documents(documents)

    # adds documents to its storage system
    def add_documents(self,documents):
        if all(map(lambda doc: isinstance(doc,Document),documents)):
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
        Website.__init__(self,network)
        self.public_keys = []
        self.certificates = {}

    # Makes certificate using
    # TODO: Update to ensure new encryption method is included
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

    # way for users to submit a Public Key to the Certificate Authority
    def submit_PK(self,IP,PK):
        if self.__Valid_Public_Key(PK):
            self.__add_Public_Key(PK)
            self.__make_certificate(IP,PK)

# Generic user of website
class User:

    MAC_ADDRESS_LENGTH = 12

    def __init__(self,email,network,private_key = None,public_key = None,money = 0, blockchain = None, mac_address = None):
        # adding self to the network
        self.network = network
        network.add_users([self])
        self.email = email
        self.money = money

        if blockchain is not None:
            self.blockchain = blockchain
        else:
            self.blockchain = BlockChain(None,None)

        # Dictionary of emails of people who have previously gotten a negative score
        self.invalid_emails = {}
        self.emails_to_MS = {}

        # generating MAC Address
        if mac_address is not None:
            self.MAC_ADDRESS = mac_address
        else:
            self.MAC_ADDRESS = self.__generate_MAC_ADDRESS()

        self.IP_Address = network.get_IP_Address(self.MAC_ADDRESS)

        #generating private/public key pairs
        if private_key is None or public_key is None:
            self.__private_key = self.generate_private_key()
            self.public_key = self.__private_key.publickey()
        else:
            self.__private_key = private_key
            self.public_key = public_key

    def __generate_MAC_ADDRESS(self):
        MAC_ADDRESS = []
        for i in range(User.MAC_ADDRESS_LENGTH):
            MAC_ADDRESS.append(str(random.randint(0,9)))
        return ''.join(MAC_ADDRESS)

    def generate_private_key(self):
        random_generator = Random.new().read
        return RSA.generate(1024, random_generator)

    #adds block to its current block chain iff the block is a valid block for a blockchain
    def recieve_block(self,block):
        if self.Valid_Block(block,self.blockchain):
            #TODO Needs to Add Block Appropriately
            self.blockchain.add_block_end(block)
            self.update_block_chain_dep_vals()
        else:
            return False
        return True

    # Updates the Blockchain Values
    def update_block_chain_dep_vals(self):
        self.update_invalid_users()
        self.update_users_to_MS()

    def update_invalid_users(self):
        self.blockchain.score_all_users()
        user_to_rep = self.blockchain.users
        invalid_users = {}
        for user,rep in user_to_rep.iteritems():
            if rep < 0:
                invalid_users[user] = True
        self.invalid_emails = invalid_users

    #updates the users dictionary of which users have already ranked a certain media source
    def update_users_to_MS(self):
        s_to_MS = self.blockchain.get_sources_to_MS()
        self.emails_to_MS = s_to_MS

    # checks to see if valid block to add to blockchain
    def Valid_Block(self,block,blockchain):
        return True
        if isinstance(block,Block) and isinstance(blockchain,BlockChain):
            #ensures that the current block has the previous hash
            if block.prefix == blockchain.get_last_hash() and self.Valid_Ratings(block.block_items):
                return True
        return False

    # checks if the ratings in a block list are correctly defined
    def Valid_Ratings(self,rating_lst):
        return True
        return all(map(lambda rating: self.Valid_Rating(rating), rating_lst))

    # checks if the user doesn't have a negative reputation
    # and if the user hasn't ranked the news_source before
    def Valid_Rating(self,rating):
        return True
        if rating.email in self.invalid_emails:
            return False
        elif self.UserAlreadyRatedMS(rating):
            return False
        else:
            return True

    #Checks to see if the user has already rated the media source
    def UserAlreadyRatedMS(self,rating):
        MS_url = rating.media_source_url
        user_email = rating.email

        # checking the stored data read from the Block_Chain
        if user_email not in self.emails_to_MS:
            return False

        for url in self.emails_to_MS[user_email]:
            if MS_url == url:
                return True
        return False

    # defines how a user will recieve an object passed in from the network
    def recieve(self,object):
        if isinstance(object,Block):
            self.recieve_block(object)

    # publish a Public Key
    def publish_public_key(self):
        self.network.publish_public_key(self.publish_public_key(),self.MAC_ADDRESS,self.IP_Address)

    # Getting the ledger
    def get_Ledger(self):
        if self.blockchain is not None:
            return self.blockchain.toString()
        return None

    # Signs a rating
    #TODO
    def sign_rating(self,rating):
        if isinstance(rating,Rating):
            args = rating.String_to_Sign()
            #signature = self.__private_key

class Miner(User):
    # average time (secs) for hash
    avg_time_hash = 60
    max_nonce_val = sys.maxsize
    start_prefix_val = 1

    def __init__(self,email,network,private_key=None,public_key=None,money = 0, blockchain = None):
        User.__init__(self,email,network,private_key,public_key,money,blockchain)

        # creating empty Block with previous hash
        if blockchain != None:
            self.__block = Block(self.blockchain.get_last_hash(),self.email)
        else:
            self.__block = Block(Miner.start_prefix_val,self.email)

        self.mined_hash = None

    #Main Call from Simulation Code
    def run(self):
        self.Mine_Hash_Val()
        self.add_block_to_blockchain(self.__block)
        self.send_block_to_users()

    #searches for correct hash value
    def Mine_Hash_Val(self):
        r = random.randint(0,Miner.max_nonce_val)
        self.__block.change_nonce(r)
        self.__block.update_footer()

    def add_block_to_blockchain(self,block):
        if self.blockchain is not None:
            self.blockchain.add_block_end(block)
        else:
            new_node = Block_Node(block)
            self.blockchain = BlockChain(new_node,new_node)

    def send_block_to_users(self):
        self.network.send_block(self.__block,self)

    def recieve_rating(self,rating):
        if isinstance(rating,Rating):
#            print "Recieving Rating!"
#            sys.stdout.flush()
            self.add_rating_to_block(rating)

    def recieve_ratings(self,rating_lst):
        if all(map(lambda rating: isinstance(rating,Rating) and self.Valid_Rating(rating), rating_lst)):
            self.add_ratings_to_block(rating_lst)
        else:
            for rating in rating_lst:
                if self.Valid_Rating(rating) and isinstance(rating,Rating):
                    self.add_rating_to_block(rating)

    # Reinitializes Block
    # Use when another miner has found the block
    def reinitialize_block(self):
        self.__block = Block(self.blockchain.get_last_hash(),self.email)

    def add_rating_to_block(self,rating):
        if self.Valid_Rating(rating):
#            print "Valid Block"
#            sys.stdout.flush()
            self.__block.add_block_items([rating])
        else:
            print "inValid Block"
            sys.stdout.flush()

    def add_ratings_to_block(self,ratings):
        if self.Valid_Ratings(ratings):
#            print "Valid Block"
#            sys.stdout.flush()
            self.__block.add_block_items(ratings)
#        else:
#            print "InValid Block :("
#            sys.stdout.flush()

# users that rank documents
class Ranker(User):

    # ranking accuracy of users [0,1]
    ranking_acc = .7

    def __init__(self,email,network,private_key=None,public_key=None,doc_list = [],money = 0, blockchain = None):
        User.__init__(self,email,network,private_key,public_key,money, blockchain)
        self.visited_MS_urls = {}

    # Main Function run by the simulation code
    # ranks a new media source and sends the ranking to all the miners
    def run(self):
        self.rank_new_media_source()

    def rank_new_media_source(self):
        new_source = self.get_new_media_source()
        ranking = self.give_ranking(new_source)
#        print ranking.toString()
#        sys.stdout.flush()
        self.publish_ranking(ranking)

    def get_new_media_source(self):
        new_source = self.network.get_new_source(self.visited_MS_urls)
        if new_source != None:
            self.visited_MS_urls[new_source.url] = True
            return new_source
        return None

    def give_ranking(self,media_source):
        r = random.random()
        #accurate rating
        if r <= Ranker.ranking_acc:
            isMSfake = media_source.isfakenews
        else:
            isMSfake = not media_source.isfakenews
        return Rating(self.email, media_source.url,isMSfake)

    def publish_ranking(self,ranking):
        self.network.send_rating_to_miners(self,ranking)


class Evil_Ranker(Ranker):
    # ranks the opposite of what news sources media_source Ranking_Acc% of time
    def give_ranking(self,media_source):
        r = random.random()
        #accurate rating
        if r <= Ranker.ranking_acc:
            isMSfake = not media_source.isfakenews
        else:
            isMSfake =  media_source.isfakenews
        return Rating(self.email, media_source.url,isMSfake)

# in case a user is a ranker and a miner
class Miner_Ranker(User,Miner,Ranker):
    def __init__(self):
        pass
    def run(self,Lottery_winner):
        if Lottery_winner:
            # running like a miner
            self.Mine_Hash_Val()
            self.add_block_to_block_chain(self.__block)
            self.send_block_to_users()
        else:
            # running like a Rater
            self.rank_new_media_source()

#A source that exclusively makes new documents
#TODO
class Media_Source:

    # trustworthiness metrics
    min_trust = 0
    max_trust = 10

    def __init__(self,network, name, url = None, document_lst = [],isfakenews = False):
        self.network = network
        self.name = name
        self.isfakenews = isfakenews
        if url == None:
            self.url = self.__generate_URL()

        if all(map(lambda doc: isinstance(doc,Document),document_lst)):
            self.document_lst = document_lst
        else:
            self.document_lst = []


    #generates a new document that is not Fake news with a probability of Trust/(max_trust-min_trust)
    def make_new_Doc(self):
        r = random.randint(Media_Source.min_trust,Media_Source.max_trust)
        if r<= self.__trustworthiness:
            self.document_lst.append(Document(False,self))
        else:
            self.document_lst.append(Document(True,self))

    #sends document to the whole network
    def publishDoc(self):
        if self.network is not None:
            self.network.publish_documents(self.document_lst)
            return True
        return False

    def change_network(self,network):
        self.network = network

    def __generate_URL(self):
        if self.name != None:
            return ''.join(["www.",self.name,".com"])
        return None

# defines a news article/document
class Document:
    def __init__(self,Is_Fake_news, source,Title = None,topic = None):
        self.__Is_Fake_news = Is_Fake_news
        self.Title = Title
        self.topic = topic
        self.source = source

#Items to be placed on the blockchain
class Block_Item:
    def __init__(self, hashed_signature = None):
        self.hashed_signature = hashed_signature

    def toString(self):
        return self.hashed_signature

#Rating items to be placed on the Block_chain system
# defines a rating generated by a user for a document
class Rating(Block_Item):
    def __init__(self,email, media_source_url, is_fake_news, hashed_signature = None):
        # Markers to identify User
        self.email = email

        #Media_source_identifier
        self.media_source_url = media_source_url

        #Rating that defines if media is fake or not
        self.is_fake_news = is_fake_news
        Block_Item.__init__(self,hashed_signature)

    def String_to_Sign(self):
        args = [self.email, self.media_source_url, str(self.is_fake_news)]
        return ' '.join(args)

    def toString(self):
        args = [self.email, self.media_source_url, str(self.is_fake_news)]
        return ''.join(args)

#Transaction items to be placed on the block chain
class Transaction(Block_Item):
    def __init__(self, sender, reciever, transact_amnt, hashed_signature = None):
        if isinstance(sender,User) and isinstance(reciever,User):
            self.sender_email = sender.email
            self.reciever_email = reciever.email
        else:
            self.sender_email = None
            self.reciever_email = None

        self.transact_amnt = transact_amnt
        Block_Item.__init__(self,hashed_signature)

    def toString(self):
        args = [str(self.sender_email),str(self.reciever_email),
                self.transact_amnt,self.hashed_signature]
        return ''.join(args)

    # Returns a String of relevant information for a user to sign with their private key
    def toString_to_Sign(self):
        args = [str(self.sender_email), str(self.reciever_email),
                self.transact_amnt]
        return ''.join(args)

# A Block that includes Transactions, Ratings, Generational Hash, Nonce Value, Cryptography
class Block:
    #class variables
    max_num_items = 100

    def __init__(self,prefix,miner_email, nonce = None, footer = None,block_items = []):
        self.prefix = prefix
        self.block_items = []
        self.nonce = nonce
        self.generation_transaction = miner_email
        self.add_block_items(block_items)
        self.footer = self.__generatehashval()

    # adds ratings to block until max_num_items per block is reached
    def add_block_items(self,block_items):
        if all(map(lambda block_item: isinstance(block_item,Block_Item),block_items)):
            for rating in block_items:
                if len(self.block_items) < Block.max_num_items:
                    self.block_items.append(rating)
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
    def replace_block_items(self,block_items):
        first = -1
        for i,item in enumerate(block_items):
            if len(self.block_items) < Block.max_num_items:
                if isinstance(item,Block_Item):
                    self.block_items.append(item)
            elif first == -1:
                first = i
            else:
                if i - first >= len(block_items) - 1:
                    first = i
                self.block_items[i-first] = item

    #getting the string representation of all the ratings and accumulating them onto a string
    def __accumulate_strings_of_block_items(self):
        str_lst = []
        for item in self.block_items:
            str_lst.append(item.toString())
        return (''.join(str_lst))

    #hashes with the sha256 the nonce value, the previous hash, and the transactions in the block respectively
    def __generatehashval(self):
        hasher = sha256()
        hashvals = [str(self.nonce),str(self.prefix),self.__accumulate_strings_of_block_items()]
        hasher.update(''.join(hashvals))
        return hasher.hexdigest()

    def aggregate_block_ratings(self, users):
        ratings = {}
        for item in self.block_items:
            #if item.item_type() == "rating":
            if isinstance(item,Rating):
                if item.email not in users:
                    val = 1
                    if item.is_fake_news:
                        val = -1
                    if item.media_source_url in ratings:
                        ratings[item.media_source_url] += val
                    else:
                        ratings[item.media_source_url] = val
                else:
                    if users[item.email]>=0:
                        val = 1
                        if item.is_fake_news:
                            val = -1
                        if item.media_source_url in ratings:
                            ratings[item.media_source_url] += val
                        else:
                            ratings[item.media_source_url] = val


        return ratings

    def ratings_by_user(self):
        users = {}
        for item in self.block_items:
            #if item.item_type() == "rating":
            if isinstance(item,Rating):
                user = item.email
                val = 1
                if item.is_fake_news:
                    val = 0
                if user not in users:
                    users[user] = {item.media_source_url : val}
                else:
                    users[user][item.media_source_url] = val
        return users

    def toString(self):
        ledger = []
        for item in self.block_items:
            ledger.append(item.toString())
        return ''.join(ledger)

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

    def toString(self):
        if self.block is not None:
            return self.block.toString()
        return None

# Block Chain that keeps track of Block_Nodes to enable easy forking abilities
class BlockChain:
    # class variable
    # maximum difference for two block chains to be different in length until one is dropped
    max_diff = 5
    max_length = 100000

    def __init__(self,first_b,last_b):
        self.first_b = first_b
        self.last_b = last_b
        self.total_length = self.__get_length(self.first_b,self.last_b)
        self.forked_b = None
        self.forked_length = 0
        self.forked_last_val = None
        #scores of the users
        self.users = {}
        self.users_money = {}

    # gets length by working backwards from last to first
    # prevents cycling
    def __get_length(self,first,last):
        counter = 0
        curr_b = last
        while curr_b is not None and counter < 100000:
            if curr_b is first:
                return counter + 1
            else:
                curr_b = curr_b.prev
                counter += 1
        return None

    # Adds Block to the End of the Block_Chain
    def add_block_end(self,block):
        if self.first_b is None or self.last_b is None:
            if isinstance(block,Block):
                n_block = Block_Node(block)
            elif isinstance(block,Block_Node):
                n_block = block
            else:
                return False
            self.first_b = n_block
            self.last_b = n_block
            self.total_length = 1
        else:
            if isinstance(block,Block):
                # checking if BlockChain does not have None Values
                n_block = Block_Node(block)
                n_block.prev = self.last_b
                self.last_b.change_nxt(n_block)
                self.last_b = n_block
                self.total_length += 1
                return True
            elif isinstance(block, Block_Node):
                block.prev = self.last_b
                self.last_b.change_nxt(block)
                self.last_b = block
                self.total_length += 1
                return True
            return False

    # Adds Block to the End of the Forked Block_Chain
    def add_block_end_forked(self, block):
        if isinstance(block,Block):
            n_block = Block_Node(block)
            n_block.prev = self.forked_last_val
            self.forked_last_val.nxt = n_block
            self.forked_last_val = n_block
            self.forked_length += 1
            return True
        elif isinstance(block, Block_Node) and self.forked_last_val is not None:
            block.prev = self.forked_last_val
            self.forked_last_val.nxt = block
            self.forked_last_val = block
            self.forked_length += 1
            return True
        return False

    # Adds a block to the block chain ensuring prefix manner, Includes prefix
    # Returns boolean statement stating if block was added to the chain or not
    def add_block_prefix_matching(self, block):
        #ensuring proper data_structure was passed in
        if isinstance(block, Block):
            n_block = Block_Node(block)
        elif isinstance(Block_Node, block):
            n_block = block
        else:
            return False
        #finding valid block
        [valid_block, is_forked] = self.__search_for_block_with_hash(n_block.block.prefix)

        # checking to see if a block was found
        if valid_block is None:
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
            length_valid = self.__get_length(self.first_b, valid_block) + 1
            # changing forked value to new block if length of new block chain is greater than previous
            if length_valid > self.forked_length :
                self.__update_forked_vals(valid_block, n_block)
                return True
            return False

    # Forks Blockchain at Forked_b with forked_b value
    # returns  True or False if forking is possibly
    def __update_forked_vals(self, forked_b, first_fork_b):
        # ensuring both args ars Block Nodes and Valid Blocks to Fork
        if isinstance(forked_b, Block_Node) and isinstance(first_fork_b, Block_Node)\
                and forked_b is not None and first_fork_b is not None and not (forked_b is self.last_b):
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
        if self.forked_b is not None:
            self.forked_b.forked = None
        self.forked_b = None
        self.forked_last_val = None
        self.forked_length = 0

    # changes the which value gets forked
    def change_forked_b(self, forked_b, forked_val):
        self.forked_b = forked_b
        self.forked_b.forked = forked_val
        self.forked_last_val = forked_val
        self.forked_length = self.__get_length(self.first_b, self.forked_last_val)

    # Changes blockchain to keep longest block_chain (chooses either forked value or original blockchain)
    # if both chains are the same length: keeps original chain and erases forked value
    def update_blockchain(self):
        if self.forked_length > self.total_length:
            # changing forked chain as original
            self.total_length = self.forked_length
            self.last_b = self.forked_last_val
        # resetting forked vals
        self.__reset_forked_vals()

    # search for block that is less than max_diff away from end and also has same prefix value
    # returns a list with elements: 1. the Found Valid Block 2. is the block a forked value
    def __search_for_block_with_hash(self, prev_hash):
        # searching for correct prefix in unforked chain
        primary_search_val = self.__search(BlockChain.max_diff, prev_hash, self.last_b)
        if primary_search_val is not None:
            return [primary_search_val, False]
        elif self.forked_last_val is not None:
            # searching through forked blockchain
            forked_search_val = self.__search(BlockChain.max_diff, prev_hash, self.forked_last_val)
            return [forked_search_val, True]

    # searches through linked list starting end value to find prev_hash value
    # looks up to distance of max length from end
    def __search(self, max_length, prev_hash, last_block):
        counter = max_length
        temp_block = last_block
        for i in range(counter):
            if temp_block is None:
                return None
            elif temp_block.block.footer == prev_hash:
                return temp_block
            elif temp_block.prev is not None:
                temp_block = temp_block.prev
            else:
                return None
        return None

    # gets the hash of the last block in the block_chain
    def get_last_hash(self):
        if self.last_b is None:
            return None
        return self.last_b.block.footer

    # gets the hash of the forked value
    def get_last_forked_hash(self):
        if self.forked_last_val is None:
            return None
        return self.forked_last_val.block.footer

    # returns the original and forked blockchain last hashes
    def get_last_hashes(self):
        return [self.get_last_hash(), self.get_last_forked_hash()]

    # gets the sources ratings
    def get_source_rating(self, news_source_url):
        curr_b = self.last_b
        rating = 0
        while curr_b is not None:
            ratings = curr_b.block.aggregate_block_ratings()
            if news_source_url in ratings:
                rating += ratings[news_source_url]
            curr_b = curr_b.prev
        return rating

    # returns dict of {news_source: 1 or 0}
    def get_all_ratings(self, users):
        curr_b = self.last_b
        all_ratings = {}
        binary_ratings = {}
        while curr_b is not None:
            curr_ratings = curr_b.block.aggregate_block_ratings(users)
            all_ratings = Counter(all_ratings) + Counter(curr_ratings)
            curr_b = curr_b.prev
        # 1 if real, 0 if fake
    	for source, rating in all_ratings.iteritems():
            if rating > 0:
                binary_ratings[source] = 1
            else:
                binary_ratings[source] = 0
        return binary_ratings

    def score_all_users(self):
        all_ratings = self.get_all_ratings(self.users)
        curr_b = self.last_b
        users = {}
        while curr_b is not None:
            curr_ratings = curr_b.block.aggregate_block_ratings(self.users)
            all_ratings = Counter(all_ratings) + Counter(curr_ratings)
            curr_users = curr_b.block.ratings_by_user()
            for user, ratings in curr_users.iteritems():
                score = 0
                for source, rating in ratings.iteritems():
                    if all_ratings[source] == ratings[source]:
                        score += 1
                    else:
                        score -= 1
                if user in users:
                    users[user] += score
                else:
                    users[user] = score
            curr_b = curr_b.prev
        self.users = users
        return users

    #TODO: accumulates the amount of money each user has
    def get_money_of_all_users(self):
        pass

    def get_sources_to_MS(self):
        all_ratings = self.get_all_ratings(self.users)
        curr_b = self.last_b
        users = {}
        while curr_b is not None:
            curr_ratings = curr_b.block.aggregate_block_ratings(self.users)
            all_ratings = Counter(all_ratings) + Counter(curr_ratings)
            curr_users = curr_b.block.ratings_by_user()
            for user, ratings in curr_users.iteritems():
                source_lst = []
                for source, rating in ratings.iteritems():
                    source_lst.append(source)
                if user in users:
                    users[user] += source_lst
                else:
                    users[user] = source_lst
            curr_b = curr_b.prev
        return users

    def toString(self):
        curr_b = self.first_b
        counter = 0
        ledger = []
        while curr_b is not None and counter < BlockChain.max_length:
            ledger.append(curr_b.toString())
        return ''.join(ledger)