import streamlit as st
from streamlit_option_menu import option_menu
from utils import switch_page
import login, home, account, trending, device, chatbot

st.set_page_config(
    page_title="Watt Wise",
    page_icon="⚡",
)

# Initialize page in session state if not present
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Define page mappings
PAGE_MAPPINGS = {
    'Dashboard': 'home',
    'Trending': 'trending',
    'My Devices': 'device',
    'Profile': 'account',
    'Watt-bot': 'chatbot'
}

# Sidebar Navigation
with st.sidebar:
    if 'user' in st.session_state:
        # Get current page index
        current_page = st.session_state['page']
        default_idx = 0
        
        # Map current page to menu index
        for idx, (menu_item, page_name) in enumerate(PAGE_MAPPINGS.items()):
            if page_name == current_page:
                default_idx = idx
                break

        selected = option_menu(
            menu_title="⚡ Watt Wise",
            options=['Dashboard', 'Trending', 'My Devices', 'Profile', 'Watt-bot'],
            icons=['house-door-fill', "pie-chart-fill", 'display-fill', 'person-fill', 'chat-left-text-fill'],
            menu_icon="zap",
            default_index=default_idx,
            styles={
                "container": {"padding": "5!important", "background-color": "white"},
                "icon": {"color": "#2a2a2a", "font-size": "22px"},
                "nav-link": {
                    "color": "#2a2a2a", 
                    "font-size": "18px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "--hover-color": "#34c242"
                },
                "nav-link-selected": {"background-color": "#02ab21", "color": "white"},
                "menu": {"color": "white"},
            }
        )

        # Update page based on selection
        if selected in PAGE_MAPPINGS:
            new_page = PAGE_MAPPINGS[selected]
            if new_page != st.session_state['page']:
                switch_page(new_page)
    else:
        st.info("Please login to access the dashboard")

# Page routing
page_components = {
    'login': login.app,
    'home': home.app,
    'account': account.app,
    'trending': trending.app,
    'device': device.app,
    'chatbot': chatbot.app
}

current_page = st.session_state['page']
if current_page in page_components:
    page_components[current_page]()
else:
    st.error(f"Page '{current_page}' not found.")