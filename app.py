"""
Streamlit Frontend - Stock Market Finance Application
Main application entry point.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="Stock Market Finance App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def fetch_api(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make API request to backend."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            return {"error": "Invalid method"}
        
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 204:
            return {"success": True}
        else:
            return {"error": response.json().get("detail", "API Error")}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend API. Make sure the server is running."}
    except Exception as e:
        return {"error": str(e)}


def main():
    """Main application."""
    st.title("📈 Stock Market Finance Application")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Stock Management", "Price History", "Projections", "Settings"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Stock Management":
        show_stock_management()
    elif page == "Price History":
        show_price_history()
    elif page == "Projections":
        show_projections()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    """Display main dashboard."""
    st.header("Dashboard")
    
    # Get all stocks
    stocks = fetch_api("/stocks/")
    
    if "error" in stocks:
        st.error(stocks["error"])
        st.info("Make sure the backend API is running on http://localhost:8000")
        return
    
    if not stocks:
        st.info("No stocks in database. Add some stocks from the Stock Management page.")
        return
    
    # Display stock cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Stocks", len(stocks))
    
    # Get sectors count
    sectors = set(s.get("sector") for s in stocks if s.get("sector"))
    with col2:
        st.metric("Sectors", len(sectors))
    
    # Active stocks
    active_stocks = [s for s in stocks if s.get("is_active")]
    with col3:
        st.metric("Active Stocks", len(active_stocks))
    
    st.divider()
    
    # Stock list
    st.subheader("Your Stocks")
    
    df = pd.DataFrame(stocks)
    if not df.empty:
        display_cols = ["symbol", "name", "sector", "industry", "exchange", "is_active"]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)


def show_stock_management():
    """Stock management page."""
    st.header("Stock Management")
    
    tab1, tab2, tab3 = st.tabs(["Add Stock", "View Stocks", "Fetch Prices"])
    
    with tab1:
        st.subheader("Add New Stock")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Quick Add (Fetch from Yahoo Finance)")
            symbol = st.text_input("Stock Symbol", placeholder="e.g., AAPL, GOOGL, MSFT")
            
            if st.button("Fetch & Add Stock", type="primary"):
                if symbol:
                    with st.spinner(f"Fetching {symbol.upper()}..."):
                        result = fetch_api(f"/stocks/fetch/{symbol.upper()}", method="POST")
                        
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"Added {result['symbol']} - {result['name']}")
                else:
                    st.warning("Please enter a stock symbol")
        
        with col2:
            st.markdown("### Manual Add")
            with st.form("add_stock_form"):
                m_symbol = st.text_input("Symbol")
                m_name = st.text_input("Company Name")
                m_sector = st.text_input("Sector (optional)")
                m_industry = st.text_input("Industry (optional)")
                m_exchange = st.text_input("Exchange (optional)")
                
                if st.form_submit_button("Add Stock"):
                    if m_symbol and m_name:
                        data = {
                            "symbol": m_symbol.upper(),
                            "name": m_name,
                            "sector": m_sector or None,
                            "industry": m_industry or None,
                            "exchange": m_exchange or None,
                        }
                        result = fetch_api("/stocks/", method="POST", data=data)
                        
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"Added {result['symbol']} - {result['name']}")
                    else:
                        st.warning("Symbol and Name are required")
    
    with tab2:
        st.subheader("Your Stocks")
        
        stocks = fetch_api("/stocks/")
        
        if "error" in stocks:
            st.error(stocks["error"])
        elif not stocks:
            st.info("No stocks found. Add some stocks first!")
        else:
            for stock in stocks:
                with st.expander(f"{stock['symbol']} - {stock['name']}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Sector:** {stock.get('sector', 'N/A')}")
                        st.write(f"**Industry:** {stock.get('industry', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Exchange:** {stock.get('exchange', 'N/A')}")
                        st.write(f"**Active:** {'Yes' if stock.get('is_active') else 'No'}")
                    
                    with col3:
                        if st.button("Delete", key=f"delete_{stock['id']}"):
                            result = fetch_api(f"/stocks/{stock['id']}", method="DELETE")
                            if "error" not in result:
                                st.success("Deleted!")
                                st.rerun()
    
    with tab3:
        st.subheader("Fetch Historical Prices")
        
        stocks = fetch_api("/stocks/")
        
        if "error" in stocks:
            st.error(stocks["error"])
        elif not stocks:
            st.info("No stocks found. Add some stocks first!")
        else:
            stock_options = {f"{s['symbol']} - {s['name']}": s['symbol'] for s in stocks}
            selected = st.selectbox("Select Stock", list(stock_options.keys()))
            
            col1, col2 = st.columns(2)
            
            with col1:
                period = st.selectbox(
                    "Period",
                    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                    index=0
                )
            
            with col2:
                use_dates = st.checkbox("Use custom date range")
            
            start_date = None
            end_date = None
            
            if use_dates:
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
                with col2:
                    end_date = st.date_input("End Date", datetime.now())
            
            if st.button("Fetch Prices", type="primary"):
                symbol = stock_options[selected]
                
                data = {"symbol": symbol, "period": period}
                if use_dates:
                    data["start_date"] = start_date.isoformat()
                    data["end_date"] = end_date.isoformat()
                
                with st.spinner(f"Fetching prices for {symbol}..."):
                    result = fetch_api("/prices/fetch", method="POST", data=data)
                    
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"Fetched {result['total_fetched']} prices, {result['new_records']} new records added.")


def show_price_history():
    """Price history page."""
    st.header("Price History")
    
    stocks = fetch_api("/stocks/")
    
    if "error" in stocks:
        st.error(stocks["error"])
        return
    
    if not stocks:
        st.info("No stocks found. Add some stocks first!")
        return
    
    # Stock selector
    stock_options = {f"{s['symbol']} - {s['name']}": s for s in stocks}
    selected = st.selectbox("Select Stock", list(stock_options.keys()))
    stock = stock_options[selected]
    
    # Date range
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=90))
    
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    with col3:
        limit = st.number_input("Max Records", min_value=10, max_value=1000, value=200)
    
    # Fetch prices
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "limit": limit,
    }
    
    prices = fetch_api(f"/prices/{stock['id']}", data=params)
    
    if "error" in prices:
        st.error(prices["error"])
        return
    
    if not prices:
        st.warning("No price data found. Fetch historical prices from Stock Management.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(prices)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Display stats
    st.subheader("Statistics")
    
    stats = fetch_api(f"/prices/{stock['id']}/stats")
    
    if "error" not in stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Min Price", f"${stats.get('min_price', 0):.2f}")
        with col2:
            st.metric("Max Price", f"${stats.get('max_price', 0):.2f}")
        with col3:
            st.metric("Avg Price", f"${stats.get('avg_price', 0):.2f}")
        with col4:
            st.metric("Total Records", stats.get('total_records', 0))
    
    # Candlestick chart
    st.subheader("Price Chart")
    
    chart_type = st.radio("Chart Type", ["Candlestick", "Line"], horizontal=True)
    
    if chart_type == "Candlestick":
        fig = go.Figure(data=[go.Candlestick(
            x=df['date'],
            open=df['open_price'],
            high=df['high_price'],
            low=df['low_price'],
            close=df['close_price'],
            name=stock['symbol']
        )])
    else:
        fig = px.line(df, x='date', y='close_price', title=f"{stock['symbol']} Closing Price")
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=500,
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Volume chart
    st.subheader("Trading Volume")
    
    fig_volume = px.bar(df, x='date', y='volume')
    fig_volume.update_layout(height=300)
    st.plotly_chart(fig_volume, use_container_width=True)
    
    # Raw data
    with st.expander("View Raw Data"):
        st.dataframe(df, use_container_width=True)


def show_projections():
    """Projections page."""
    st.header("Stock Projections & Analysis")
    
    stocks = fetch_api("/stocks/")
    
    if "error" in stocks:
        st.error(stocks["error"])
        return
    
    if not stocks:
        st.info("No stocks found. Add some stocks first!")
        return
    
    # Stock selector
    stock_options = {f"{s['symbol']} - {s['name']}": s for s in stocks}
    selected = st.selectbox("Select Stock", list(stock_options.keys()))
    stock = stock_options[selected]
    
    tab1, tab2, tab3 = st.tabs(["Price Projection", "Moving Average", "Volatility"])
    
    with tab1:
        st.subheader("Price Projection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            days_ahead = st.slider("Days to Project", 7, 90, 30)
        
        with col2:
            lookback = st.slider("Historical Days for Trend", 30, 365, 90)
        
        if st.button("Calculate Projection", key="proj_btn"):
            params = {"days_ahead": days_ahead, "lookback_days": lookback}
            projection = fetch_api(f"/prices/{stock['id']}/projection", data=params)
            
            if "error" in projection:
                st.error(projection["error"])
            else:
                # Display projection info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Last Price", f"${projection['last_price']:.2f}")
                with col2:
                    trend = projection['trend']
                    st.metric("Trend", trend.capitalize(), delta="📈" if trend == "bullish" else "📉")
                with col3:
                    st.metric("Daily Change", f"${projection['daily_change_rate']:.4f}")
                
                st.write(f"**R-squared:** {projection['r_squared']:.4f} (higher = more reliable trend)")
                
                # Projection chart
                proj_df = pd.DataFrame(projection['projections'])
                proj_df['date'] = pd.to_datetime(proj_df['date'])
                
                # Get historical prices for context
                hist_prices = fetch_api(f"/prices/{stock['id']}", data={"limit": lookback})
                
                if not isinstance(hist_prices, list):
                    hist_prices = []
                
                fig = go.Figure()
                
                if hist_prices:
                    hist_df = pd.DataFrame(hist_prices)
                    hist_df['date'] = pd.to_datetime(hist_df['date'])
                    hist_df = hist_df.sort_values('date')
                    
                    fig.add_trace(go.Scatter(
                        x=hist_df['date'],
                        y=hist_df['close_price'],
                        mode='lines',
                        name='Historical',
                        line=dict(color='blue')
                    ))
                
                fig.add_trace(go.Scatter(
                    x=proj_df['date'],
                    y=proj_df['projected_price'],
                    mode='lines',
                    name='Projected',
                    line=dict(color='orange', dash='dash')
                ))
                
                fig.update_layout(
                    title=f"{stock['symbol']} Price Projection",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=500,
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Moving Average Analysis")
        
        window = st.slider("Moving Average Window (days)", 5, 100, 20)
        
        if st.button("Calculate Moving Average", key="ma_btn"):
            ma_data = fetch_api(f"/prices/{stock['id']}/moving-average", data={"window": window})
            
            if "error" in ma_data:
                st.error(ma_data["error"])
            elif isinstance(ma_data, list) and ma_data:
                df = pd.DataFrame(ma_data)
                df['date'] = pd.to_datetime(df['date'])
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['close_price'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='blue')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['moving_average'],
                    mode='lines',
                    name=f'{window}-day MA',
                    line=dict(color='orange')
                ))
                
                fig.update_layout(
                    title=f"{stock['symbol']} Moving Average",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=500,
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for moving average calculation")
    
    with tab3:
        st.subheader("Volatility Analysis")
        
        vol_lookback = st.slider("Analysis Period (days)", 7, 180, 30)
        
        if st.button("Calculate Volatility", key="vol_btn"):
            volatility = fetch_api(f"/prices/{stock['id']}/volatility", data={"lookback_days": vol_lookback})
            
            if "error" in volatility:
                st.error(volatility["error"])
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Annualized Volatility", f"{volatility['volatility']:.2f}%")
                    st.metric("Average Daily Return", f"{volatility['avg_daily_return']:.4f}%")
                
                with col2:
                    st.metric("Price Range", f"{volatility['price_range_pct']:.2f}%")
                    st.metric("Min/Max", f"${volatility['min_price']:.2f} - ${volatility['max_price']:.2f}")


def show_settings():
    """Settings page."""
    st.header("Settings")
    
    st.info("API Configuration")
    st.code(f"Backend URL: {API_BASE_URL}")
    
    # Health check
    st.subheader("System Status")
    
    if st.button("Check API Health"):
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                st.success("✅ Backend API is running")
            else:
                st.error("❌ Backend API returned an error")
        except:
            st.error("❌ Cannot connect to Backend API")


if __name__ == "__main__":
    main()
