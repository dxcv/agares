# @file new_extreme_strategy_demo.py
# @brief The new extreme strategy demo

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

class new_extreme_Strategy(Strategy):
    """ 
    The new extreme strategy on daily candlestick data.
    Buy an asset when close price rises above the highest price in last m days,
    and sell it when close price falls under the lowest price in last m days.
    """
    def __init__(self, name, m):
	super(new_extreme_Strategy, self).__init__(name)
	self.m = m

    @staticmethod
    def ExtremePrice(close, m):
	"""
	    Return highest and lowest prices of the last m timeunit.
	    Note that both return variables (highest and lowest) start 
	    from the (m+1)-th timeunit. The first m-th timeunit are np.nan
	    Return:
		highest(np.ndarray)
		lowest(np.ndarray)
	"""
	window = []
	highest = np.zeros(len(close)) 
	lowest = np.zeros(len(close)) 
	for i, price in enumerate(close):
	    if i < m: 
		highest[i], lowest[i] = np.nan, np.nan # skip m timeunit.
		window.append(close[i])		
		continue 
	    # note that both highest and lowest start from the (m+1)-th timeunit
	    # the first m-th timeunit are np.nan
	    highest[i] = np.max(window)
	    lowest[i] = np.min(window)
	    window.pop(0)
	    window.append(close[i])
	return highest, lowest


    # the variable name 'cst' is short for 'candlestick'
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

	# ExtremePrice
	highest, lowest = self.ExtremePrice(close_1day, self.m)
	df_extreme = pd.DataFrame({'close': close_1day, 'highest': highest, 'lowest': lowest}, 
				index = datetime_1day)

	# skip extra data
	df_extreme = df_extreme.iloc[actual_ahead:]
	close_1day = close_1day[actual_ahead:]

	#df_extreme.plot()
	#plt.show()
	hold_flag = 0
	for i, ticker in enumerate(df_extreme.index):
	    # skip null value at the beginning
	    if np.isnan(df_extreme.iloc[i]['highest']) or np.isnan(df_extreme.iloc[i]['lowest']):
		continue 
	    # start trading
	    price = float(close_1day[i])
	    if (hold_flag == 0) and (df_extreme.iloc[i]['close'] > df_extreme.iloc[i]['highest']): 
		# quantity is the number of shares (unit: boardlot) you buy this time 
		quantity = buy(price, str(ticker), ratio = 1) 
	        hold_flag = 1
	    if (hold_flag == 1) and (df_extreme.iloc[i]['close'] < df_extreme.iloc[i]['lowest']): 
		# sell all the shares bought last time
		sell(price, str(ticker), quantity) 
	        hold_flag = 0
	


if __name__ == '__main__':
    # list of candlestick data files, each item represents a period data of the interested stock
    # 'mp' refers to 'multiple period'
    mpstock = ['000001.sz-1Day']
    # create a trading strategy
    strategy = new_extreme_Strategy('The new extreme strategy no.1', 10)
    # set start and end datetime
    dt_start, dt_end = datetime(2005,1,1), datetime(2016,1,19)
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
