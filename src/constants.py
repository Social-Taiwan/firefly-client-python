Networks = {
  "TESTNET": {
    "url": "https://bobabase.boba.network/",
    "chainId": 1297,
    "apiGateway": "https://dapi-testnet.firefly.exchange",
    "socketURL": "wss://dapi-testnet.firefly.exchange",
    "onboardingUrl": "https://testnet.firefly.exchange",
  },
  "DEV": {
    "url": "https://l2-dev.firefly.exchange/",
    "chainId": 78602,
    "apiGateway": "https://dapi-dev.firefly.exchange",
    "socketURL": "wss://dapi-dev.firefly.exchange/",
    "onboardingUrl": "https://dev.firefly.exchange",
  },
}

EIP712_DOMAIN_NAME = "Orders";

EIP712_DOMAIN_VERSION = "1.0"

EIP712_DOMAIN_STRING = "EIP712Domain(string name,string version,uint128 chainId,address verifyingContract)"


EIP712_ORDER_STRUCT_STRING = \
    "Order(" +  \
    "bytes32 flags," + \
    "uint128 quantity," + \
    "uint128 price," + \
    "uint128 triggerPrice," + \
    "uint128 leverage," + \
    "address maker," + \
    "address taker," + \
    "uint128 expiration" + \
    ")"

ORDER_FLAGS = {
    "IS_BUY":1,
    "IS_DECREASE_ONLY": 2
}
