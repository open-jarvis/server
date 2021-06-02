"""
Copyright (c) 2021 Philipp Scheer
"""


import json
from jarvis import Crypto, Config, Logger, API
from classes.Client import Client


KEYLEN = 4096 # https://danielpocock.com/rsa-key-sizes-2048-or-4096-bits/


cnf = Config()
logger = Logger("Permission")
keys = cnf.get("keys", None)

if keys is None:
    logger.w("Keys", f"No public and private key set, generating keys with key length {KEYLEN}")
    priv, pub = Crypto.keypair(KEYLEN)
    keys = {"public": str(pub, "utf-8"), "private": str(priv, "utf-8")}
    result = cnf.set("keys", keys)

    logger.s("Keys", "Successfully created a public and private key and stored in the database") if result else \
    logger.e("Keys", "Failed to generate keys and store into database", "")


PUBLIC_KEY  = keys["public"]
PRIVATE_KEY = keys["private"]

CLIENT_KEYS = cnf.get("client-keys", {})


@API.route("jarvis/server/get/public-key")
def get_public_key(args, client, data):
    return PUBLIC_KEY

@API.route("jarvis/client/+/set/public-key")
def set_public_key(args, client: Client, data):
    global logger
    pub_key = data["public-key"]
    current_pub = client.get("public-key", None)
    # This function is dangerous because rogue clients could set the public key of real client and hijack him
    # We can prevent that by either only allowing one change (the initial set) of the public key (which is not a great idea because 
    # the client must stick to his initial private key and cannot upgrade the key size)
    # Another method would be to check the signature of the client, so that the rogue client also has to know the real private key (which is almost impossible)
    
    if current_pub is not None and current_pub.replace("\n", "") == pub_key.replace("\n", ""): # sent the original key (maybe on reconnect)
        return True
    client.set("public-key", pub_key)
    client.save()
    return True
    return False # trying to modify client public key
