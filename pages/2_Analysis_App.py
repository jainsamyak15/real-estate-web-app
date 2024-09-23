import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import re

st.set_page_config(page_title="Plotting Demo")
st.set_option('deprecation.showPyplotGlobalUse', False)


st.title('Analytics')

new_df = pd.read_csv('datasets/data_viz1.csv')
wordcloud_df = pd.read_csv('datasets/wordcloud_df.csv', header=None, names=['features', 'sector'])
# Function to safely process the features
def process_features(features):
    if pd.isna(features):
        return []
    try:
        # Remove brackets and split by comma
        return [item.strip().strip("'") for item in features.strip('[]').split(',')]
    except:
        return []

# Apply the function to process features
wordcloud_df['features'] = wordcloud_df['features'].apply(process_features)

feature_text = pickle.load(open('datasets/feature_text.pkl', 'rb'))

group_df = new_df.groupby('sector').mean(numeric_only=True)[
    ['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']]

st.header('Sector Price per Sqft Geomap')
fig = px.scatter_mapbox(group_df, lat="latitude", lon="longitude", color="price_per_sqft", size='built_up_area',
                        color_continuous_scale=px.colors.cyclical.IceFire, zoom=10,
                        mapbox_style="open-street-map", width=1200, height=700, hover_name=group_df.index)

st.plotly_chart(fig, use_container_width=True)

st.header('Features Wordcloud')

# Add sector selection for word cloud
sector_options = ['All'] + sorted([sector for sector in wordcloud_df['sector'].unique().tolist() if sector != "sector"])
selected_sector = st.selectbox('Select Sector for Word Cloud', sector_options)

# Generate word cloud text based on selected sector
if selected_sector == 'All':
    wordcloud_text = ' '.join([' '.join(features) for features in wordcloud_df['features']])
else:
    # Filtering features for the selected sector
    sector_features = wordcloud_df[wordcloud_df['sector'] == selected_sector]['features'].tolist()
    wordcloud_text = ' '.join([' '.join(features) for features in sector_features])

# Using regex to remove unwanted words (case-insensitive)
wordcloud_text = re.sub(r'\b(feng|shui|Feng Shui|Feng|Shui)\b', '', wordcloud_text, flags=re.IGNORECASE)
wordcloud_text = re.sub(r'\b(Vaastu)\b', 'Great Vaastu', wordcloud_text, flags=re.IGNORECASE)

wordcloud = WordCloud(width=800, height=800,
                      background_color='black',
                      min_font_size=10).generate(wordcloud_text)

plt.figure(figsize=(10, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.tight_layout(pad=0)
st.pyplot()


st.header('Area Vs Price')

property_type = st.selectbox('Select Property Type', ['flat', 'house'])

if property_type == 'house':
    fig1 = px.scatter(new_df[new_df['property_type'] == 'house'], x="built_up_area", y="price", color="bedRoom",
                      title="Area Vs Price")

    st.plotly_chart(fig1, use_container_width=True)
else:
    fig1 = px.scatter(new_df[new_df['property_type'] == 'flat'], x="built_up_area", y="price", color="bedRoom",
                      title="Area Vs Price")

    st.plotly_chart(fig1, use_container_width=True)

st.header('BHK Pie Chart')

sector_options = new_df['sector'].unique().tolist()
sector_options.insert(0, 'overall')

selected_sector = st.selectbox('Select Sector', sector_options)

if selected_sector == 'overall':

    fig2 = px.pie(new_df, names='bedRoom')

    st.plotly_chart(fig2, use_container_width=True)
else:

    fig2 = px.pie(new_df[new_df['sector'] == selected_sector], names='bedRoom')

    st.plotly_chart(fig2, use_container_width=True)

st.header('Side by Side BHK price comparison')

fig3 = px.box(new_df[new_df['bedRoom'] <= 4], x='bedRoom', y='price', title='BHK Price Range')

st.plotly_chart(fig3, use_container_width=True)

st.header('Side by Side Distplot for property type')

fig3 = plt.figure(figsize=(10, 4))
sns.distplot(new_df[new_df['property_type'] == 'house']['price'], label='house')
sns.distplot(new_df[new_df['property_type'] == 'flat']['price'], label='flat')
plt.legend()
st.pyplot(fig3)
