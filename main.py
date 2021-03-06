import pandas as pd
import pandas_ta as pta
import datetime 

capital_per_trade = 50000

watchlist = {'HCLTECH','TECHM','SBILIFE','ASIANPAINT','WIPRO','ITC','INFY','TCS','RELIANCE','CIPLA','JSWSTEEL','HEROMOTOCO','NESTLEIND','HINDUNILVR','SHREECEM','BHARTIARTL','HDFCBANK','BRITANNIA','ICICIBANK','HDFCLIFE','TITAN','HINDALCO','BAJAJ-AUTO','DIVISLAB','SUNPHARMA','TATAMOTORS','UPL','TATASTEEL','BAJFINANCE','LT','SBIN','INDUSINDBK','TATACONSUM','COALINDIA','MARUTI','BPCL','ULTRACEMCO','HDFC','ADANIPORTS','DRREDDY','POWERGRID','BAJAJFINSV','AXISBANK','KOTAKBANK','IOC','M&M','ONGC','EICHERMOT','NTPC','GRASIM'}

path = r"C:\Users\omkin\OneDrive\Documents\Algo Trading"
status = {'name': None, 'date': None, 'time': None, 'entry_price': None, 'stoploss': None, 'target': None, 'pnl': None, 'exit_time': None, 'traded': None, 'buysell': None, 'qty': None}
final_result = {}
trade_no = 0
for name in watchlist:
    df15 = pd.read_csv(path + '\\' + '15min' + '\\' + name + '.csv')
    df15.set_index(pd.DatetimeIndex(df15["date"]), inplace=True)
    df15['vwap'] = pta.vwap(df15['high'], df15['low'], df15['close'], df15['volume'])
    # STOCHRSIk_14_14_3_3 is blue 
    # STOCHRSId_14_14_3_3 is red
    df16= pta.stochrsi(df15['close'])
    df15 = pd.concat([df15, df16], axis=1)

    #First 20 to drop in case of 15 min.
    df15 = df15['2021-12-27 14:15:00+05:30':]

    for index,row in df15.iterrows():
        #Buy
        if (row['STOCHRSIk_14_14_3_3'] > row['STOCHRSId_14_14_3_3']) and (row['low'] < row['vwap'] < row['high']) and status['traded'] is None:
            trade_no = trade_no + 1
            status['name'] = name
            status['date'] = index.date()
            status['time'] = index.time()
            status['entry_price'] = round((row['close'])*0.005,2)/0.005
            status['stoploss'] = round((row['close']*0.99)*0.005,2)/0.005
            status['target'] = round((row['close']*1.02)*0.005,2)/0.005
            status['traded'] = 'yes'
            status['buysell'] = 'buy'
            status['qty'] = int(capital_per_trade/status['entry_price'])
        #Sell
        if (row['STOCHRSIk_14_14_3_3'] < row['STOCHRSId_14_14_3_3']) and (row['low'] < row['vwap'] < row['high']) and status['traded'] is None:
            trade_no = trade_no + 1
            status['name'] = name
            status['date'] = index.date()
            status['time'] = index.time()
            status['entry_price'] = row['close']
            status['stoploss'] = round((row['close']*1.01)*0.005,2)/0.005
            status['target'] = round((row['close']*0.98)*0.005,2)/0.005
            status['traded'] = 'yes'
            status['buysell'] = 'sell'
            status['qty'] = int(capital_per_trade/status['entry_price'])
        #Stoploss    
        if status['traded'] == 'yes':
            market_over = index.time() >= datetime.time(15,25)
            
            if (status['buysell'] == 'buy') and ((row['low'] < status['stoploss']) or (row['high'] > status['target']) or market_over):
                if (row['low'] < status['stoploss']):
                    status['pnl'] = (status['stoploss'] - status['entry_price'])* status['qty']
                if (row['high'] > status['target']):
                    status['pnl'] = (status['target'] - status['entry_price'])* status['qty']
                if market_over:
                    status['pnl'] = (row['close'] - status['entry_price'])* status['qty']
                status['exit_time'] = index.time()
                status = {'name': None, 'date': None, 'time': None, 'entry_price': None, 'stoploss': None, 'target': None, 'pnl': None, 'exit_time': None, 'traded': None, 'buysell': None, 'qty': None}
                final_result[trade_no] = status
            if (status['buysell'] == 'sell') and ((row['high'] > status['stoploss']) or (row['low'] < status['target']) or market_over):
                if (row['high'] > status['stoploss']):
                    status['pnl'] = (status['entry_price'] - status['stoploss'])* status['qty']
                if (row['low'] < status['target']):
                    status['pnl'] = (status['entry_price'] - status['target'])* status['qty']
                if market_over:
                    status['pnl'] = (status['entry_price'] - row['close'])* status['qty']
                status['exit_time'] = index.time()
                status = {'name': None, 'date': None, 'time': None, 'entry_price': None, 'stoploss': None, 'target': None, 'pnl': None, 'exit_time': None, 'traded': None, 'buysell': None, 'qty': None}
                final_result[trade_no] = status
                
                
results = pd.DataFrame(final_result).T
results.to_csv(path + '\\' + 'final' + '.csv')            
