import plotly.graph_objects as go
import pandas as pd

def plot_stock(df, symbol):
    # Filter data for the specific symbol
    symbol_df = df[df['Symbol'] == symbol].copy()
    
    # Sort by datetime to ensure correct order
    symbol_df = symbol_df.sort_values('Datetime')
    
    # Set datetime as index for the candlestick chart
    symbol_df = symbol_df.set_index('Datetime')
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=symbol_df.index,
        open=symbol_df["Open"],
        high=symbol_df["High"],
        low=symbol_df["Low"],
        close=symbol_df["Close"],
        name=symbol
    ))
    
    fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )
    
    return fig