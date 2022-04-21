import numpy as np
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

CONTRACT_ADDRESS = "0xD7c51CD3cd29519Cf76bF26BDA0778E6D419dd36"
PRIVATE_KEY = "ddd014e5aaa5bf4700818844572c84bf7b51c5e8d8ca4c12b5b3a5e80cc51964"
res = "20028"
hashesToBeStored = f"hashesbc{res}.npy"
infura = "https://rinkeby.infura.io/v3/ffb90fe6270e42fa94c43ffe12198d3c"
with open("abi.json") as f:
    info_json = json.load(f)
CONTRACT_ABI = info_json["abi"]
PUBLIC_ADDRESS = "0x29787E9dBE17fa768aD62870e84b5fAd019c19c1"

hashes = np.load(hashesToBeStored, allow_pickle=True)
w3 = Web3(Web3.HTTPProvider(infura))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
nonce = w3.eth.getTransactionCount(PUBLIC_ADDRESS)
myContract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
transaction = {
    'gasPrice': w3.eth.gas_price * 100,
    'chainId': "0x4",
    "from": PUBLIC_ADDRESS,
    "nonce": nonce
}
batch_reg_tx = myContract.functions.addTransaction(113133156664212525236363636363365612521515551313, 414148155152525236363636363655536363636666665114814).buildTransaction(transaction)
signed_tx = w3.eth.account.sign_transaction(batch_reg_tx, PRIVATE_KEY)
send_stored_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_stored_tx)
print(tx_receipt)
