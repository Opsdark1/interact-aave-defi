from brownie import config, network, accounts, interface
from web3 import Web3
from scripts.get_weth import get_account, get_weth, LIST

AMOUNT = Web3.toWei(0.1, "ether")

def main():
    account = get_account()

    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in LIST:
        get_weth()

    pool = get_pool()

    approve_erc20(AMOUNT, pool.address, erc20_address, account)
    
    print("Depositing")
    transaction = pool.deposit(erc20_address, AMOUNT, account.address, 0, {"from": account, 'gas': 100000, 'allow_revert': True})
    transaction.wait(1)
    print("Deposited")
    
    borrowable_eth, total_debth = get_borrowable_data(pool, account)
    
    link_eth_price = get_asset_price(config["networks"][network.show_active()]["link_eth_pricefeed"])
    print(f"The LINK/ETH price is {link_eth_price}")
    
    amount_link_to_borrow = (1/link_eth_price) * (borrowable_eth * 0.95)
    borrowable_transaction = pool.borrow(config["networks"][network.show_active()]["link_token"], Web3.toWei(amount_link_to_borrow, "ether"), 1, 0, account.address, {"from": account})
    borrowable_transaction.wait(1)
    print("LINK borrowed")

    repay_all(amount_link_to_borrow, pool, account)
    
    print("You just deposted LINK in aave")

def get_pool():
    pool_addresses_provider= interface.IPoolAddressesProvider(config["networks"][network.show_active()]["pool_addresses"])
    pool_addresses = pool_addresses_provider.getPool()

    pool = interface.IPool(pool_addresses)
    return pool

def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20")
    erc20 = interface.IERC20(erc20_address)
    transaction = erc20.approve(spender, amount, {"from": account})
    transaction.wait(1)
    print("Approved")
    return transaction

def get_borrowable_data(pool, account):
    (totalCollateralBase, totalDebtBase, availableBorrowsBase, currentLiquidationThreshold, ltv, healthFactor) = pool.getUserAccountData(account.address) 
    totalCollateralBase = Web3.fromWei(totalCollateralBase, "ether")
    totalDebtBase = Web3.fromWei(totalDebtBase, "ether")
    availableBorrowsBase = Web3.fromWei(availableBorrowsBase, "ether")

    print(f"You have a collateral of: {totalCollateralBase}")
    print(f"You have a debt of: {totalDebtBase}")
    print(f"You have a available borrows of: {availableBorrowsBase}")
    
    return(float(availableBorrowsBase), float(totalDebtBase))


def get_asset_price(price_feed_address):
    link_eth_price_feed = interface.AggregatirV3Interface(price_feed_address)
    latest_price = link_eth_price_feed.latestRoundData()[1]

    converter = Web3.fromWei(latest_price, "ether")
    return float(converter)

def repay_all(amount, pool, account):
    approve_erc20(Web3.toWei(amount, "ether"), pool, config["networks"][network.show_active()]["link_token"], account)
    repay_transaction = pool.repay(config["networks"][network.show_active()]["link_token"], amount, 1, account.address, {"from": account})
    repay_transaction.wait(1)
    return repay_transaction