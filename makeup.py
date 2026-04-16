import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Makeup Sales Dashboard",
    page_icon="💄",
    layout="wide"
)

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("makeup_sales_dataset_2025.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Revenue_INR"] = df["Revenue_USD"] * 90.75
    df["Price_INR"] = df["Price_USD"] * 90.75
    return df

df_raw = load_data()

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("💄 Makeup Sales")
page = st.sidebar.radio("Navigate", ["📊 Dashboard", "🔮 Revenue Prediction"])

# ================================================================
# PAGE 1: DASHBOARD
# ================================================================
if page == "📊 Dashboard":
    st.title("📊 Makeup Sales Dashboard")
    st.markdown("Interactive overview of sales performance across brands, regions, and channels.")

    # SIDEBAR FILTERS
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")

    all_brands = sorted(df_raw["Brand"].unique())
    all_products = sorted(df_raw["Product_Type"].unique())
    all_countries = sorted(df_raw["Country"].unique())
    all_channels = sorted(df_raw["Sales_Channel"].unique())

    selected_brands = st.sidebar.multiselect("Brand", all_brands, default=all_brands)
    selected_products = st.sidebar.multiselect("Product Type", all_products, default=all_products)
    selected_countries = st.sidebar.multiselect("Country", all_countries, default=all_countries)
    selected_channels = st.sidebar.multiselect("Sales Channel", all_channels, default=all_channels)

    df = df_raw[
        df_raw["Brand"].isin(selected_brands) &
        df_raw["Product_Type"].isin(selected_products) &
        df_raw["Country"].isin(selected_countries) &
        df_raw["Sales_Channel"].isin(selected_channels)
    ]

    # KPI CARDS
    total_revenue = df["Revenue_INR"].sum()
    total_units = df["Units_Sold"].sum()
    total_transactions = len(df)
    avg_order_value = df["Revenue_INR"].mean() if total_transactions > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Total Revenue (INR)", f"₹{total_revenue:,.0f}")
    k2.metric("📦 Units Sold", f"{total_units:,}")
    k3.metric("🧾 Transactions", f"{total_transactions:,}")
    k4.metric("🛒 Avg Order Value (INR)", f"₹{avg_order_value:,.0f}")

    st.markdown("---")

    # ROW 1: Revenue by Brand | Revenue by Product Type
    col1, col2 = st.columns(2)

    with col1:
        brand_rev = (
            df.groupby("Brand")["Revenue_INR"]
            .sum().reset_index()
            .sort_values("Revenue_INR", ascending=False)
        )
        fig_brand = px.bar(
            brand_rev, x="Brand", y="Revenue_INR",
            title="Revenue by Brand (INR)", color="Brand",
            text_auto=".2s", color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_brand.update_layout(showlegend=False, xaxis_title="", yaxis_title="Revenue (INR)")
        st.plotly_chart(fig_brand, use_container_width=True)

    with col2:
        product_rev = (
            df.groupby("Product_Type")["Revenue_INR"]
            .sum().reset_index()
            .sort_values("Revenue_INR", ascending=False)
        )
        fig_product = px.bar(
            product_rev, x="Product_Type", y="Revenue_INR",
            title="Revenue by Product Type (INR)", color="Product_Type",
            text_auto=".2s", color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_product.update_layout(showlegend=False, xaxis_title="", yaxis_title="Revenue (INR)")
        st.plotly_chart(fig_product, use_container_width=True)

    # ROW 2: Monthly Revenue Trend
    monthly_rev = (
        df.groupby("Month")["Revenue_INR"]
        .sum().reset_index().sort_values("Month")
    )
    fig_trend = px.line(
        monthly_rev, x="Month", y="Revenue_INR",
        title="Monthly Revenue Trend (INR)", markers=True,
        color_discrete_sequence=["#e91e8c"]
    )
    fig_trend.update_layout(xaxis_title="Month", yaxis_title="Revenue (INR)")
    st.plotly_chart(fig_trend, use_container_width=True)

    # ROW 3: Revenue by Country | Sales Channel Breakdown
    col3, col4 = st.columns(2)

    with col3:
        country_rev = (
            df.groupby("Country")["Revenue_INR"]
            .sum().reset_index()
            .sort_values("Revenue_INR", ascending=False)
        )
        fig_country = px.choropleth(
            country_rev, locations="Country", locationmode="country names",
            color="Revenue_INR", title="Revenue by Country (INR)",
            color_continuous_scale="RdPu", labels={"Revenue_INR": "Revenue (INR)"}
        )
        fig_country.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_country, use_container_width=True)

    with col4:
        channel_rev = df.groupby("Sales_Channel")["Revenue_INR"].sum().reset_index()
        fig_channel = px.pie(
            channel_rev, names="Sales_Channel", values="Revenue_INR",
            title="Revenue by Sales Channel",
            color_discrete_sequence=px.colors.qualitative.Pastel, hole=0.4
        )
        st.plotly_chart(fig_channel, use_container_width=True)

    # ROW 4: Payment Method | Units Sold by Brand
    col5, col6 = st.columns(2)

    with col5:
        payment_rev = df.groupby("Payment_Method")["Revenue_INR"].sum().reset_index()
        fig_payment = px.pie(
            payment_rev, names="Payment_Method", values="Revenue_INR",
            title="Revenue by Payment Method",
            color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4
        )
        st.plotly_chart(fig_payment, use_container_width=True)

    with col6:
        units_brand = (
            df.groupby("Brand")["Units_Sold"]
            .sum().reset_index()
            .sort_values("Units_Sold", ascending=True)
        )
        fig_units = px.bar(
            units_brand, x="Units_Sold", y="Brand", orientation="h",
            title="Units Sold by Brand", color="Brand", text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_units.update_layout(showlegend=False, xaxis_title="Units Sold", yaxis_title="")
        st.plotly_chart(fig_units, use_container_width=True)

    # ROW 5: Heatmap Brand x Product Type
    st.subheader("Revenue Heatmap: Brand × Product Type (INR)")
    heatmap_data = (
        df.groupby(["Brand", "Product_Type"])["Revenue_INR"]
        .sum().reset_index()
        .pivot(index="Brand", columns="Product_Type", values="Revenue_INR")
        .fillna(0)
    )
    fig_heat = px.imshow(
        heatmap_data, text_auto=".2s", color_continuous_scale="RdPu",
        aspect="auto", labels={"color": "Revenue (INR)"}
    )
    fig_heat.update_layout(xaxis_title="Product Type", yaxis_title="Brand")
    st.plotly_chart(fig_heat, use_container_width=True)

    # RAW DATA
    with st.expander("📋 View Raw Data"):
        st.dataframe(df.reset_index(drop=True), use_container_width=True)


# ================================================================
# PAGE 2: REVENUE PREDICTION
# ================================================================
elif page == "🔮 Revenue Prediction":
    st.title("🔮 Revenue Prediction")
    st.markdown("Predict expected revenue based on product and sales details.")

    brand_options = df_raw["Brand"].unique()
    product_options = df_raw["Product_Type"].unique()
    country_options = df_raw["Country"].unique()
    channel_options = df_raw["Sales_Channel"].unique()
    payment_options = df_raw["Payment_Method"].unique()

    # PREPROCESSING FOR MODEL
    df_model = df_raw.drop(columns=["Date", "Sale_ID", "Month", "Revenue_INR"]).copy()

    from sklearn.preprocessing import OneHotEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor

    encoders = {}

    def encode_categorical(dataframe, column):
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        encoded = encoder.fit_transform(dataframe[[column]])
        encoded_df = pd.DataFrame(
            encoded,
            columns=encoder.get_feature_names_out([column]),
            index=dataframe.index
        ).astype(int)
        dataframe.drop(columns=[column], inplace=True)
        dataframe[encoded_df.columns] = encoded_df
        encoders[column] = encoder

    encode_categorical(df_model, "Brand")
    encode_categorical(df_model, "Product_Type")
    encode_categorical(df_model, "Country")
    encode_categorical(df_model, "Sales_Channel")
    encode_categorical(df_model, "Payment_Method")

    X = df_model.drop(["Price_INR", "Revenue_USD", "Price_USD"], axis=1, errors="ignore")
    y = df_model["Price_INR"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    feature_columns = X.columns

    # INPUT FORM
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox("Brand", brand_options)
            product_type = st.selectbox("Product Type", product_options)
            country = st.selectbox("Country", country_options)
        with col2:
            sales_channel = st.selectbox("Sales Channel", channel_options)
            payment_method = st.selectbox("Payment Method", payment_options)
            quantity = st.number_input("Units Sold", min_value=1, value=10)

        submitted = st.form_submit_button("Predict Revenue", use_container_width=True)

    if submitted:
        input_data = pd.DataFrame({
            "Brand": [brand], "Product_Type": [product_type],
            "Country": [country], "Sales_Channel": [sales_channel],
            "Payment_Method": [payment_method]
        })

        for col in ["Brand", "Product_Type", "Country", "Sales_Channel", "Payment_Method"]:
            encoder = encoders[col]
            encoded = encoder.transform(input_data[[col]])
            encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out([col]))
            input_data.drop(columns=[col], inplace=True)
            input_data[encoded_df.columns] = encoded_df

        input_data = input_data.reindex(columns=feature_columns, fill_value=0)

        predicted_price = model.predict(input_data)[0]
        predicted_revenue = predicted_price * quantity

        st.markdown("---")
        r1, r2 = st.columns(2)
        r1.metric("💰 Predicted Unit Price (INR)", f"₹{predicted_price:,.2f}")
        r2.metric("📈 Predicted Revenue (INR)", f"₹{predicted_revenue:,.2f}")

        fig_result = go.Figure(go.Bar(
            x=["Unit Price (INR)", f"Revenue for {quantity} units (INR)"],
            y=[predicted_price, predicted_revenue],
            marker_color=["#e91e8c", "#9c27b0"],
            text=[f"₹{predicted_price:,.0f}", f"₹{predicted_revenue:,.0f}"],
            textposition="outside"
        ))
        fig_result.update_layout(
            title="Prediction Breakdown", yaxis_title="Amount (INR)", showlegend=False
        )
        st.plotly_chart(fig_result, use_container_width=True)
