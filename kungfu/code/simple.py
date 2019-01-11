#coding:utf-8

import json
import numpy as np
import pandas as pa
import tushare as ts
import talib as ta

from utils.useful import hash_object

STOCK_LIST = ['000001']

bar_log_file ='bar.log'
tick_log_file ='tick.log'

g_context  = None
def print_line(text,fp=None):
    text = str(text)
    if fp:
        fp.write(text+'\n')
        fp.flush()
    print text

def initialize(context):
    global g_context
    g_context = context

    context.add_md(source=SOURCE.XTP)
    context.add_td(source=SOURCE.XTP)
    context.subscribe(tickers=STOCK_LIST, source=SOURCE.XTP)
    context.register_bar(source=SOURCE.XTP, min_interval=1, start_time='09:30:00', end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=5, start_time='09:30:00',  end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=15, start_time='09:30:00',  end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=30, start_time='09:30:00',  end_time='15:00:00')
    context.register_bar(source=SOURCE.XTP, min_interval=60, start_time='09:30:00',  end_time='15:00:00')
    context.trade = True
    context.barlog = open(bar_log_file,'a+')
    context.ticklog = open(tick_log_file,'a+')

def on_pos(context, pos_handler, request_id, source, rcv_time):
    print '--'.center(20,'*')
    # context.log_info(pos_handler)
    print pos_handler.get_tickers()
    print '-- xxx -- '
    if(request_id == -1) and(pos_handler is None):
        context.set_pos(context.new_pos(SOURCE.XTP), SOURCE.XTP)
    else:
        context.log_info("[RSP_POS] {}".format(pos_handler.dump()))

    context.current_pos = pos_handler
    context.stop()


def query_amount():
    """查询资金余额"""
    return g_context.current_pos

def query_pos(code):
    """查询合约持仓"""
    return 0

def save_bar_data(code,bar,interval):
    # 非交易时间段丢弃
    f = open('{}-{}.txt'.format(code,interval),'a+')
    data = json.dumps(hash_object(bar))
    f.write(data+'\n')
    f.close()

def get_bars(code,interval,range=100):
    """
    当天的k线不够则从tushare中获取
    :param code: 股票代码
    :param interval: k线类型
    :param bar_num:  k线数量
    :return:
    """
    bars = []
    f = open('{}-{}.txt'.format(code, interval))
    lines = filter(lambda _:_ and _[0]!='#', map(str.strip,f.readlines()) )
    lines = lines[::-1]
    f.close()
    lines = map(lambda _:json.loads(_),lines)
    lines = map(lambda _:_['Close'],lines)
    close = np.array(lines)

    # df = ts.get_hist_data(code, ktype='5')
    # close2 = df.close.values
    # close = np.append(close,close2)

    return close

def get_yesterday_close_price(code):
    return 0

def get_current_price(code):
    return 0


def buy(code,num):
    """买入下单"""
    pass

def sell(code,num):
    """卖出下单"""
    pass


def strategy_ma(bar ):
    """计算均线策略"""
    close = get_bars('000001', 5)
    print close
    nbar = 5
    ma5 = ta.MA(close, nbar)
    ma5_s = ma5[nbar - 1]
    print ma5_s

    nbar = 10
    ma10 = ta.MA(close, nbar)
    ma10_e = ma5[nbar - 1]
    print ma10_e


def strategy_inday(code,num = 100 ,limit=0.02 ):
    """日内涨跌幅策略
    @:param code: 股票代码
    @:param num ：买卖数量
    @:param limit: 价格浮动限
    """
    zf =  get_current_price(code) / get_yesterday_close_price(code) - 1
    if zf <= -limit:
        #跌幅过限
        amount = query_amount()
        pos_sum = query_pos(code)
        if get_current_price(code) *pos_sum <= amount * 0.1:
            """持仓资金占总资金 <= 10% """
            buy(code,num)
    elif zf >= limit:
        if query_pos(code) >= num:
            sell(code,num)


def on_bar_5(context, bars, intervals,source, rcv_time):


    # save_bar_data(bar_data) # 1,5,15
    bar_num = 10
    for code,bar in bars.items():
        # if int(intervals) == 15:
        save_bar_data(code,bar ,intervals   )


        # print_line( code + ' '+ str(hash_object(bar)) ,context.barlog)
        # if bar == 15:
        #     bars_1 = get_before_n_bar15_from_tushare(code)
        #     bars_2 = get_today_n_bar15_from_kungfu()
        #     bars = bars_1+bars_2
        """
            ma5 = talib.ma(bars,5)
            ma10 = talib.ma(bars,10)

            ma5_pre = talib.ma(bars-1, 5)
            ma10_pre = talib.ma(bars-1, 10)

            if ma5 >= ma10 and ma5_pre < ma10_pre:
                money = query_amount()
                num = 100
                if current_price('000001') * num('000001') <= money*10% :
                    buy(code,num)
            else if ma5 <= ma10 and ma5_pre > ma10_pre:
                num = 100
                if query_pos(code) >= num:
                    sell(code, num)
        
        """

"""
def on_bar(context, bars, intervals,source, rcv_time):
    print '>>on_bar()', bars, intervals,source, rcv_time
    print_line( ' bars info  '.center(40, '=') ,context.barlog)

    save_bar_data(bar_data) # 1,5,15
    bar_num = 10
    for code,bar in bars.items():
        print_line( code + ' '+ str(hash_object(bar)) ,context.barlog)
        if bar == 15:
            bars_1 = get_before_n_bar15_from_tushare(code)
            bars_2 = get_today_n_bar15_from_kungfu()
            bars = bars_1+bars_2
            ma5 = talib.ma(bars,5)
            ma10 = talib.ma(bars,10)

            ma5_pre = talib.ma(bars-1, 5)
            ma10_pre = talib.ma(bars-1, 10)

            if ma5 >= ma10 and ma5_pre < ma10_pre:
                money = query_amount()
                num = 100
                if current_price('000001') * num('000001') <= money*10% :
                    buy(code,num)
            else if ma5 <= ma10 and ma5_pre > ma10_pre:
                num = 100
                if query_pos(code) >= num:
                    sell(code, num)


def on_bar2(context, bars, intervals,source, rcv_time):
    print '>>on_bar()', bars, intervals,source, rcv_time
    print_line( ' bars info  '.center(40, '=') ,context.barlog)

    save_bar_data(bar_data) # 1,5,15
    bar_num = 10

    # times 1 min
    zf = current_price(code ) / yesterday_close_price(code) -1 # 涨幅

    for code,bar in bars.items():
        if bar == 1:
            if zf <= -0.02:
                money = query_amount()
                num = 100
                if current_price(code) * num(code) <= money*10% :
                    buy(code,num)

            else if zf >= 0.02:
                num = 100
                if query_pos(code) >= num:
                    sell(code, num)

"""

def on_error(context, error_id, error_msg, order_id, source, rcv_time):
    context.log_error("[ERROR] (err_id){} (err_msg){} (order_id){} (source){}".format(error_id, error_msg, order_id, source))


def on_tick(context, md, source, rcv_time):
    return
    print '>>on_tick()' , md,source,rcv_time
    print_line( ' md info (Ticks) '.center(40,'=') ,context.ticklog)
    print_line( hash_object(md) ,context.ticklog)
    if context.trade:
        last_price = md.LastPrice

        # rid = context.insert_limit_order(source=SOURCE.XTP,
        #                                  ticker=md.InstrumentID,
        #                                  exchange_id=EXCHANGE.SZE,
        #                                  price=last_price,
        #                                  volume=100,
        #                                  direction=DIRECTION.Buy,
        #                                  offset=OFFSET.Open)
        context.trade = False
    else:
        print 'to stop()..'
        # context.stop()

def on_rtn_order(context, rtn_order, order_id, source, rcv_time):
    context.log_info("on_rtn_order|order_id:{}|stock:{}|trade:{}|left:{}|status:{}".format(order_id, rtn_order.InstrumentID, rtn_order.VolumeTraded, rtn_order.VolumeTotal, rtn_order.OrderStatus))


def on_rtn_trade(context, rtn_trade, order_id, source, rcv_time):
    context.log_info("on_rtn_trade|order_id:{}|stock:{}|price:{}|volume:{}".format(order_id,rtn_trade.InstrumentID,rtn_trade.Price,rtn_trade.Volume))
