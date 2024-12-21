import streamlit as st
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Single CSS style block
def init_styles():
    st.markdown("""
        <style>
        .news-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .news-title { font-size: 1.2rem; font-weight: bold; }
        .news-meta { color: #666; font-size: 0.9rem; }
        .news-description { margin: 0.5rem 0; }
        .news-link {
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            background-color: #02ab21;
            text-decoration: none;
            display: inline-block;
            
        }
        </style>
    """, unsafe_allow_html=True)

def get_search_queries():
    """Return a list of targeted search queries for energy saving topics"""
    return [
        # Home energy savings
        "home energy saving tips",
        "reduce electricity bill tips",
        "household energy efficiency",
        "smart home energy savings",

        # Appliance specific
        "energy efficient appliances",
        "energy star appliance savings",
        "appliance power consumption tips",

        # Seasonal
        "summer energy saving tips" if datetime.now().month in [5, 6, 7, 8, 9] else "winter energy saving tips",
        "seasonal energy efficiency",

        # Technology and Innovation
        "smart thermostat savings",
        "home energy management",
        "energy monitoring devices",
    ]

def fetch_energy_news():
    """
    Fetch energy-saving related news articles from NewsAPI with improved relevancy
    """
    load_dotenv()
    
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        st.error("NewsAPI key not found. Please set it in the .env file.")
        return []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    search_queries = get_search_queries()

    combined_query = ' OR '.join(f'({query})' for query in search_queries)
    # Add exclusion for irrelevant topics
    exclusions = '-stock -market -investment -stocks -shares -manufacturing -industrial'
    final_query = f'({combined_query}) {exclusions}'

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': final_query,
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date.strftime('%Y-%m-%d'),
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 10,
        'apiKey': api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('articles', [])
    except requests.RequestException as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def display_news_article(article):
    """
    Display a single news article in an improved card format
    """
    with st.container():
        st.markdown('<div class="news-card">', unsafe_allow_html=True)
        
        st.markdown(f'<div class="news-title">{article["title"]}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            try: 
                image_url = article.get('urlToImage')
                if image_url:
                    st.image(image_url, use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200?text=News", use_column_width=True)
            except Exception as e:
                st.image("https://via.placeholder.com/300x200?text=Error+Loading+Image", use_column_width=True)
        
        with col2:
            date = datetime.strptime(article['publishedAt'][:10], '%Y-%m-%d').strftime('%B %d, %Y')
            st.markdown(f'<div class="news-meta">📰 {article["source"]["name"]} • 📅 {date}</div>', 
                       unsafe_allow_html=True)
            
            if article.get('description'):
                st.markdown(f'<div class="news-description">{article["description"]}</div>', 
                          unsafe_allow_html=True)
            
            st.markdown(f'<a href="{article["url"]}" target="_blank" class="news-link">Read Full Article →</a>', 
                       unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def energy_news_section():
    """
    Main component for displaying energy news
    """
    st.title("📰 Latest Energy Saving Tips & News")
    init_styles()
    
    if st.button("🔄 Refresh"):
        st.rerun()
    
    # Fetch and display news
    articles = fetch_energy_news()
    if articles:
        for article in articles:
            display_news_article(article)
    else:
        st.info("No news available at this moment")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    energy_news_section()