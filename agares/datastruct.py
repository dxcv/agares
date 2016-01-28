from agares.errors import PeriodTypeError

class StockInfo(object):
    """ 
    StockInfo

    :ivar code: stock code
    :ivar name: stock name
    """
    def __init__(self, str_stock):
        info = str_stock.split('.')
        if len(info) == 2:
            self.code = info[0]
            self.name = info[1] 
        else:
            assert False

    def __str__(self):
        return "%s.%s" % (self.code, self.name)


class PeriodInfo(object):
    """ PeriodInfo """
    periods = ["1Minute", "5Minute", "30Minute", "60Minute", 
			"1Day", "1Week", "1Month"]    

    def __init__(self, str_period):
        if str_period not in self.periods:
            raise PeriodTypeError
        self._type = str_period

    @property
    def type(self):
        """
        Unit of time
        """
        return self._type

    def __str__(self):
	return "%s" % self._type


class PStockInfo(object):
    """ 
    stock with period information
    """
    def __init__(self, pstock):
        t = pstock.split('-')
	if len(t) == 2:
            self.stock = StockInfo(t[0])
            self.period = PeriodInfo(t[1])
        else:
            assert False

    def __str__(self):
        """ return string like '510300.300etf-1Minute'  """
        return "%s-%s" % (self.stock, self.period)



