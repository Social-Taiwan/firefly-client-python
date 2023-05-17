from config import TEST_ACCT_KEY, TEST_NETWORK
from firefly_exchange_client import FireflyClient, Networks, MARKET_SYMBOLS, ORDER_SIDE, ORDER_TYPE, OrderSignatureRequest, GetOrderbookRequest
import asyncio
import numpy as np
import time

# customer define
spread = 10
warning_free_collateral = 100

async def place_limit_order(client: FireflyClient, price,symbol, side, qty):
    # default leverage of account is set to 3 on firefly
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)

    # creates a LIMIT order to be signed
    signature_request = OrderSignatureRequest(
        symbol=symbol,  # market symbol
        price=price,  # price at which you want to place order
        quantity=qty, # quantity
        side=side, 
        orderType=ORDER_TYPE.LIMIT,
        leverage=user_leverage
    )  

    # create signed order
    signed_order = client.create_signed_order(signature_request);

    print("Placing a limit order")
    # place signed order on orderbook
    resp = await client.post_signed_order(signed_order)

    # returned order with PENDING state
    print(resp)

    return

async def main():
    # initialize client
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY, # private key of wallet
        )

    await client.init(True) 

    # add market that you wish to trade on ETH/BTC are supported currently
    client.add_market(MARKET_SYMBOLS.ETH)

    
    
    while True: 
        # cancel original orders
        await client.cancel_all_open_orders(MARKET_SYMBOLS.ETH)
        
        # check user balance
        balances = await client.get_user_account_data()
        freeCollateral = np.float64(balances["freeCollateral"])
        if freeCollateral < warning_free_collateral:
            # error handle
            print()
            
        # get price and calculate mid price
        orderbook = await client.get_orderbook(GetOrderbookRequest(
            symbol = MARKET_SYMBOLS.ETH,
            limit = 1
        ))
        
        bid = np.float64(orderbook["bestBidPrice"])/1e18
        ask = np.float64(orderbook["bestAskPrice"])/1e18
        mid = (bid + ask) / 2
        
         # place limit order
        await place_limit_order(client,np.ceil(mid+spread/2), MARKET_SYMBOLS.ETH, ORDER_SIDE.SELL, 0.01)
        await place_limit_order(client,np.floor(mid-spread/2), MARKET_SYMBOLS.ETH, ORDER_SIDE.BUY, 0.01)
        
        time.sleep(10)

if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())