import streamlit as st

def switch_page(page):
    """
    Updates the session state with the target page and triggers a rerun
    if the page has actually changed
    """
    if st.session_state.get('page') != page.lower():
        st.session_state['page'] = page.lower()
        st.rerun()