import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
st.title("💸 Amex Spending Chart")
st.write("Get insights on your spending")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.write(df.head())

    st.subheader("Filter Data")
    columns = df.columns.tolist()
    selected_columns = st.multiselect("Select columns to filter by", columns)
    filtered_df = df[selected_columns]
    st.subheader("Summary of the selected category")
    st.write(filtered_df.head())
    
    #st.subheader("Plot Data")
   #x_column = st.selectbox("Select x axis", filtered_df)
    #y_column = filtered_df.iloc[:,1]

    
    if st.button("Generate Plot"):
        st.bar_chart(filtered_df, x=filtered_df.iloc(:,1), y=filtered_df.iloc(:,2))
    st.write("Waiting on file")