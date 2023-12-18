from brownie import config, network, accounts, interface
from web3 import Web3

LIST= ["development", "ganache-local", "mainnet-fork", "mainnet-fork-dev"]

def get_account(id=None, index=None):

    if id:
        return accounts.load(id)

    if index:
        return accounts[index]

    if network.show_active() in LIST:
        return accounts[0]

    return accounts.add(config["wallets"]["form_key"])

def get_weth():
    account = get_account()
    weth = interface.IWETH(config["networks"][network.show_active()]["weth_token"])
    transaction = weth.deposit({"from": account, "value": Web3.toWei(0.1, "ether")})
    transaction.wait(1)
    print("Recieved 0.1 WETH")
    return transaction

def main():
    get_weth()