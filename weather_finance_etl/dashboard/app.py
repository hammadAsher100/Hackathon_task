import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration with better theme
st.set_page_config(
    page_title="Weather & Finance Analytics Dashboard",
    page_icon="🌤️📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
    }
    
    .subheader {
        font-size: 1.8rem;
        color: #2c3e50;
        border-left: 5px solid #3498db;
        padding-left: 15px;
        margin: 2rem 0 1rem 0;
    }
    
    /* Card styling */
    .metric-card {
        background: #042e4b;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border: 1px solid #e1e8ed;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0px 0px;
        gap: 1rem;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API clients (same as before)
@st.cache_resource
def get_weather_client():
    try:
        from api_client.openweathermap_client import OpenWeatherClient
        return OpenWeatherClient()
    except:
        return None

@st.cache_resource
def get_finance_client():
    try:
        from api_client.alphavantage_client import AlphaVantageClient
        return AlphaVantageClient()
    except:
        return None

# Enhanced weather visualization
def plot_weather_dashboard(weather_df, city):
    if weather_df is None or weather_df.empty:
        return
    
    # Header with city info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<h3 style="text-align: center;">🌍 Current Weather in {city}</h3>', unsafe_allow_html=True)
    
    # Main metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp = weather_df['temp_c'].iloc[0]
        st.markdown(f'''
        <div class="metric-card">
            <h4>🌡️ Temperature</h4>
            <h2>{temp:.1f}°C</h2>
            <p>Feels like: {weather_df['feels_like_c'].iloc[0]:.1f}°C</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        humidity = weather_df['humidity'].iloc[0]
        st.markdown(f'''
        <div class="metric-card">
            <h4>💧 Humidity</h4>
            <h2>{humidity}%</h2>
            <p>Comfort level: {"Comfortable" if humidity < 70 else "High"}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        pressure = weather_df['pressure'].iloc[0]
        st.markdown(f'''
        <div class="metric-card">
            <h4>📊 Pressure</h4>
            <h2>{pressure} hPa</h2>
            <p>{"Normal" if 1010 < pressure < 1020 else "Check conditions"}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        wind_speed = weather_df['wind_speed'].iloc[0]
        st.markdown(f'''
        <div class="metric-card">
            <h4>💨 Wind Speed</h4>
            <h2>{wind_speed} m/s</h2>
            <p>{ "Calm" if wind_speed < 3 else "Breezy" if wind_speed < 7 else "Windy"}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Weather condition with emoji
    condition = weather_df['description'].iloc[0].title()
    emoji_map = {
        'clear': '☀️', 'cloud': '☁️', 'rain': '🌧️', 'snow': '❄️',
        'thunderstorm': '⛈️', 'drizzle': '🌦️', 'mist': '🌫️'
    }
    emoji = '🌈'
    for key, value in emoji_map.items():
        if key in condition.lower():
            emoji = value
            break
    
    st.markdown(f'''
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); 
                border-radius: 15px; margin: 20px 0; color: white;">
        <h1 style="margin: 0; font-size: 4rem;">{emoji}</h1>
        <h3 style="margin: 10px 0;">{condition}</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Interactive gauges
    st.markdown('<div class="subheader">Detailed Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Temperature gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=temp,
            title={'text': "Temperature (°C)"},
            delta={'reference': 20},
            gauge={
                'axis': {'range': [-10, 40]},
                'bar': {'color': "#e74c3c"},
                'steps': [
                    {'range': [-10, 0], 'color': "#3498db"},
                    {'range': [0, 15], 'color': "#2ecc71"},
                    {'range': [15, 25], 'color': "#f1c40f"},
                    {'range': [25, 40], 'color': "#e74c3c"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Humidity gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=humidity,
            title={'text': "Humidity (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 30], 'color': "#f1c40f"},
                    {'range': [30, 70], 'color': "#2ecc71"},
                    {'range': [70, 100], 'color': "#e74c3c"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Wind speed gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=wind_speed,
            title={'text': "Wind Speed (m/s)"},
            gauge={
                'axis': {'range': [0, 20]},
                'bar': {'color': "#9b59b6"},
                'steps': [
                    {'range': [0, 5], 'color': "#2ecc71"},
                    {'range': [5, 15], 'color': "#f1c40f"},
                    {'range': [15, 20], 'color': "#e74c3c"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# Enhanced finance visualization
def plot_finance_dashboard(finance_df, symbol):
    if finance_df is None or finance_df.empty:
        return
    
    # Header with stock info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<h3 style="text-align: center;">💹 {symbol} Stock Analysis</h3>', unsafe_allow_html=True)
    
    # Calculate metrics
    latest = finance_df.iloc[-1]
    if len(finance_df) > 1:
        previous = finance_df.iloc[-2]
        price_change = latest['close'] - previous['close']
        percent_change = (price_change / previous['close']) * 100
    else:
        price_change = 0
        percent_change = 0
    
    # Main metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        change_color = "green" if price_change >= 0 else "red"
        change_emoji = "📈" if price_change >= 0 else "📉"
        st.markdown(f'''
        <div class="metric-card">
            <h4>{change_emoji} Current Price</h4>
            <h2 style="color: {change_color};">${latest['close']:.2f}</h2>
            <p style="color: {change_color};">{price_change:+.2f} ({percent_change:+.2f}%)</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h4>🔓 Open</h4>
            <h3>${latest['open']:.2f}</h3>
            <p>Day range: ${latest['low']:.2f} - ${latest['high']:.2f}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h4>📊 Volume</h4>
            <h3>{latest['volume']:,}</h3>
            <p>Shares traded</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        avg_volume = finance_df['volume'].mean()
        st.markdown(f'''
        <div class="metric-card">
            <h4>📈 Avg Volume</h4>
            <h3>{avg_volume:,.0f}</h3>
            <p>30-day average</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Interactive charts in tabs
    st.markdown('<div class="subheader">Technical Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Candlestick", "📈 Trend Analysis", "📉 Performance", "ℹ️ Statistics"])
    
    with tab1:
        # Enhanced candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=finance_df['datetime'],
            open=finance_df['open'],
            high=finance_df['high'],
            low=finance_df['low'],
            close=finance_df['close'],
            name=symbol,
            increasing_line_color='#2ecc71',
            decreasing_line_color='#e74c3c'
        )])
        
        fig.update_layout(
            title=f"{symbol} - Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
            height=500,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Trend analysis with moving averages
        df = finance_df.sort_values('datetime').copy()
        df['MA_7'] = df['close'].rolling(window=7).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()
        df['MA_50'] = df['close'].rolling(window=50).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['close'], name='Close Price', 
                               line=dict(color='#3498db', width=3)))
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['MA_7'], name='7-Day MA', 
                               line=dict(color='#e74c3c', width=2, dash='dot')))
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['MA_20'], name='20-Day MA', 
                               line=dict(color='#2ecc71', width=2, dash='dash')))
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['MA_50'], name='50-Day MA', 
                               line=dict(color='#f39c12', width=2, dash='dashdot')))
        
        fig.update_layout(
            title=f"{symbol} - Price Trend with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Returns distribution
            df['daily_return'] = df['close'].pct_change() * 100
            returns = df['daily_return'].dropna()
            
            fig = px.histogram(returns, nbins=30, 
                             title="Daily Returns Distribution",
                             color_discrete_sequence=['#3498db'])
            fig.update_layout(
                xaxis_title="Daily Return (%)",
                yaxis_title="Frequency",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cumulative returns
            df['cumulative_return'] = (1 + df['daily_return']/100).cumprod()
            fig = px.area(df, x='datetime', y='cumulative_return',
                         title="Cumulative Returns",
                         color_discrete_sequence=['#2ecc71'])
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Cumulative Return",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Statistics table
        st.markdown("**Key Statistics**")
        stats_data = {
            'Metric': ['Current Price', '30-Day High', '30-Day Low', 'Average Volume', 
                      'Volatility (Std Dev)', 'Sharpe Ratio*', 'Total Return*'],
            'Value': [f"${latest['close']:.2f}", 
                     f"${finance_df['high'].max():.2f}",
                     f"${finance_df['low'].min():.2f}",
                     f"{finance_df['volume'].mean():,.0f}",
                     f"{returns.std():.2f}%",
                     f"{(returns.mean()/returns.std()):.2f}",
                     f"{((df['cumulative_return'].iloc[-1] - 1) * 100):.2f}%"]
        }
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
        st.caption("*Based on available data period")

# Main application with enhanced sidebar
def main():
    # Header
    st.markdown('<h1 class="main-header">🌤️📈 Weather & Finance Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 20px; color: white;">
            <h2>🚀 Dashboard</h2>
            <p>Real-time Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Navigation")
        app_mode = st.radio("Choose Dashboard", 
                           ["🏠 Overview", "🌤️ Weather", "📈 Finance", "📊 Combined View"],
                           label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        # Quick actions
        if st.button("🔄 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #7f8c8d;">
            <p>Built with ❤️ using Streamlit</p>
            <p>Data from OpenWeather & Alpha Vantage</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content based on selection
    if app_mode == "🏠 Overview":
        show_overview()
    elif app_mode == "🌤️ Weather":
        show_weather_dashboard()
    elif app_mode == "📈 Finance":
        show_finance_dashboard()
    else:
        show_combined_view()

def show_overview():
    st.markdown('<div class="subheader">Welcome to Your Analytics Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🌤️ Weather Analytics</h3>
            <p>• Real-time weather data</p>
            <p>• Global city coverage</p>
            <p>• Interactive gauges</p>
            <p>• Multi-parameter analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Finance Analytics</h3>
            <p>• Stock market data</p>
            <p>• Technical indicators</p>
            <p>• Candlestick charts</p>
            <p>• Performance metrics</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick start section
    st.markdown('<div class="subheader">🚀 Quick Start</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Get Weather Data:**
        1. Go to Weather tab
        2. Enter city name
        3. Click 'Get Weather Data'
        4. View interactive charts
        """)
    
    with col2:
        st.info("""
        **Get Stock Data:**
        1. Go to Finance tab  
        2. Enter stock symbol
        3. Choose time interval
        4. Click 'Get Stock Data'
        5. Analyze performance
        """)

# Add your existing show_weather_dashboard(), show_finance_dashboard(), and show_combined_view() functions here
# (Keep the data fetching logic from your previous version)

def show_weather_dashboard():
    st.markdown('<div class="subheader">Weather Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 Search Parameters")
        city = st.text_input("🌍 City Name", "London", key="weather_city")
        country = st.text_input("🇺🇸 Country Code (optional)", "GB", key="weather_country")
        
        if st.button("🌤️ Get Weather Data", type="primary", use_container_width=True):
            # Your existing weather data fetching logic here
            pass
    
    with col2:
        if 'weather_data' in st.session_state:
            plot_weather_dashboard(st.session_state.weather_data, st.session_state.weather_city)

def show_finance_dashboard():
    st.markdown('<div class="subheader">Finance Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 Search Parameters")
        symbol = st.text_input("💹 Stock Symbol", "AAPL", key="finance_symbol").upper()
        interval = st.selectbox("⏰ Time Interval", ["Daily", "Intraday"], key="finance_interval")
        
        if st.button("📈 Get Stock Data", type="primary", use_container_width=True):
            # Your existing finance data fetching logic here
            pass
    
    with col2:
        if 'finance_data' in st.session_state:
            plot_finance_dashboard(st.session_state.finance_data, st.session_state.finance_symbol)

def show_combined_view():
    st.markdown('<div class="subheader">Combined Analytics View</div>', unsafe_allow_html=True)
    
    # Your existing combined view logic here
    pass

if __name__ == "__main__":
    main()