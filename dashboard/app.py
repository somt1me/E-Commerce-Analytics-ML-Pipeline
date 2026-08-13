import os
import sqlite3
import requests
import pandas as pd
import streamlit as st

# ------------------------------------------------------------------
# Streamlit Page Configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics & ML Dashboard 2026",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join("database", "ecommerce.db")
API_URL = "http://127.0.0.1:8000/predict"


# ------------------------------------------------------------------
# Helper Function to Retrieve Data from SQLite
# ------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_db_data(query: str) -> pd.DataFrame:
    """Đọc dữ liệu từ SQLite CSDL"""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ------------------------------------------------------------------
# Sidebar Navigation
# ------------------------------------------------------------------
st.sidebar.title("🛒 Navigation")
app_mode = st.sidebar.radio(
    "Select Function:",
    ["📊 Executive Analytics Dashboard", "🤖 Real-Time ML Predictor"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Project:** E-Commerce End-to-End Analytics & ML Pipeline\n\n"
    "**Data Year:** 2026\n\n"
    "**API Status:** "
)

# Check API status
try:
    health_res = requests.get("http://127.0.0.1:8000/health", timeout=2)
    if health_res.status_code == 200:
        st.sidebar.success("Backend API: ONLINE 🟢")
    else:
        st.sidebar.warning("Backend API: DEGRADED 🟡")
except Exception:
    st.sidebar.error("Backend API: OFFLINE 🔴")


# ==================================================================
# FUNCTION 1: EXECUTIVE ANALYTICS DASHBOARD
# ==================================================================
if app_mode == "📊 Executive Analytics Dashboard":
    st.title("📊 E-Commerce Business Performance 2026")
    st.caption("Visualizing key business metrics & customer segmentation from SQLite Database")

    if not os.path.exists(DB_PATH):
        st.error(f"Cannot find database at `{DB_PATH}`. Please run `python src/db_connector.py` first.")
        st.stop()

    # Load overview data
    fact_df = load_db_data("SELECT * FROM fact_orders")
    rfm_df = load_db_data("SELECT * FROM rfm_segmentation")

    if fact_df.empty:
        st.warning("Table `fact_orders` has no data.")
        st.stop()

    # 1. KPI Cards
    total_revenue = fact_df["order_amount"].sum() if "order_amount" in fact_df.columns else 0
    total_orders = fact_df["order_id"].nunique() if "order_id" in fact_df.columns else len(fact_df)
    aov = total_revenue / total_orders if total_orders > 0 else 0
    
    returned_orders = len(fact_df[fact_df["order_status"].str.lower() == "returned"]) if "order_status" in fact_df.columns else 0
    return_rate = (returned_orders / total_orders) * 100 if total_orders > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Average Order Value (AOV)", f"${aov:,.2f}")
    col4.metric("Return Rate", f"{return_rate:.2f}%")

    st.markdown("---")

    # 2. Charts Section
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📦 Revenue by Product Category")
        if "product_category" in fact_df.columns and "order_amount" in fact_df.columns:
            cat_sales = (
                fact_df.groupby("product_category")["order_amount"]
                .sum()
                .sort_values(ascending=True)
            )
            st.bar_chart(cat_sales)
        else:
            st.info("Not enough information in columns `product_category` or `order_amount`.")

    with chart_col2:
        st.subheader("🎯 Customer Segmentation (RFM)")
        if not rfm_df.empty and "customer_segment" in rfm_df.columns:
            segment_counts = rfm_df["customer_segment"].value_counts()
            st.bar_chart(segment_counts)
        else:
            st.info("No data available for customer segmentation. Please run `python src/rfm_analytics.py` to generate the segmentation.")

    # 3. View Data Table Details
    with st.expander("🔍 View Sample Data Table (Top 100 Orders)"):
        st.dataframe(fact_df.head(100), use_container_width=True)


# ==================================================================
# FUNCTION 2: REAL-TIME ML PREDICTOR
# ==================================================================
elif app_mode == "🤖 Real-Time ML Predictor":
    st.title("🤖 Order High-Value Classifier")
    st.caption("Enter order information via the REST API to predict the likelihood of it becoming a **High-Value Order**.")

    st.markdown("---")

    with st.form("prediction_form"):
        st.subheader("📋 Enter Order Information")

        f_col1, f_col2, f_col3 = st.columns(3)

        with f_col1:
            order_date = st.date_input("Order Date", value=pd.to_datetime("2026-08-15"))
            product_category = st.selectbox(
                "Product Category",
                ["Electronics", "Clothing", "Home & Kitchen", "Books", "Beauty", "Sports"]
            )
            quantity = st.number_input("Quantity", min_value=1, max_value=50, value=2)
            payment_method = st.selectbox(
                "Payment Method",
                ["Credit Card", "PayPal", "Debit Card", "Cash on Delivery", "Bank Transfer"]
            )

        with f_col2:
            shipping_cost = st.number_input("Shipping Cost ($)", min_value=0.0, value=15.0, step=1.0)
            discount_applied = st.number_input("Discount Applied ($)", min_value=0.0, value=5.0, step=1.0)
            customer_age = st.slider("Customer Age", min_value=18, max_value=80, value=30)
            membership_status = st.selectbox("Membership Status", ["Silver", "Gold", "Platinum", "Regular"])

        with f_col3:
            traffic_source = st.selectbox("Traffic Source", ["Direct", "Organic Search", "Paid Ads", "Social Media", "Email"])
            device_type = st.selectbox("Device Type", ["Mobile", "Desktop", "Tablet"])

        submit_button = st.form_submit_button("🚀 Submit Real-Time Prediction", use_container_width=True)

    if submit_button:
        # Prepare the JSON payload
        payload = {
            "order_date": str(order_date),
            "product_category": product_category,
            "quantity": int(quantity),
            "payment_method": payment_method,
            "shipping_cost": float(shipping_cost),
            "discount_applied": float(discount_applied),
            "customer_age": int(customer_age),
            "membership_status": membership_status,
            "traffic_source": traffic_source,
            "device_type": device_type,
        }

        with st.spinner("Connecting to API and calculating probability..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=5)

                if response.status_code == 200:
                    result = response.json()
                    is_high_val = result.get("is_high_value_order", 0)
                    prob = result.get("high_value_probability", 0.0)

                    st.markdown("### 🎯 Results From The Model:")
                    res_col1, res_col2 = st.columns(2)

                    with res_col1:
                        if is_high_val == 1:
                            st.success("🟢 **High-Value Order**")
                        else:
                            st.warning("🟡 **Standard Order**")

                    with res_col2:
                        if prob is not None:
                            st.metric("High-Value Probability (Confidence)", f"{prob * 100:.2f}%")

                    st.json(result)

                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to Backend API! Please start the FastAPI server (`uvicorn api.main:app --reload`) first.")
            except Exception as e:
                st.error(f"Processing Error: {str(e)}")