import streamlit as st
import pandas as pd

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("makeup_sales_dataset_2025.csv")

# -------------------------------
# SAVE ORIGINAL OPTIONS
# -------------------------------
brand_options = df["Brand"].unique()
product_options = df["Product_Type"].unique()
country_options = df["Country"].unique()
channel_options = df["Sales_Channel"].unique()
payment_options = df["Payment_Method"].unique()

# -------------------------------
# PREPROCESSING
# -------------------------------
df.drop("Date", axis=1, inplace=True)

# Convert USD → INR
df["Price_USD"] *= 90.75
df.rename(columns={"Price_USD": "Price_INR"}, inplace=True)

df.drop("Sale_ID", axis=1, inplace=True)

# -------------------------------
# ENCODING
# -------------------------------
from sklearn.preprocessing import OneHotEncoder

encoders = {}

def encode_categorical(df, column):
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded = encoder.fit_transform(df[[column]])

    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out([column]),
        index=df.index
    ).astype(int)

    df.drop(columns=[column], inplace=True)
    df[encoded_df.columns] = encoded_df

    encoders[column] = encoder

# Apply encoding
encode_categorical(df, "Brand")
encode_categorical(df, "Product_Type")
encode_categorical(df, "Country")
encode_categorical(df, "Sales_Channel")
encode_categorical(df, "Payment_Method")

# -------------------------------
# TRAIN MODEL TO PREDICT PRICE
# -------------------------------
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

X = df.drop(["Price_INR", "Revenue_USD"], axis=1)
y = df["Price_INR"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor()
model.fit(X_train, y_train)

feature_columns = X.columns

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("Makeup Sales Revenue Prediction")

brand = st.selectbox("Select Brand", brand_options)
product_type = st.selectbox("Product Type", product_options)
country = st.selectbox("Country", country_options)
sales_channel = st.selectbox("Sales Channel", channel_options)
payment_method = st.selectbox("Payment Method", payment_options)
quantity = st.number_input("Units Sold", min_value=1)

# -------------------------------
# CREATE INPUT DATA
# -------------------------------
input_data = pd.DataFrame({
    "Brand": [brand],
    "Product_Type": [product_type],
    "Country": [country],
    "Sales_Channel": [sales_channel],
    "Payment_Method": [payment_method]
})

# Apply SAME encoders
for col in ["Brand", "Product_Type", "Country", "Sales_Channel", "Payment_Method"]:
    encoder = encoders[col]
    encoded = encoder.transform(input_data[[col]])

    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out([col])
    )

    input_data.drop(columns=[col], inplace=True)
    input_data[encoded_df.columns] = encoded_df

# Ensure column match
input_data = input_data.reindex(columns=feature_columns, fill_value=0)

# -------------------------------
# PREDICT PRICE
# -------------------------------
predicted_price = model.predict(input_data)[0]

# -------------------------------
# CALCULATE REVENUE
# -------------------------------
predicted_revenue = predicted_price * quantity

# -------------------------------
# OUTPUT
# -------------------------------
st.subheader("Predicted Revenue (INR):")
st.write(round(predicted_revenue, 2))