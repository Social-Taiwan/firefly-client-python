import os,sys
import time

from zmq import Socket
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(script_dir, "./src")))
sys.path.append(os.path.abspath(os.path.join(script_dir, "./src/classes")))

from web3 import Web3
from order_signer import OrderSigner
from firefly_client import FireflyClient
from sockets import Sockets
from order_signer import OrderSigner
from constants import *
from utils import *
from interfaces import *
from enums import *

# ordersAddress = "0x8C6eDe33D167D416b32eDd568C3578B0deF9bB8D"
ordersAddress = "0xF232c48a40ECFd927787FF3bDbAD4BB7B801b683"
private_key = "d7f7c1d3f9e48a2cec15127d0c7b1b07cd0689ed93813c61ec2b993312f5c3d3"
userAddress = "0xD4d1B6Ad2F00B7f2992bd27be6B444ca8e3c0cE4"

def post_order_test(client:FireflyClient,params:dict):
    signature_request = OrderSignatureRequest(
        symbol= params["symbol"], 
        price= params["price"], 
        quantity= params["quantity"], 
        side= params["side"], 
        orderType=params["order_type"],
        leverage= params["leverage"],
        expiration= params["expiration"] if "expiration" in params.keys() else int(time.time()+(30*24*60*60)),
        reduceOnly= params["reduce_only"],
        salt= params["salt"] if "salt" in params.keys() else random.randint(1,100000000)
    )  
    print(signature_request)
    signed_order = client.create_signed_order(signature_request)
    print(signed_order)
    order_request = PlaceOrderRequest(
        signed_order, 
        postOnly=params["post_only"] if "post_only" in params.keys() else True)
    resp = client.post_signed_order(order_request)
    return resp

def post_cancel_order_test(client:FireflyClient,order):
    signer:OrderSigner = client.get_order_signer(order["symbol"])
    order_to_sign = client.create_order_to_sign(order)
    hash = signer.get_order_hash(order_to_sign)
    cancel_req = client.create_signed_cancel_orders(order["symbol"],hash)
    resp = client.post_cancel_order(cancel_req)
    return resp


def test_getters_with_symbol(client:FireflyClient,symbol:MARKET_SYMBOLS):
    resp = client.get_market_meta_info(symbol)
    print(resp)
    resp = client.get_exchange_info(symbol)
    print(resp)
    resp = client.get_market_data(symbol)
    print(resp)
    req = GetMarketRecentTradesRequest(symbol=symbol,pageSize=10)
    resp = client.get_market_recent_trades(params=req)
    print(resp)
    req = GetCandleStickRequest(symbol=symbol, interval=Interval._1m)
    resp = client.get_market_candle_stick_data(req)
    print(resp['data'])
    

def test_user_getters(client:FireflyClient):
    # Get user account data
    print("account:",client.get_user_account_data())
    
    # get address
    print(client.get_public_address())

    # get user user Trades
    req = GetUserTradesRequest(
        symbol= MARKET_SYMBOLS.ETH,
        maker= True,
        fromId= 0,
        startTime=(time.time()-(5*24*60*60))*1000,
        endTime= time.time()*1000,
        pageSize= 10,
        pageNumber= 1,
        type= ORDER_TYPE.LIMIT,
    )
    print(client.get_user_trades(req))
    
    # get user position 
    req = GetPositionRequest(
        symbol=MARKET_SYMBOLS.ETH
    )
    print(client.get_user_position(req))

    # get user default leverage
    print(client.get_user_default_leverage(MARKET_SYMBOLS.ETH))
    req = GetOrderRequest(
        symbol=MARKET_SYMBOLS.ETH
    )
    print(client.get_orders(req))
    req = GetTransactionHistoryRequest(
        symbol=MARKET_SYMBOLS.ETH
    )
    print(client.get_transaction_history(req))
    

    
    return 

def test_orderhash_to_cancel():
    ordersAddress = "0x1578dD5561A67081b2136f19f61F2c72D1ca8756"
    private_key = "6f2ad7a2fde3ee1da954a5910a0a33c4115b24edf052d0612264e45bdaf12437"
    userAddress = "0x7daf02a2F521De45a357ee1E0804497683E981A8"

    data = "0x643ece6bae58380874dcbced70500e7c50d962f998ce71b17f89b34b936c7b08" # the input
    cancel_hash_ts = "0x691022cb4f3e200ccf54cff9d71e7eec22a692ec029713014cbd6285539f31f1" # the cancel hash
    hashSig_ts = "0x8b4678989c6ac698be6aa4f79a7c6cb402013729811f93224ada4f3f3d36002d010aff3164d26b55d72382c11782aa0ea855e080972e8b182dabba1c17c9dbf61c01" # the hashSig
    
    signer = OrderSigner(78602,ordersAddress)
    cancel_hash_py = signer.sign_cancellation_hash([data])
    if cancel_hash_py == cancel_hash_ts:
        print("cancel hash matched") 
    else:
        print("cancel hash didnt matched")
    hashSig = signer.sign_hash(cancel_hash_py,"6f2ad7a2fde3ee1da954a5910a0a33c4115b24edf052d0612264e45bdaf12437")
    print(hashSig)
    if hashSig == hashSig_ts:
        print("hashSig matched") 
    else:
        print("hashSig didnt matched")
    
def place_and_cancel_order_test():
    client = FireflyClient(
        True,
        Networks["TESTNET"], 
        private_key,
        True
        )
    print("init")
    client.add_market(MARKET_SYMBOLS.ETH, ordersAddress)
    print("add market")
    order_req = {
        "symbol":MARKET_SYMBOLS.ETH, 
        "price":790, 
        "quantity":0.1, 
        "side":ORDER_SIDE.BUY, 
        "order_type":ORDER_TYPE.LIMIT,
        "leverage":3,
        "expiration":int(time.time()+(30*24*60*60)),
        "reduce_only":False,
        "salt":10,
        "post_only":True
    }
    print("order_req:",order_req)
    resp = post_order_test(client,order_req)
    print("place order resp:",resp)
    order_req["orderType"] = order_req["order_type"]
    order_req["reduceOnly"] = order_req["reduce_only"]
    print("cancel order req:",order_req)
    resp = post_cancel_order_test(client,order_req)
    print("cancel order resp:",resp)
    return 

def main():
    callback = lambda x:print(x)
    # socket = Sockets(url=Networks["DEV"]["apiGateway"])
    private_key = "6f2ad7a2fde3ee1da954a5910a0a33c4115b24edf052d0612264e45bdaf12437"
    client = FireflyClient(True,Networks["DEV"],private_key,True)
    print(client.socket.connection_established)
    client.socket.listen("default",callback)
    client.socket.subscribe_global_updates_by_symbol(MARKET_SYMBOLS.BTC)
    time.sleep(60)
    client.socket.unsubscribe_global_updates_by_symbol(MARKET_SYMBOLS.BTC)
    print("unsubs")
    time.sleep(60)
    print("disconnect")
    client.socket.disconnect()
    return 

if __name__ == "__main__":
    main()