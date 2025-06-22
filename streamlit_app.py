import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("💳 Low-Memory Year-End Spending Analyzer")
st.write("Optimized to handle large Amex year-end summaries efficiently.")

# Only load required columns
USE_COLS = ["Date", "Category", "Sub-Category", "Charges $", "Credits $"]

@st.cache_data(show_spinner="Loading and optimizing CSV...")
def load_data(file):
    df = pd.read_csv(file, usecols=USE_COLS, low_memory=True)

    # Date conversion
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    # Charges cleanup
    df["Charges $"] = (
        df["Charges $"]
        .replace(r"[\$,]", "", regex=True)
        .replace(r"^\s*$", pd.NA, regex=True)
    )
    df["Charges $"] = pd.to_numeric(df["Charges $"], errors="coerce").astype("float32")

    # Credits cleanup
    df["Credits $"] = (
        df["Credits $"]
        .replace(r"[\$,]", "", regex=True)
        .replace(r"^\s*$", pd.NA, regex=True)
    )
    df["Credits $"] = pd.to_numeric(df["Credits $"], errors="coerce").fillna(0).astype("float32")

    # Drop invalid rows
    df = df.dropna(subset=["Date", "Charges $"])

    # Convert categories to category type
    df["Category"] = df["Category"].astype("category")
    df["Sub-Category"] = df["Sub-Category"].astype("category")

    return df

uploaded_file = st.file_uploader("Upload your Year-End Summary CSV", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)

    # Filters
    st.subheader("📅 Filter by Date")
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    st.subheader("🗂️ Filter by Category")
    available_categories = sorted(df["Category"].unique())
    selected_categories = st.multiselect("Select categories to include", available_categories, default=available_categories)

    if start_date >= end_date:
        st.warning("⚠️ End date must be after start date.")
    elif not selected_categories:
        st.warning("⚠️ Please select at least one category.")
    else:
        # Apply filters early
        filtered_df = df[
            (df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date)) &
            (df["Category"].isin(selected_categories))
        ]

        st.subheader("📊 Filtered Preview")
        st.write(filtered_df.head(10))  # Small preview

        # 💰 Spending Summary
        total_charges = filtered_df["Charges $"].sum()
        total_credits = filtered_df["Credits $"].sum()
        net_spending = total_charges - total_credits

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Spending", f"${total_charges:,.2f}")
        col2.metric("💵 Total Credits", f"${total_credits:,.2f}")
        col3.metric("🧮 Net Spending", f"${net_spending:,.2f}")

        if st.button("Generate Charts"):
            # Bar chart: Sub-Category
            subcat_summary = filtered_df.groupby("Sub-Category")["Charges $"].sum().sort_values(ascending=False)
            st.subheader("📊 Spending by Sub-Category")
            st.bar_chart(subcat_summary)

            # Pie chart: Category
            st.subheader("🧩 Category Spending Breakdown")
            category_summary = filtered_df.groupby("Category")["Charges $"].sum()
            fig, ax = plt.subplots()
            ax.pie(category_summary, labels=category_summary.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
