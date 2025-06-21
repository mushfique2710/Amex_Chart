import streamlit as st
import pandas as pd
import datetime
#import matplotlib.pyplot as plt
st.title("💸 Credit Card Spending Chart")
st.write("Get insights on your spending")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # convert the 'date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format = "%d/%m/%Y")
    st.subheader("Data Preview")
    st.write(df.head())

    st.subheader("Filter Data")
    columns = df[['Date', 'Sub-Category', 'Charges $']]
    filtered_df = columns
    st.write(filtered_df.head())

    d = st.date_input("Select the start date" , format = "DD/MM/YYYY")
    d1 = pd.to_datetime(d, format = "%d/%m/%Y")
    d2 = st.date_input("Select the end date",format = "DD/MM/YYYY")
    d3 = pd.to_datetime(d2, format = "%d/%m/%Y")
   
    filtered_df2 = df[(df['Date'] > d) & (df['Date'] < d2)]

    st.subheader("Summary of the selected category")
    st.write(filtered_df2.head())
    
    
    if st.button("Generate Plot"):
        st.bar_chart(filtered_df, x="Sub-Category", y="Charges $")
        st.write("Waiting on file")