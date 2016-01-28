# @file ma_strategy_demo.py
# @brief The simplest moving average (MA) strategy demo

import ipdb
from datetime import datetime
from agares.engine.ag import (
	Strategy,
	create_trading_system,
	run,
	buy,
	sell,
	report)
from talib import (MA, MACD)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class MA_Strategy(Strategy):
    """ 
    The simplest moving average (MA) strategy
    Buy an asset when the 10-timeunit moving average of its price rises above 
    its 20-timeunit average, and sell it vice versa.
    """
    def __init__(self, name, nfast, nslow):
	super(MA_Strategy, self).__init__(name)
	self.nfast = nfast
	self.nslow = nslow


    def compute_trading_points(self, cst, actual_ahead):
	"""
	Args:
            cst(pd.DataFrame): The variable name 'cst' is short for 'candlestick'
            actual_ahead(int): Number of extra daily data. We add extra daily data 
                        (before start date) for computing indexes such as MA, MACD. 
			These may help to avoid nan at the beginning of indexes.
			It can be set at the main program (var: n_ahead). However, 
			it would be smaller than you set because of lack of data.
			That's why we use a different variable name from that of main
			program.
	"""
	df_1day = cst['1Day']
	datetime_1day = df_1day.index
	close_1day = df_1day['close'].values

	# Moving average
	maf = MA(close_1day, self.nfast)
	mas = MA(close_1day, self.nslow)
	df_ma = pd.DataFrame({'ma_fast': maf, 'ma_slow': mas}, 
				index = datetime_1day)

	# skip extra data
	df_ma = df_ma.iloc[actual_ahead:]
	close_1day = close_1day[actual_ahead:]

	#df_ma.plot()
	#plt.show()
	start_flag = 0
	hold_flag = 0
	for i, ticker in enumerate(df_ma.index):
	    # skip null value at the beginning
	    if np.isnan(df_ma.iloc[i]['ma_fast']) or np.isnan(df_ma.iloc[i]['ma_slow']):
		continue 
	    # skip the days of 'ma_fast'>='ma_slow' at the beginning
	    # those should be the days waiting fo selling, not buying, thus not suitable for a start
	    if (start_flag == 0) and (df_ma.iloc[i]['ma_fast'] <= df_ma.iloc[i]['ma_slow']):
		continue
	    else:
		start_flag = 1
	    # start trading
	    if (start_flag == 1):
		price = float(close_1day[i])
		if (hold_flag == 0) and (df_ma.iloc[i]['ma_fast'] > df_ma.iloc[i]['ma_slow']): 
		    # quantity is the number of shares (unit: boardlot) you buy this time 
		    quantity = buy(price, str(ticker), ratio = 1) 
		    hold_flag = 1
		if (hold_flag == 1) and (df_ma.iloc[i]['ma_fast'] < df_ma.iloc[i]['ma_slow']): 
		    # sell all the shares bought last time
		    sell(price, str(ticker), quantity) 
		    hold_flag = 0
	


if __name__ == '__main__':
    # list of candlestick data files, each item represents a period data of the interested stock
    # 'mp' refers to 'multiple period'
    mpstock = ['000001.sz-1Day']
    # create a trading strategy
    strategy = MA_Strategy('Simple MA strategy no.1', 10, 20)
    # set start and end datetime
    dt_start, dt_end = datetime(1997,1,1), datetime(2016,1,27)
    # number of extra daily data for computation (ahead of start datatime)
    n_ahead = 40
    # settings of a trading system
    # capital:        Initial money for investment
    # StampTaxRate:   Usually 0.001. Only charge when sell.
    #                 The program do not consider the fact that buying funds do not charge this tax.  
    #                 So set it to 0 if the 'mpstock' is a fund.
    # CommissionChargeRate:   Usually 2.5e-4. The fact that commission charge is at least 5 yuan has
    #                         been considered in the program.
    settings = {'capital': 1000000, 'StampTaxRate': 0.00, 'CommissionChargeRate': 2.5e-4}
    # create a trading system
    create_trading_system(strategy, mpstock, dt_start, dt_end, n_ahead, settings)
    # start back testing
    run()
    # report performance of the trading system
    report(ReturnEquity = False)
