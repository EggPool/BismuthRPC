#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A basic Bismuth node.py client for the Json-RPRC gateway
Also handles wallet and accounts
@EggPool

"""

# Generic modules
#import socket, sys


# Bismuth specific modules
from rpcconnections import Connection
from rpcwallet import Wallet
from ttlcache import Asyncttlcache

"""
Note: connections.py is legacy. Will be replaced by a "command_handler" class. WIP, see protobuf code.
"""

__version__ = '0.0.3'


class Node:
    """
    Connects to a node.py via socket of use local filesystem if needed to interact with a running bismuth node.
    """
    
    __slots__ = ("config", "wallet", "s", "connection")
    
    def __init__(self, config):
        self.config = config
        self.wallet = Wallet(verbose=config.verbose)
        # TODO: raise error if missing critical info like bismuth node/path
        node_ip, node_port = self.config.bismuthnode.split(":")
        self.connection = Connection((node_ip, int(node_port)), verbose=config.verbose)

 
    """
    All json-rpc calls are directly mapped to async methods here thereafter:
    As the mapping is auto, we can't conform to PEP and thus, no underscore in method names.
    """
    
    def stop(self, *args, **kwargs):
        """Clean stop the server"""
        print("Stopping Server")
        self.connection.close(self.s)
        # TODO: Close possible open files and db connection
        
        # TODO: Signal possible threads to terminate and wait.
        return True
        
        # NOT So simple. Have to signal tornado app to close (and not leave the port open) see 
        # https://stackoverflow.com/questions/5375220/how-do-i-stop-tornado-web-server
        # https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784
        #sys.exit()
 
 
    @Asyncttlcache(ttl=10)
    async def getinfo(self, *args, **kwargs):
        """
        Returns a dict with the node info
        Could take a param like verbosity of returned info later.
        """
        # WARNING: getinfo is deprecated and will be fully removed in 0.16. Projects should transition to using getblockchaininfo, getnetworkinfo, and getwalletinfo before upgrading to 0.16
        # However we get all info in one go, and it can be cached for subsequent partial info requests from other listed commands.
        try:       
            # TODO: connected check and reconnect if needed. But will be handled by the connection layer. Don't bother here.
            # Moreover, it's not necessary to keep a connection open all the time. Not all commands need one, so it just need to connect on demand if it is not.
            info = self.connection.command("statusjson")
            """
            info = {"version":self.config.version, "protocolversion":"mainnet0016", "walletversion":data[7], "testnet":False, # config data
                    "balance":10.00, "blocks":data[5], "timeoffset":0, "connections":data[1], "difficulty":109.65, # live status
                    "errors":""} # to keep bitcoind compatibility
            """
            # add extra info
            info["version"] = self.config.version
            info["errors"] = ""

        except Exception as e:
            info = {"version":self.config.version, "error":str(e)}
                
        return info


    async def getblockhash(self, *args, **kwargs):
        """
        Returns the hash of a given block_height
        """
        try:
            self.connection.send("blockget")
            self.connection.send(str(args[1]))
            block = self.connection.receive()
            block = block[0][7]
            
        except Exception as e:
            block = {"version":self.config.version, "error":str(e)}
        
        return block
        
    
    async def getrawmempool(self, *args, **kwargs):
        """
        WIP
        """
        try:
            self.connection.send("mempool")
            self.connection.send([])
            mempool = self.connection.receive()
            # WIP
            
        except Exception as e:
            mempool = {"version":self.config.version, "error":str(e)}
        
        return mempool
        
        
    async def getdifficulty(self, *args, **kwargs):
        """
        Returns the current network difficulty
        """
        try:
            info = await self.getinfo()
            diff = info["difficulty"]
            
        except Exception as e:
            diff = {"version":self.config.version, "error":str(e)}
            
        return diff


    async def getblocknumber(self, *args, **kwargs):
        """
        Deprecated. Removed in version 0.7. Use getblockcount. 
        Returns the number of blocks in the longest block chain. 
        """
        info = await self.getblockcount()
        return info


    # No need to cache since it's using cached getinfo()
    async def getblockcount(self, *args, **kwargs):
        """
        Returns the number of blocks in the longest block chain. 
        """
        info = await self.getinfo()
        try:
            blocks = info['blocks']
            return blocks
        except Exception as e:
            error = {"version":self.config.version, "error":str(e)}
            return error


    async def getaccountaddress(self, *args, **kwargs):
        """(account)
        Returns the current bitcoin address for receiving payments to this account.
        If (account) does not exist, it will be created along with an associated new address that will be returned.
        """
        try:
            account = args[1] # 0 is self
            address = self.wallet.get_account_address(account)
            # address is a single string.
            return address
        except Exception as e:
            error = {"version":self.config.version, "error":str(e)}                
        return error

        
    async def getnewaddress(self, *args, **kwargs):
        """(account)
        Returns a new bitcoin address for receiving payments. 
        If (account) is specified payments received with the address will be credited to (account). 
        """
        try:
            account = args[1] # 0 is self
            address = self.wallet.get_new_address(account)
            # address is a single string.
            return address
        except Exception as e:
            error = {"version":self.config.version, "error":str(e)}                
        return error

        
    async def backupwallet(self, *args, **kwargs):
        """(file_name)
        Backups the whole wallet directory in then given archive filename
        """
        try:
            file_name = args[1] # 0 is self
            return self.wallet.backup_wallet(file_name)
        except Exception as e:
            error = {"version":self.config.version, "error":str(e)}                
        return error                
        

    async def dumpwallet(self, *args, **kwargs):
        """(file_name)
        Sends all the priv keys from the wallet
        """
        try:
            file_name = args[1] # 0 is self
            return self.wallet.dump_wallet(file_name, self.config.version)
        except Exception as e:
            error = {"version":self.config.version, "error":str(e)}                
        return error                


    async def getbalance(self, *args, **kwargs):
        """
        Returns the balance of the whole wallet, or of a specific account
        """
        try:       
            # mockup
            balance = 99.99996160
            return balance

        except Exception as e:
            return {"version":self.config.version, "error":str(e)}


    async def listaccounts(self, *args, **kwargs):
        """
        List all accounts and balance of the wallet
        """
        try:
            # mockup
            list_accounts = {"":99.99996160}
            return list_accounts

        except Exception as e:
            return {"version":self.config.version, "error":str(e)}


    async def getaccount(self, *args, **kwargs):
        """
        Get the account of the provided address args[0]
        """
        #print (args[0])
        try:
            # mockup
            get_account = ""
            return get_account
        except Exception as e:
            return {"version":self.config.version, "error":str(e)}


    async def getaddressesbyaccount(self, *args, **kwargs):
        """
        List the addresses of the provided account args[1]
        """
        try:
            account = args[1] # 0 is self
            return self.wallet.get_addresses_by_account(account)
        except Exception as e:
            return {"version":self.config.version, "error":str(e)}


    async def listreceivedbyaddress(self, *args, **kwargs):
        """
        List the incoming transactions by address, for all adresses of the wallet.
        """
        try:
            # mockup
            list_received_by_address = [{"address":"moPhStktszZGwtVjziE7eoQ76ATQqfhMtK","account":"","amount":10.00000000,"confirmations":1,"label":"","txids":["82790ce7d1fd0df0bc2ffd3cdfdd452e36a32b90885984213a9424f083f74df4"]}]
            return list_received_by_address
        except Exception as e:
            return {"version":self.config.version, "error":str(e)}


    async def listsinceblock(self, *args, **kwargs):
        """
        List the transactions since the provided blockheight.
        """
        try:
            # mockup
            list_since_block = {"transactions":[{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":19,"generated":True,"blockhash":"1e60d7dba8bd93e99676dd72171e54eb8ffe35ebfb54439a646075c5a06eab11","blockindex":0,"blocktime":1516567237,"txid":"282ecec426b322698b6616f1cf70ebd767824645ea2b5526f38984fa78601b02","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":27,"generated":True,"blockhash":"2e6925dfb821aa90a5b0e8c9c921076158c79941e0e5a3153140cfb950c97c29","blockindex":0,"blocktime":1516567236,"txid":"5eaf83f5cb6b8f9b5bcf8f0ab0f2aa17ce3baf1d8d0e04467afbd2aba0a7b505","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":14,"generated":True,"blockhash":"39b09cc3bfbbf598bce6e00bc278be453a1d63940396dadb68a411a75e83c8e3","blockindex":0,"blocktime":1516567238,"txid":"eb213bfbb2e864c8b0d76d343b8bc3e05e952b467f264ad26ee94dbf3ad1380c","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":4,"generated":True,"blockhash":"570e1067a5d10485c707c352ef63c0f055c9c0080e7ec000a712b510a64fcbed","blockindex":0,"blocktime":1516567240,"txid":"5864254cb7ac736097257e31de0694afd98aac9286e0cf42458d414157acc70f","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":36,"generated":True,"blockhash":"13afa042517c9f7a367bf1a974344bcd59b91d60f622235172219bbbc5349bc0","blockindex":0,"blocktime":1516567234,"txid":"8fe36ed8d940405717b2c67bbc04dfa493a1764f67bdfcc0be074c350001a512","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":35,"generated":True,"blockhash":"0d942352ec5a8e504da1c3e62b7cf13422960210a13f4f5c39cbc628cb1cba69","blockindex":0,"blocktime":1516567235,"txid":"56d3a785f5d34c12fbdea4ce620b135d0efbdc673c68524b429afd6bffaa4313","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":11,"generated":True,"blockhash":"1427fea6b0fdfd0d2fbf64128fce1d00a6df311dc5c5cbc04513d472252aa5ae","blockindex":0,"blocktime":1516567239,"txid":"720871f16132ed9fb0146d4d2bba20b62b1e7838005132d765f18694d1790314","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":43,"generated":True,"blockhash":"499760ed4b9eb832c2cc236b3769f03809e46c5770233c3e6ff3c3808ef2cac4","blockindex":0,"blocktime":1516567233,"txid":"902fbbf636834c7ba3d9f1952ae0fdd368e349f369d47e1a061ab94c646f04f7","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":13,"generated":True,"blockhash":"374fc66965120c26f0d8270a5538ad4afc941e54591e500820ac454870e13a64","blockindex":0,"blocktime":1516567238,"txid":"636a2009aa80186685c00e60bec2b1cd99ff1d027e1ebf890f9791d1bf0a47fa","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"},{"account":"","address":"n2LAv7w2vG45gZSaFZBXQhTeaMndS1Y78W","category":"immature","amount":50.00000000,"vout":0,"confirmations":34,"generated":True,"blockhash":"44877e0fb2ccf89118079043fa7eaa5357c94a484724bd329c4bf99dcb5c6bd6","blockindex":0,"blocktime":1516567235,"txid":"0e62ce6d124ec07653341c7f3bd889f541b9f19bacca548d96e5cc941e7772fd","walletconflicts":[],"time":1516567222,"timereceived":1516567222,"bip125-replaceable":"no"}],"removed":[],"lastblock":"524e347f08e65c7d23bb7a24e6fae828f22db8a1d198bbe11aea655c18015a91"}
            return list_since_block
        except Exception as e:
            return {"version":self.config.version, "error":str(e)}
        
        
    """
    Here comes extra commands, that are *not* bitcoind compatible
    """   

    async def reindexwallet(self, *args, **kwargs):
        """
        Force a reindex of the wallet accounts and addresses
        """
        try:
            return self.wallet.reindex()
        except Exception as e:
            return {"version":self.config.version, "error":str(e)}
    
