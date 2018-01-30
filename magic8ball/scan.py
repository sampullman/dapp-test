# Blockchain scanning methods and experiments

from .constants import *
import json

def make_result(timestamp, scanner, tx, question, answer, status):
    return {"timestamp": timestamp, "scanner_id": scanner.id, "event_id": tx['hash'],
                    "data": json.dumps({"asker": tx['from'], "question": question,
                                         "answer": answer, 'status': status})}

class BlockIter:
    def __init__(self, web3, _from, _to):
        self.web3 = web3
        self._from = _from
        self._to = _to

    def __iter__(self):
        return self

    def __next__(self):
        block = None
        while not block:
            if self._from <= self._to:
                block = self.web3.eth.getBlock(self._from)
                self._from += 1
                return block
            else:
                raise StopIteration()

def scan_questions2(db, web3, scanner, to_block):
    contract_hash = scanner.contract_hash.lower()
    results = []

    for block in BlockIter(web3, scanner.next_block, to_block):

        for tx_hash in block.transactions:
            result = scan_question_tx(web3, scanner, block.number, block.timestamp, contract_hash, tx_hash)
            if result:
                results.append(result)

    scanner.next_block = to_block+1
    print("Scan2 to block {}".format(scanner.next_block))
    return results

def scan_questions3(db, web3, scanner, to_block):
    contract_hash = scanner.contract_hash.lower()
    results = []
    filter = web3.eth.filter({'fromBlock': scanner.next_block, 'toBlock': to_block, 'address': contract_hash})

    for data in filter.get_all_entries():
        block = web3.eth.getBlock(data['blockNumber'])
        result = scan_question_tx(web3, scanner, data['blockNumber'], block.timestamp,
                                    contract_hash, data['transactionHash'])
        if result:
            results.append(result)

    scanner.next_block = to_block+1
    return results

def scan_question_tx(web3, scanner, blockNumber, timestamp, contract_hash, tx_hash):
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    tx = web3.eth.getTransaction(tx_hash)
    if not tx.input.startswith(scanner.function):
        #print("{} {}".format(blockNumber, "Wrong function!"))
        return None
    
    if (not tx) or (len(tx.input) <= 138):
        print("{} {} {}".format(blockNumber, "This is not the transaction you're looking for.", len(tx.input)))
        return None
    question = bytearray.fromhex(tx.input[138:]).decode().strip('\x00')
    #print(tx_hash)

    if not receipt:
        print("{} ".format(blockNumber)+"Transaction pending (this should never occur): "+tx_hash)
        return make_result(timestamp, scanner, tx, question, "", PENDING)
        return None
    status = receipt['status']
    if not (status == 1 or status == "0x1"):
        #print("{} Failed {}: {}".format(blockNumber, receipt['status'], question))
        return make_result(timestamp, scanner, tx, question, "", FAILED)
    if receipt['to'] == contract_hash:
        if len(receipt['logs']) == 0:
            print("{} ".format(blockNumber)+"No logs")
            return None
        data = receipt['logs'][0]['data']
        if len(data) < 130:
            print("{} ".format(blockNumber)+"Invalid log length")
            return None
        answer = bytearray.fromhex(data[130:]).decode().strip('\x00')
        return make_result(timestamp, scanner, tx, question, answer, SUCCESS)
        #print("{} ".format(blockNumber)+"Question: {}\nanswer: {}".format(question, answer))
    print("{}\n{}\n\n".format(receipt['to'], contract_hash))
    return None

# TODO -- compare transaction retrieval time to:
#   web3.eth.getBlockTransactionCount
#   web3.eth.getTransactionFromBlock
# or
#   traditional filter/getFilterChanges methods
def scan_questions(db, web3, scanner, to_block):
    contract_hash = scanner.contract_hash.lower()
    results = []
    
    for block_num in range(scanner.next_block, to_block+1):
        block = web3.eth.getBlock(block_num)
        if not block:
            continue

        for tx_hash in block.transactions:
            result = scan_question_tx(web3, scanner, block.number, block.timestamp, contract_hash, tx_hash)
            if result:
                results.append(result)

    scanner.next_block = to_block+1
    print("Scanned to block {}".format(scanner.next_block))
    return results