import pandas as pd
import streamlit as st

st.title("💳 Year-End Spending Analyzer")
st.write("Upload your American Express year-end summary to analyze your spending.")

# File uploader
uploaded_file = st.file_uploader("Upload your Year-End Summary CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean Date column
    try:
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    except Exception as e:
        st.error(f"Error parsing dates: {e}")
        st.stop()

    # Clean Charges column
    df["Charges $"] = df["Charges $"].replace(r"[\$,]", "", regex=True)             # Remove $ and commas
    df["Charges $"] = df["Charges $"].replace(r"^\s*$", pd.NA, regex=True)          # Replace empty/whitespace with NaN
    df = df.dropna(subset=["Charges $"])                                            # Drop rows with missing Charges
    df["Charges $"] = df["Charges $"].astype(float)                                 # Convert to float

    # Show data preview
    st.subheader("📄 Preview of Data")
    st.write(df.head())

    # Date filter
    st.subheader("📅 Filter by Date Range")
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    start_date = st.date_input("Start date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("End date", min_value=min_date, max_value=max_date, value=max_date)

    if start_date >= end_date:
        st.warning("⚠️ End date must be after start date.")
    else:
        filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

        st.subheader("📊 Filtered Transactions")
        st.write(filtered_df.head())

        # 💰 Total Spending Section
        total_spent = filtered_df["Charges $"].sum()
        st.metric(label="💰 Total Spending", value=f"${total_spent:,.2f}")

        if st.button("Generate Spending Chart"):
            # Group and sum charges by sub-category
            chart_data = filtered_df.groupby("Sub-Category")["Charges $"].sum().sort_values(ascending=False)
            st.bar_chart(chart_data)
