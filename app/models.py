from . import mongo
import datetime
import hashlib
import json
from Crypto.PublicKey import RSA
from Crypto import Random
from pprint import pprint

class User(object):
    def __init__(self, username, password=''):
        # Values to capture for a user, hash the password when received
        self.username = username
        self.password = self.hash_password(password)
        self.users = mongo.db.users

    def hash_password(self, password):
        # Hash the password and store it as a hexdigest
        hashed_password = hashlib.sha256(password.encode('UTF-8')).hexdigest()
        return hashed_password

    def register_new_user(self):
        # Attempt to register a new user
        # Return a response, depending on whether it was successful

        # Look for a user in the database
        user = self.users.find_one({'username': self.username})
        registration_success = False  # Init as False before creation

        if user is None:
            # Generate private and public keys
            private_key, public_key = self.create_RSA_keys()

            # Generate localize timestamp for Perth
            user_obj_id = self.users.insert_one({
                'username': self.username,
                'password': self.password,
                'created': datetime.datetime.now(),
                'private_key': private_key,
                'public_key': public_key
            }).inserted_id

            self.user_obj_id = user_obj_id
            self.public_key = public_key

            # If a user_id was successfully returned, user has been created
            if user_obj_id is not None:
                response = 'User was successfully created! Please log in below'
                registration_success = True
            else:
                response = 'Error: User could not be created!'
        else:
            response = 'User already exists!'

        return registration_success, response

    def create_RSA_keys(self):
        # Method to create private and public keys for users
        random_generator = Random.new().read
        rsa_object = RSA.generate(2048, random_generator)

        # Export the private and public keys
        private_key = rsa_object.exportKey(format='PEM')
        public_key_obj = rsa_object.publickey()
        public_key = public_key_obj.exportKey(format='PEM')

        return (private_key, public_key)

    def login_user(self):
        # Attempt to login
        users = mongo.db.users
        login_success = False  # Init as False until login confirmed

        # Look for the user in the database
        # Look for a user in the database
        user = users.find_one({'username': self.username})
        if user is not None:
            # Check the hashed password to see if it matches the entry in the database
            if user['password'] == self.password:
                response = 'Successfully logged in!'
                login_success = True
            else:
                response = 'Incorrect password!'
        else:
            response = 'User: \'{0}\' does not exist! Please register'.format(self.username)

        return (login_success, response)

    @staticmethod
    def create_new_transaction(from_username, to_username, amount):
        # Retrieve Documents for the 'from_user' and 'to_user'
        from_user = mongo.db.users.find_one({'username': from_username})
        to_user = mongo.db.users.find_one({'username': to_username})

        # Get the required public and private keys for the users
        from_user_private_key = from_user['private_key']
        from_user_public_key = from_user['public_key']
        to_user_public_key = to_user['public_key']

        # Create an RSA object using the users private_key
        from_user_private_key_obj = RSA.importKey(from_user_private_key)

        # Start building the blockchain transaction, using a dictionary object
        transaction = {
            'cc_amount': amount,
            'from_user_pk': from_user_public_key.decode('UTF-8'),
            'to_user_pk': to_user_public_key.decode('UTF-8')
        }

        # Sign the transaction using the 'from_users' private key
        transaction_json = json.dumps(transaction, sort_keys=True)

        hash_transaction = hashlib.sha256(
            bytes(str(transaction_json), encoding="UTF-8")
        ).hexdigest()

        signature = from_user_private_key_obj.sign(
            bytes(str(hash_transaction), encoding="UTF-8"), K=None
        )

        # Add 'signature to the dictionary object
        transaction['signature'] = signature

        # Dump updated transaction to JSON and send to Miner
        transaction_to_miner = json.dumps(transaction, sort_keys=True)

        # Send transaction to Miner for acceptance and to add to the blockchain
        response = Miner.add_transaction_to_blockchain(transaction_to_miner)

        return response

    @staticmethod
    def get_formatted_blockchain_log():
        # Get all the blockchain transactions from the database 'blockchain'
        blockchain_transactions = mongo.db.blockchain.find()
        # Parse transactions and load them into 'table_list'
        table_list = []

        for transaction in blockchain_transactions:
            to_user_pk = transaction['to_user_pk']
            from_user_pk = transaction['from_user_pk']

            # Helper function to encode as 'UTF-8' if not:
            if isinstance(to_user_pk, str):
                to_user_pk = to_user_pk.encode('UTF-8')
            if isinstance(from_user_pk, str):
                from_user_pk = from_user_pk.encode('UTF-8')

            # Cross-reference user database to get actual username
            to_user = mongo.db.users.find_one(
                {'public_key': to_user_pk}
            )
            to_user_username = to_user['username']

            # If from 'miner' set from username as simply 'miner'
            if from_user_pk == b'<miner>':
                from_user_username = '<miner>'
            else:
                from_user = mongo.db.users.find_one(
                    {'public_key': from_user_pk}
                )
                from_user_username = from_user['username']

            if to_user is not None:
                table_list.append({
                    'from_user': from_user_username,
                    'to_user': to_user_username,
                    'amount': transaction['cc_amount'],
                    'timestamp': transaction['timestamp'],
                    'nonce': transaction['nonce'],
                    'miner_verify': transaction['miner_verify']
                })

        return table_list

    @staticmethod
    def get_raw_blockchain_log():
        blockchain_transactions = mongo.db.blockchain.find()

        blockchain_list = []

        for transaction in blockchain_transactions:
            for key, val in transaction.items():
                transaction[key] = str(val)
            blockchain_list.append(transaction)

        return blockchain_list


    @staticmethod
    def get_username_list(username=None):
        # Find all users in the database and return a sorted username list
        # Optionally filter out the passed in username
        users = mongo.db.users.find()

        # Get the list of users
        username_list = [
            (str(user['username']), user['username'])
            for user in users
            if user['username'] != username
        ]

        # Now sort the values on 'username'
        username_list = sorted(username_list, key=lambda v: v[1])
        return username_list



class Miner(object):
    # Miner object for verifying and adding transactions and new users to the mongodb database
    # Currently only has static methods
    def __init__(self):
        self.blockchain = mongo.db.blockchain

    @staticmethod
    def initialise_new_user(user, chriscoins=100):
        blockchain = mongo.db.blockchain

        # Initialise the user on the blockchain and give the user an amount of chriscoins
        blockchain.insert_one({
            'from_user_pk': '<miner>',
            'to_user_pk': user.public_key,
            'cc_amount': chriscoins,
            'timestamp': datetime.datetime.now(),
            'nonce': '-',
            'miner_verify': True
        })

    @staticmethod
    def add_transaction_to_blockchain(transaction_json):
        blockchain = mongo.db.blockchain

        # Load the JSON file into a dictionary object
        transaction = json.loads(transaction_json)

        # Verify the signature on the transaction before adding to blockchain
        signature = transaction.pop('signature')  # Remove signature from the original object
        from_user_public_key_obj = RSA.importKey(transaction['from_user_pk'])
        transaction_no_sig_json = json.dumps(transaction, sort_keys=True)

        # Hash this transaction 'minus signature' and verify it against the supplied signature
        hashed_transaction_no_sig = hashlib.sha256(
            bytes(str(transaction_no_sig_json), encoding="UTF-8")
        ).hexdigest()

        verified_transaction = from_user_public_key_obj.verify(
            bytes(str(hashed_transaction_no_sig), encoding="UTF-8"),
            signature
        )

        if verified_transaction:
            # Transaction verified, add a few items to the transaction
            transaction['signature'] = str(signature)
            transaction['nonce'] = '-'
            transaction['miner_verify'] = True
            transaction['timestamp'] = datetime.datetime.now()

            # Now add to blockchain
            blockchain.insert_one(transaction)

            response = 'Transaction was successful'
        else:
            response = 'Transaction could not be verified'
            raise Exception

        # Return the success of the transaction
        return response
