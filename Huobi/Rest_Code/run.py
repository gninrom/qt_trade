#_*_coding:utf8_*_
from HuobiUtil import *
import HuobiService
import json

if __name__=='__main__':
    print "get user accout info"
    print HuobiService.get_accounts() 
    res =  HuobiService.get_balance(4844796)
    #data = res.json()
    #print res["data"]["list"]
    print HuobiService.get_depth("btcusdt","step0")
    print HuobiService.get_depth("eosusdt","step0")
    print HuobiService.get_depth("eosbtc","step0")
