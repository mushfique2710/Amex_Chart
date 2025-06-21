import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("💳 Year-End Spending Analyzer")
st.write("Upload your American Express year-end summary to analyze your spending.")

# Upload CSV with low_memory=True
uploaded_file = st.file_uploader("Upload your Year-End Summary CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, low_memory=True)

    # Clean Date column
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    # Clean Charges column
    df["Charges $"] = df["Charges $"].replace(r"[\$,]", "", regex=True)
    df["Charges $"] = df["Charges $"].replace(r"^\s*$", pd.NA, regex=True)
    df["Charges $"] = pd.to_numeric(df["Charges $"], errors="coerce")

    # Clean Credits column
    df["Credits $"] = df["Credits $"].replace(r"[\$,]", "", regex=True)
    df["Credits $"] = df["Credits $"].replace(r"^\s*$", pd.NA, regex=True)
    df["Credits $"] = pd.to_numeric(df["Credits $"], errors="coerce").fillna(0)

    # Drop rows with missing essential info
    df = df.dropna(subset=["Date", "Charges $"])

    # Preview
    st.subheader("📄 Preview of Data")
    st.write(df.head())

    # 📅 Date Filter
    st.subheader("📅 Filter by Date Range")
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

    # 🗂️ Category Filter
    st.subheader("🗂️ Filter by Category")
    available_categories = sorted(df["Category"].dropna().unique())
    selected_categories = st.multiselect("Select categories to include", available_categories, default=available_categories)

    if start_date >= end_date:
        st.warning("⚠️ End date must be after start date.")
    elif not selected_categories:
        st.warning("⚠️ Please select at least one category.")
    else:
        # Apply filters
        filtered_df = df[
            (df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date)) &
            (df["Category"].isin(selected_categories))
        ]

        st.subheader("📊 Filtered Transactions")
        st.write(filtered_df.head())

        # 💰 Financial Summary
        total_charges = filtered_df["Charges $"].sum()
        total_credits = filtered_df["Credits $"].sum()
        net_spending = total_charges - total_credits

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Spending", f"${total_charges:,.2f}")
        col2.metric("💵 Total Credits", f"${total_credits:,.2f}")
        col3.metric("🧮 Net Spending", f"${net_spending:,.2f}")

        if st.button("Generate Charts"):
            # 📊 Bar chart
            subcat_summary = filtered_df.groupby("Sub-Category")["Charges $"].sum().sort_values(ascending=False)
            st.subheader("📊 Spending by Sub-Category")
            st.bar_chart(subcat_summary)

            # 🥧 Pie chart using matplotlib
            st.subheader("🧩 Spending Breakdown by Category")
            category_summary = filtered_df.groupby("Category")["Charges $"].sum()
            fig, ax = plt.subplots()
            ax.pie(category_summary, labels=category_summary.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
