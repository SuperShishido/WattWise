import streamlit as st
import firebase_admin
import pandas as pd
import plotly.express as px
from firebase_admin import firestore
from datetime import datetime

class Device:
    def __init__(self, name, wattage, hours_per_day, days_per_year, category):
        self.name = name
        self.wattage = wattage
        self.hours_per_day = hours_per_day
        self.days_per_year = days_per_year
        self.category = category

    def calculate_energy_consumption(self):
        """Calculate annual energy consumption in kWh"""
        return self.wattage * self.hours_per_day * self.days_per_year / 1000
    
    def calculate_cost(self, rate=0.2487):
        """Calculate annual cost of energy consumption in CA"""
        return self.calculate_energy_consumption() * rate
    
def get_device_categories():
    return [
        "Heating",
        "Air Conditioning/Cooling",
        "Kitchen Appliances",
        "Laundry",
        "Electronics",
        "Lighting",
        "Other"
    ]

def app():
    if 'user' not in st.session_state:
        st.error("You need to login to manage your devices")
        return
    
    db = firestore.client()
    user_id = st.session_state['user']

    # Sidebar for adding new devices
    with st.sidebar:
        st.subheader("Add New Device")
        new_device_name = st.text_input("Device Name")
        new_device_category = st.selectbox("Category", get_device_categories())
        new_device_wattage = st.number_input("Wattage (W)", min_value=0)
        new_device_hours_per_day = st.number_input("Hours Used Per Day", min_value=0, max_value=24)
        new_device_days_per_year = st.number_input("Days Used Per Year", min_value=0, max_value=365)

        if st.button("Add Device"):
            if new_device_name and new_device_wattage > 0:
                device_data = {
                    "name": new_device_name,
                    "category": new_device_category,
                    "wattage": new_device_wattage,
                    "hours_per_day": new_device_hours_per_day,
                    "days_per_year": new_device_days_per_year,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }

                db.collection("users").document(user_id).collection("devices").add(device_data)
                st.success("Device added successfully")
                st.rerun()
    
    # Main content area
    st.title("My Devices")

    # Get user's devices
    devices_ref = db.collection("users").document(user_id).collection("devices").stream()
    devices = []
    
    for device in devices_ref:
        device_data = device.to_dict()
        device_data['id'] = device.id
        devices.append(device_data)

    # Group devices by category
    devices_by_category = {}
    for device in devices:
        category = device['category']
        if category not in devices_by_category:
            devices_by_category[category] = []
        devices_by_category[category].append(device)

    # Display devices by category
    total_consumption = 0
    total_cost = 0

    for category, category_devices in devices_by_category.items():
        st.header(category)
        for device in category_devices:
            with st.expander(f"{device['name']} Details"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Wattage (W)", f"{device['wattage']}W")
                
                with col2:
                    device_obj = Device(
                        device['name'],
                        device['wattage'],
                        device['hours_per_day'],
                        device['days_per_year'],
                        device['category']
                    )
                    consumption = device_obj.calculate_energy_consumption()
                    total_consumption += consumption
                    st.metric("Annual Energy Use", f"{consumption:.2f} kWh")

                with col3:
                    cost = device_obj.calculate_cost()
                    total_cost += cost
                    st.metric("Annual Cost", f"${cost:.2f}")

                # Edit/Delete buttons
                edit_col, delete_col = st.columns(2)

                with edit_col:
                    if st.button("Edit", key=f"edit_{device['id']}"):
                        st.session_state['editing_device'] = device['id']

                with delete_col:
                    if st.button("Delete", key=f"delete_{device['id']}"):
                        db.collection("users").document(user_id).collection("devices").document(device['id']).delete()
                        st.success("Device deleted successfully")
                        st.rerun()

                # Edit form
                if 'editing_device' in st.session_state and st.session_state['editing_device'] == device['id']:
                    with st.form(key=f"edit_form_{device['id']}"):
                        new_name = st.text_input("Device Name", value=device['name'])
                        new_category = st.selectbox("Category", get_device_categories(), index=get_device_categories().index(device['category']))
                        new_wattage = st.number_input("Wattage (W)", value=device['wattage'])
                        new_hours_per_day = st.number_input("Hours Used Per Day", value=device['hours_per_day'])
                        new_days_per_year = st.number_input("Days Used Per Year", value=device['days_per_year'])

                        if st.form_submit_button("Save Changes"):
                            updated_data = {
                                "name": new_name,
                                "category": new_category,
                                "wattage": new_wattage,
                                "hours_per_day": new_hours_per_day,
                                "days_per_year": new_days_per_year,
                                "updated_at": datetime.now()
                            }

                            db.collection("users").document(user_id).collection("devices").document(device['id']).update(updated_data)
                            del st.session_state['editing_device']
                            st.success("Device updated successfully")
                            st.rerun()

    # Display totals
    st.header("Total Energy Usage")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Annual Energy Use", f"{total_consumption:.2f} kWh")
    with col2:
        st.metric("Total Annual Cost", f"${total_cost:.2f}")
    
    # Collect data for pie chart (by devices)
    device_names = []
    energy_consumptions = []
    for device in devices:
        device_obj = Device(
            device['name'],
            device['wattage'],
            device['hours_per_day'],
            device['days_per_year'],
            device['category']
        )
        device_names.append(device['name'])
        energy_consumptions.append(device_obj.calculate_energy_consumption())

    # Create DataFrame for pie chart
    pie_data = pd.DataFrame({
        'Device': device_names,
        'Energy Consumption (kWh)': energy_consumptions
    })
    pie_chart = px.pie(
        pie_data,
        names='Device',
        values='Energy Consumption (kWh)',
        title="Energy Consumption by Device",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Display pie chart
    st.plotly_chart(pie_chart, use_container_width=True)