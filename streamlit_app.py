import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("💳 Streaming Year-End Spending Analyzer")
st.write("Handles large CSVs safely using chunked loading.")

USE_COLS = ["Date", "Category", "Sub-Category", "Charges $", "Credits $"]

@st.cache_data(show_spinner="Streaming and filtering CSV...")
def stream_process_csv(file, start_date, end_date, selected_categories):
    chunks = pd.read_csv(file, usecols=USE_COLS, low_memory=True, chunksize=10000)

    filtered_chunks = []
    for chunk in chunks:
        # Clean and convert
        chunk["Date"] = pd.to_datetime(chunk["Date"], dayfirst=True, errors="coerce")
        chunk["Charges $"] = pd.to_numeric(
            chunk["Charges $"]
                .replace(r"[\$,]", "", regex=True)
                .replace(r"^\s*$", pd.NA, regex=True),
            errors="coerce"
        ).astype("float32")

        chunk["Credits $"] = pd.to_numeric(
            chunk["Credits $"]
                .replace(r"[\$,]", "", regex=True)
                .replace(r"^\s*$", pd.NA, regex=True),
            errors="coerce"
        ).fillna(0).astype("float32")

        chunk = chunk.dropna(subset=["Date", "Charges $"])
        chunk = chunk[
            (chunk["Date"] >= pd.to_datetime(start_date)) &
            (chunk["Date"] <= pd.to_datetime(end_date)) &
            (chunk["Category"].isin(selected_categories))
        ]

        filtered_chunks.append(chunk)

    if filtered_chunks:
        final_df = pd.concat(filtered_chunks, ignore_index=True)
        final_df["Category"] = final_df["Category"].astype("category")
        final_df["Sub-Category"] = final_df["Sub-Category"].astype("category")
        return final_df
    else:
        return pd.DataFrame(columns=USE_COLS)

uploaded_file = st.file_uploader("📂 Upload Year-End Summary CSV", type="csv")

if uploaded_file:
    # Get categories first from a quick peek at the file
    temp_df = pd.read_csv(uploaded_file, usecols=["Category"], nrows=500)
    default_categories = sorted(temp_df["Category"].dropna().unique())

    # Filter UI
    st.subheader("📅 Select Date Range")
    start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2024-12-31"))

    st.subheader("🗂️ Select Categories")
    selected_categories = st.multiselect("Filter categories", default_categories, default=default_categories)

    if start_date >= end_date:
        st.warning("⚠️ End date must be after start date.")
    elif not selected_categories:
        st.warning("⚠️ Please select at least one category.")
    else:
        # Process large file with filters
        filtered_df = stream_process_csv(uploaded_file, start_date, end_date, selected_categories)

        if filtered_df.empty:
            st.info("No matching transactions found.")
        else:
            st.success(f"✅ Loaded {len(filtered_df):,} filtered transactions.")

            # Show top rows only
            st.subheader("📄 Preview")
            st.write(filtered_df.head(10))

            # Spending metrics
            total_charges = filtered_df["Charges $"].sum()
            total_credits = filtered_df["Credits $"].sum()
            net_spending = total_charges - total_credits

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Spending", f"${total_charges:,.2f}")
            col2.metric("💵 Total Credits", f"${total_credits:,.2f}")
            col3.metric("🧮 Net Spending", f"${net_spending:,.2f}")

            # Chart logic
            if len(filtered_df) > 5000:
                st.warning("📉 Skipping charts due to large size. Showing summary only.")
            else:
                # Bar chart
                st.subheader("📊 Spending by Sub-Category")
                subcat_summary = filtered_df.groupby("Sub-Category")["Charges $"].sum().sort_values(ascending=False)
                st.bar_chart(subcat_summary)

                # Pie chart
                st.subheader("🧩 Spending by Category")
                category_summary = filtered_df.groupby("Category")["Charges $"].sum()
                fig, ax = plt.subplots()
                ax.pie(category_summary, labels=category_summary.index, autopct="%1.1f%%", startangle=90)
                ax.axis("equal")
                st.pyplot(fig)
