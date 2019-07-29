# -*- coding:utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
import requests
import json
from util import *
import time
import HuobiService

class CalTrian(object):
    def __init__(self):
        self.start_time = time.time()
        self.sum_usdt = 0
        self.sum_btc = 0
        self.last_usdt = 0
        self.last_btc = 0

        self.BTC_USDT = 1
        self.BTC_USDT_MIN_NUM = 0.000001
        self.EOS_USDT = 64
        self.EOS_USDT_MIN_NUM = 50.01
        self.EOS_BTC = 80
        self.EOS_BTC_MIN_NUM = 50.01

        self.sell_fee = 0.001
        self.buy_fee = 0.001

        self.btc_usdt_sell = 7285965
        self.btc_usdt_sell_num = 0
        self.btc_usdt_buy = 7281483
        self.btc_usdt_buy_num = 0

        self.eos_btc_sell = 0.00085978
        self.eos_btc_sell_num = 0
        self.eos_btc_buy =  0.00085553
        self.eos_btc_buy_num = 0

        self.eos_usdt_sell = 6291
        self.eos_usdt_sell_num = 0
        self.eos_usdt_buy = 6252
        self.eos_usdt_buy_num = 0
        self.session = requests.session()

        self.usdt_balance = 4000
        self.btc_balance = 0.0005
        self.eos_balance = 200

        # self.usdt_balance = 7000
        # self.btc_balance = 0.0008
        # self.eos_balance = 300

        self.usdt_real = 0
        self.btc_real = 0
        self.eos_real = 0

        self.min_profit = 0.001

        self.executor = ThreadPoolExecutor(3)
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'token': 'xxx',
        }


    def ticker(self, symbol):
        try:
            res = self.session.get('http://xxx.com/ticker?cy_id=' + str(symbol),timeout=1,headers=self.headers)
        except requests.exceptions.Timeout:
            print 'timeout'
            return False
        try:
            data = res.json()
        except:
            print 'parse json fail',symbol, res.content
            return False
        # print data
        # print symbol, data
        try:
            sell = data['data']['sell'][0]
            buy = data['data']['buy'][0]
            sell_price = float(sell['price'].replace(',', ''))
            sell_num = float(sell['left_num'].replace(',', ''))
            buy_price = float(buy['price'].replace(',', ''))
            buy_num = float(buy['left_num'].replace(',', ''))

            user_data = data['data']['user_data']['asset']
            # print user_data
        except:
            print 'index out of range'
            return False

        if symbol == self.BTC_USDT:
            self.btc_usdt_sell = sell_price
            self.btc_usdt_sell_num = sell_num
            self.btc_usdt_buy = buy_price
            self.btc_usdt_buy_num = buy_num
            self.usdt_real = user_data['currency_trade']['num']
        elif symbol == self.EOS_USDT:
            self.eos_usdt_sell = sell_price
            self.eos_usdt_sell_num = sell_num
            self.eos_usdt_buy = buy_price
            self.eos_usdt_buy_num = buy_num
            self.eos_real = user_data['currency']['num']
        elif symbol == self.EOS_BTC:
            self.eos_btc_sell = sell_price
            self.eos_btc_sell_num = sell_num
            self.eos_btc_buy = buy_price
            self.eos_btc_buy_num = buy_num
            self.btc_real = user_data['currency_trade']['num']
        return True


    # usdt->eos->btc->usdt
    #19.85 657.05
    # 2.544e-06 168.9
    # 7918996.0 0.30872
    def eos_btc_usdt_eos(self):
        res = 1 \
              * self.eos_btc_buy * (1 - self.sell_fee) \
              * self.btc_usdt_buy * (1 - self.sell_fee) \
              / self.eos_usdt_sell * (1 - self.buy_fee) \

        if res -1 > self.min_profit:
            print time.time(),'eos',res-1,self.eos_usdt_sell,self.eos_usdt_sell_num,self.eos_btc_buy,self.eos_btc_buy_num,self.btc_usdt_buy,self.btc_usdt_buy_num
            return True
        else:
            print time.time(),'###',res-1,self.eos_usdt_sell,self.eos_usdt_sell_num,self.eos_btc_buy,self.eos_btc_buy_num,self.btc_usdt_buy,self.btc_usdt_buy_num
            return False

    def eos_btc_usdt_eos_trans(self):
        eos_usdt_buy_num = get_max_multiple(min(self.eos_usdt_sell_num, self.eos_btc_buy_num / (1 - self.buy_fee), self.usdt_balance/self.eos_usdt_sell, self.eos_balance / (1 - self.buy_fee)), 10)
        eos_btc_sell_num = eos_usdt_buy_num * (1 - self.buy_fee)
        btc_usdt_sell_num = get_down_bound_x(eos_btc_sell_num * self.eos_btc_buy * (1 - self.buy_fee), 6)
        profit_usdt = (self.btc_usdt_buy * btc_usdt_sell_num) * (1 - self.sell_fee) - self.eos_usdt_sell * eos_usdt_buy_num
        profit_btc = (self.eos_btc_buy * eos_btc_sell_num) * (1 - self.buy_fee) - btc_usdt_sell_num

        if btc_usdt_sell_num > self.btc_usdt_buy:
            print 'other people btc not enough'
            return False
        elif profit_usdt <= 0:
            print 'profit usdt <= 0'
            return False
        elif eos_btc_sell_num < self.EOS_USDT_MIN_NUM:
            print 'eos trans num < ', self.EOS_USDT_MIN_NUM
            return False
        elif btc_usdt_sell_num < self.BTC_USDT_MIN_NUM:
            print 'btc trans num < ',self.BTC_USDT_MIN_NUM
            return False
        elif btc_usdt_sell_num > self.btc_balance:
            print 'btc balance not enough'
            return False

        result_iterators = self.executor.map(self.trade,
                                             [self.EOS_USDT, self.EOS_BTC, self.BTC_USDT],
                                             [self.eos_usdt_sell, self.eos_btc_buy, self.btc_usdt_buy],
                                             [eos_usdt_buy_num, eos_btc_sell_num, btc_usdt_sell_num],
                                             ['buy', 'sell', 'sell']
                                             )

        print 'profit usdt:', profit_usdt,'profit btc', profit_btc
        #
        if profit_usdt != self.last_usdt:
            self.sum_usdt += profit_usdt
            self.last_usdt = profit_usdt
        if profit_btc != self.last_btc:
            self.sum_btc += profit_btc
            self.last_btc = profit_btc
        print 'sum:', self.start_time, time.time(), self.sum_usdt, self.sum_btc, self.sum_usdt / (
                 time.time() - self.start_time) * 60
        #
        return True

    #eos 0.0118618955274
    # 7828684.0 0.204037
    # 2.672e-06 466.38
    # 21.23 742.62
    # usdt->btc->eos->usdt
    def eos_usdt_btc_eos(self):
        res = 1 \
              * self.eos_usdt_buy * (1 - self.sell_fee) \
              / self.btc_usdt_sell * (1 - self.buy_fee) \
              / self.eos_btc_sell * (1 - self.buy_fee) \
        #大于最小利润才开始套利
        if res - 1 > self.min_profit:
            print time.time(),'eos',res-1,self.btc_usdt_sell, self.btc_usdt_sell_num,self.eos_btc_sell,self.eos_btc_sell_num,self.eos_usdt_buy,self.eos_usdt_buy_num
            return True
        else:
            print time.time(),'###',res-1,self.btc_usdt_sell, self.btc_usdt_sell_num,self.eos_btc_sell,self.eos_btc_sell_num,self.eos_usdt_buy,self.eos_usdt_buy_num
            return False

    def eos_usdt_btc_eos_trans(self):


        # self.eos_btc_sell_num<=self.eos_usdt_buy_num
        # self.eos_btc_sell_num>self.eos_usdt_buy_num
        # self.eos_usdt_buy_num / (1 - self.buy_fee) > self.eos_btc_sell_num
        eos_btc_buy_num = get_max_multiple(min(self.eos_btc_sell_num, self.eos_usdt_buy_num / (1 - self.buy_fee), self.eos_balance / (1 - self.buy_fee), self.btc_balance / self.eos_btc_sell), 10)
        eos_usdt_sell_num = eos_btc_buy_num * (1 - self.buy_fee)
        btc_usdt_buy_num = get_up_bound_x(eos_btc_buy_num * self.eos_btc_sell / (1 - self.buy_fee), 6)

        profit_usdt = self.eos_usdt_buy * eos_usdt_sell_num * (1 - self.sell_fee) - self.btc_usdt_sell * btc_usdt_buy_num
        profit_btc = btc_usdt_buy_num * (1 - self.buy_fee) - self.eos_btc_sell * eos_btc_buy_num

        if btc_usdt_buy_num > self.btc_usdt_sell_num:
            print 'other peope btc not enough'
            return False
        elif profit_usdt <=0:
            print 'pfofit_usdt <=0'
            return False
        elif eos_usdt_sell_num < self.EOS_USDT_MIN_NUM:
            print 'eos num<', self.EOS_USDT_MIN_NUM
            return False
        elif btc_usdt_buy_num < self.BTC_USDT_MIN_NUM:
            print 'btc num<',self.BTC_USDT_MIN_NUM
            return False
        elif btc_usdt_buy_num > self.usdt_balance / self.btc_usdt_sell:
            print 'usdt not enough'
            return False

        result_iterators = self.executor.map(self.trade,
                                             [self.BTC_USDT, self.EOS_BTC, self.EOS_USDT, ],
                                             [self.btc_usdt_sell, self.eos_btc_sell, self.eos_usdt_buy],
                                             [btc_usdt_buy_num, eos_btc_buy_num, eos_usdt_sell_num],
                                             ['buy', 'buy', 'sell']
                                             )




        print 'profit usdt:', profit_usdt,'profit btc', profit_btc
        if profit_usdt != self.last_usdt:
            self.sum_usdt += profit_usdt
            self.last_usdt = profit_usdt
        if profit_btc != self.last_btc:
            self.sum_btc += profit_btc
            self.last_btc = profit_btc
        print 'sum:', self.start_time, time.time(), self.sum_usdt, self.sum_btc, self.sum_usdt / (
                 time.time() - self.start_time) * 60
        #
        return True

    def getdaata(self):
        result_iterators = self.executor.map(self.ticker, [self.BTC_USDT, self.EOS_USDT, self.EOS_BTC])
        res = True

        for result in result_iterators:
            if result == False:
                res = False
                break
        print 'balance', self.usdt_real, self.btc_real, self.eos_real
        if self.usdt_real < self.usdt_balance or self.btc_real < self.btc_balance or self.eos_real < self.eos_balance:
             print 'balance not enough'
             res = False
        return res

    def cal(self):
        if self.eos_btc_usdt_eos() == True:
            return self.eos_btc_usdt_eos_trans()
        elif self.eos_usdt_btc_eos() == True:
            return self.eos_usdt_btc_eos_trans()
        else:
            return False

    def trade(self, symbol, price, num, type):

        post_data = {
            "cy_id": symbol,
            "price": price,
            "num": num,
            "google_pwd":"",
            "trade_pwd": "098765",
            "type": type
        }

        print time.time(),'to post'
        res = self.session.post("https://xxx.com/trade/do", data = post_data, timeout=3, headers=self.headers)
        print time.time(),json.dumps(post_data),res.content


c = CalTrian()

while True:
    try:
        res = c.getdaata()
    except:
        print 'connect error'
        continue
    if res == True:
        res = c.cal()
        if res == True:
            print 'success'
            time.sleep(3)
    else:
        print 'request fail'



