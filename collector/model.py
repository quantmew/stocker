def initialize(context):
    set_params()        
    set_variables()     
    set_backtest()         
def set_params():
    g.security = '600704.XSHG'
    g.benchmark='000300.XSHG'
    g.short_in_date =35
    g.long_in_date = 35
    g.short_out_date = 20
    g.long_out_date = 20
    g.dollars_per_share = 1
    g.loss = 0.1
    g.adjust = 0.8
    g.number_days = 15
    g.unit_limit = 4
    g.ratio = 0.8
def set_variables():
    g.unit = 1000
    g.N = []
    g.days = 0
    g.break_price1 = 0
    g.break_price2 = 0
    g.sys1 = 0
    g.sys2 = 0
    g.last_volume = None
    g.system1 = True
def set_backtest():
    set_benchmark(g.benchmark)
    set_option('use_real_price',True) 
    log.set_level('order','error') 
def before_trading_start(context):
    set_slip_fee(context) 
def set_slip_fee(context):
    set_slippage(FixedSlippage(0)) 
    dt=context.current_dt
    if dt>datetime.datetime(2013,1, 1):
        set_commission(PerTrade(buy_cost=0.0003, sell_cost=0.0013, min_cost=5)) 
        
    elif dt>datetime.datetime(2011,1, 1):
        set_commission(PerTrade(buy_cost=0.001, sell_cost=0.002, min_cost=5))
    elif dt>datetime.datetime(2009,1, 1):
        set_commission(PerTrade(buy_cost=0.002, sell_cost=0.003, min_cost=5))
    else:
        set_commission(PerTrade(buy_cost=0.003, sell_cost=0.004, min_cost=5))
def handle_data(context, data):
    dt = context.current_dt
    current_price = data[g.security].price
    if g.last_volume is None:
        g.last_volume = data[g.security].volume
    if dt.hour==9 :
        g.days += 1
        calculate_N() 
    if g.days > g.number_days:
        value = context.portfolio.portfolio_value
        cash = context.portfolio.cash 
        if g.sys1 == 0 and g.sys2 == 0:
            if value < (1-g.loss)*context.portfolio.starting_cash:
                cash *= g.adjust
                value *= g.adjust
        dollar_volatility = g.dollars_per_share*(g.N)[-1]
        g.unit = value*0.01/dollar_volatility      
        g.system1 = True
        
        if data[g.security].volume - g.last_volume < 0:
            pass # do something
        if g.sys1 == 0:
            market_in(current_price, g.ratio*cash, g.short_in_date)
        else:
            stop_loss(current_price)
            market_add(current_price, g.ratio*cash, g.short_in_date)    
            market_out(current_price, g.short_out_date)
        g.system1 == False
        if g.sys2==0:
            market_in(current_price, (1-g.ratio)*cash, g.long_in_date)
        else:
            stop_loss(current_price)
            market_add(current_price, (1-g.ratio)*cash, g.long_in_date)
            market_out(current_price, g.long_out_date)   
  def calculate_N():
    if g.days <= g.number_days:
        price = attribute_history(g.security, g.days, '1d',('high','low','pre_close'))
        lst = []
        for i in range(0, g.days):
            h_l = price['high'][i]-price['low'][i]
            h_c = price['high'][i]-price['pre_close'][i]
            c_l = price['pre_close'][i]-price['low'][i]
            True_Range = max(h_l, h_c, c_l)
            lst.append(True_Range)
        current_N = np.mean(np.array(lst))
        (g.N).append(current_N)
    else:
        price = attribute_history(g.security, 1, '1d',('high','low','pre_close'))
        h_l = price['high'][0]-price['low'][0]
        h_c = price['high'][0]-price['pre_close'][0]
        c_l = price['pre_close'][0]-price['low'][0]
        True_Range = max(h_l, h_c, c_l)
        current_N = (True_Range + (g.number_days-1)*(g.N)[-1])/g.number_days
        (g.N).append(current_N)
def market_in(current_price, cash, in_date):
    # Get the price for the past "in_date" days
    price = attribute_history(g.security, in_date, '1d', ('close'))
    # Build position if current price is higher than highest in past
    if current_price > max(price['close']):
        num_of_shares = cash/current_price
        if num_of_shares >= g.unit:
            print ("买入")
            print (current_price)
            print (max(price['close']))
            if g.system1 == True:
                if g.sys1 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys1 += int(g.unit)
                    g.break_price1 = current_price
            else:
                if g.sys2 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys2 += int(g.unit)
                    g.break_price2 = current_price
def market_add(current_price, cash, in_date):
    if g.system1 == True:
        break_price=g.break_price1
    else:
        break_price=g.break_price2
    if current_price >= break_price + 0.5*(g.N)[-1]: 
        num_of_shares = cash/current_price
        if num_of_shares >= g.unit: 
            print ("加仓")
            print (g.sys1)
            print (g.sys2)
            print (current_price)
            print (break_price + 0.5*(g.N)[-1])
            if g.system1 == True:
                if g.sys1 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys1 += int(g.unit)
                    g.break_price1 = current_price
            else:
                if g.sys2 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys2 += int(g.unit)
                    g.break_price2 = current_price
def market_out(current_price, out_date):
    price = attribute_history(g.security, out_date, '1d', ('close'))
    if current_price < min(price['close']):
        print ("离场")
        print (current_price)
        print (min(price['close']))
        if g.system1 == True:
            if g.sys1>0:
                order(g.security, -g.sys1)
                g.sys1 = 0
        else:
            if g.sys2>0:
                order(g.security, -g.sys2)
                g.sys2 = 0


def stop_loss(current_price):
    if g.system1 == True:
        break_price = g.break_price1
    else:
        break_price = g.break_price2
    if current_price < (break_price - 2*(g.N)[-1]):
        print ("止损")
        print (current_price)
        print (break_price - 2*(g.N)[-1])
        if g.system1 == True:
            order(g.security, -g.sys1)
            g.sys1 = 0  
        else:
            order(g.security, -g.sys2)
            g.sys2 = 0

