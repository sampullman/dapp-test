
def validate_id(hash):
    if hash:
        if not hash.startswith("0x"):
            hash = "0x{}".format(hash)
        return hash
    else:
        return False

def safe_blocknumber(web3):
    try:
        return web3.eth.blockNumber
    except Exception as e:
        return None