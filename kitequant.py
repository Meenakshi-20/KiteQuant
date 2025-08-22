# kitequant.py
import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

plt.style.use('ggplot')  # Makes graphs!

# STRATEGY
class GoldenCross(bt.Strategy):
    params = (
        ('fast', 20),  # Short-term trend
        ('slow', 50),  # Long-term trend
        ('risk_pct', 0.95)  # Use 95% of money
    )
    
    def __init__(self):
        # Like Zerodha's moving average tools
        self.fast_line = bt.indicators.SMA(period=self.p.fast, plotname='20-Day Trend')
        self.slow_line = bt.indicators.SMA(period=self.p.slow, plotname='50-Day Trend')
        self.buy_signal = bt.indicators.CrossOver(self.fast_line, self.slow_line, plotname='Buy/Sell Signal')
        
        # Track trades like Console's P&L
        self.trade_count = 0
        self.profit = 0
        
    def next(self):
        if not self.position:  # No active trade
            if self.buy_signal > 0:  # Green light!
                cash_to_use = self.broker.getcash() * self.p.risk_pct
                self.buy(size=cash_to_use / self.data.close[0])
                
        elif self.buy_signal < 0:  # Red light!
            self.close()  # Square off like in Kite
    
    def notify_trade(self, trade):
        # Show profit/loss per trade
        self.trade_count += 1
        self.profit += trade.pnlcomm
        print(f"Trade {self.trade_count}: ₹{trade.pnlcomm:.2f} ({'Profit' if trade.pnlcomm >=0 else 'Loss'})")

# VISUAL TWEAKS
def add_teen_explanations(fig):
    # Add teen-friendly explanations to each axis
    for i, ax in enumerate(fig.axes):
        ax.text(0.02, 0.98, "HOW TO READ THIS:", 
                transform=ax.transAxes, fontsize=10, weight='bold',
                verticalalignment='top', bbox=dict(facecolor='gold', alpha=0.5))
        
        tips = [
            "GREEN candles = Price went UP",
            "RED candles = Price went DOWN",
            "Blue line = 20-Day Trend",
            "Orange line = 50-Day Trend",
            "UP arrows = BUY signals",
            "DOWN arrows = SELL signals"
        ]
        
        for j, tip in enumerate(tips):
            ax.text(0.02, 0.90 - (j*0.05), tip, 
                   transform=ax.transAxes, fontsize=8,
                   verticalalignment='top')
    return fig

# DATA & RUN
def get_stock_data(ticker):
    df = yf.download(ticker, '2023-01-01', datetime.now().strftime('%Y-%m-%d'))
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    return df

def run_kitequant():
    print("\n" + "KITEQUANT FOR TEENS".center(50, '-'))
    print("(Like Zerodha, but simpler!)\n")
    
    cerebro = bt.Cerebro(stdstats=False)  # Remove clutter
    
    # 1. Load data (try your favorite stock!)
    stock_data = get_stock_data('RELIANCE.NS')  # Change to TATASTEEL.NS or INFY.NS
    data = bt.feeds.PandasData(dataname=stock_data)
    cerebro.adddata(data)
    
    # 2. Add strategy
    cerebro.addstrategy(GoldenCross)
    
    # 3. Paper trading with ₹50,000 (like Zerodha's virtual money)
    cerebro.broker.setcash(50000)
    cerebro.broker.setcommission(commission=0.001)  # Zerodha's charges
    
    # 4. Run!
    print(f"Starting with: ₹{cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    strat = results[0]
    print(f"Ending with: ₹{cerebro.broker.getvalue():,.2f}")
    print(f"Total Profit: ₹{strat.profit:,.2f} from {strat.trade_count} trades")
    
    # 5. Plot with our custom explanations
    fig = cerebro.plot(style='candlestick', barup='#5dba00', bardown='#ff3d3d', 
                       subtxtsize=8, plotdist=0.1, baralpha=0.7)[0][0]
    fig = add_teen_explanations(fig)
    
if __name__ == '__main__':
    run_kitequant()
