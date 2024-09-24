import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Property Price Prediction")

with open('df.pkl', 'rb') as file:
    df = pickle.load(file)

with open('pipeline.pkl', 'rb') as file:
    pipeline = pickle.load(file)

st.header('Enter your inputs')

# property_type
property_type = st.selectbox('Property Type', ['flat', 'house'])

# sector
sector = st.selectbox('Sector', sorted(df['sector'].unique().tolist()))

# Bedrooms with input validation
bedrooms = st.number_input('Number of Bedrooms', min_value=1, max_value=10, value=2, step=1)

# Bathrooms with input validation
bathrooms = st.number_input('Number of Bathrooms', min_value=1, max_value=bedrooms, value=2, step=1)

balcony = st.selectbox('Balconies', sorted(df['balcony'].unique().tolist()))

property_age = st.selectbox('Property Age', sorted(df['agePossession'].unique().tolist()))

# Built-up area with input validation
avg_bedroom_size = 132
avg_bathroom_size = 40
built_up_area = st.number_input('Built Up Area (sq ft)', min_value=bedrooms * avg_bedroom_size + bathrooms * avg_bathroom_size, max_value=10000, value=1500, step=50)

servant_room = float(st.selectbox('Servant Room', [0.0, 1.0]))
store_room = float(st.selectbox('Store Room', [0.0, 1.0]))

furnishing_type = st.selectbox('Furnishing Type', sorted(df['furnishing_type'].unique().tolist()))
luxury_category = st.selectbox('Luxury Category', sorted(df['luxury_category'].unique().tolist()))
floor_category = st.selectbox('Floor Category', sorted(df['floor_category'].unique().tolist()))

if st.button('Predict'):
    # Input validation
    if built_up_area < bedrooms * avg_bedroom_size + bathrooms * avg_bathroom_size:
        st.error("The built-up area seems too small for the number of bedrooms and bathrooms. Please check your inputs.")
    elif built_up_area / bedrooms > 1000:
        st.error("The built-up area seems too large for the number of bedrooms. Please check your inputs.")
    elif bathrooms > bedrooms:
        st.error("The number of bathrooms cannot be greater than the number of bedrooms. Please check your inputs.")
    else:
        # form a dataframe
        data = [[property_type, sector, bedrooms, bathrooms, balcony, property_age, built_up_area, servant_room, store_room,
                 furnishing_type, luxury_category, floor_category]]
        columns = ['property_type', 'sector', 'bedRoom', 'bathroom', 'balcony',
                   'agePossession', 'built_up_area', 'servant room', 'store room',
                   'furnishing_type', 'luxury_category', 'floor_category']

        # Convert to DataFrame
        one_df = pd.DataFrame(data, columns=columns)

        # predict
        base_price = np.expm1(pipeline.predict(one_df))[0]
        low = base_price - 0.22
        high = base_price + 0.22

        # display
        st.success(f"The estimated price of the property is between {round(low, 2)} Cr and {round(high, 2)} Cr")