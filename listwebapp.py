import streamlit as st
from datetime import datetime
import pymysql
import pandas as pd

# Example username and password (For testing purposes, this can be replaced with a database or a secure method)
VALID_USERNAME = "khurram"
VALID_PASSWORD = "15199400"

# MySQL database connection using PyMySQL
def connect_to_db():
    return pymysql.connect(
        host="localhost",  # Host (default for MySQL Workbench is localhost)
        user="root",       # Your MySQL username
        password="Gh6968amu@",       # Your MySQL password (if any)
        database="milk_shop"  # Name of your database
    )

# Initialize session state for storing data
if 'price_per_liter' not in st.session_state:
    st.session_state.price_per_liter = 0

# Check if user is logged in
def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

# Login function
def login(username, password):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False
        st.error("Invalid username or password")

# Load data from MySQL
def load_data_from_db():
    conn = connect_to_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM milk_data")
    result = cursor.fetchall()
    conn.close()
    return result

# Save data to MySQL
def save_data_to_db(date, day, time, quantity, total_price):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO milk_data (date, day, time, quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
        (date, day, time, quantity, total_price)
    )
    conn.commit()
    conn.close()

# Delete data from MySQL
def delete_data_from_db(entry_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM milk_data WHERE id = %s", (entry_id,))
    conn.commit()
    conn.close()

# App title
st.title("Hanief Milk Shop Management")

# Step 1: Login Form
check_login()

if not st.session_state.logged_in:
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            login(username, password)

# If logged in, show the app
if st.session_state.logged_in:
    # Step 2: Input box for price per liter
    st.header("Set Milk Price per Liter")
    price_input = st.text_input("Enter the price per liter of milk:", value="0")
    if st.button("Save Price"):
        try:
            st.session_state.price_per_liter = float(price_input)
            st.success(f"Price per liter set to: ₹{st.session_state.price_per_liter}")
        except ValueError:
            st.error("Please enter a valid number for the price.")

    # Step 3: Input daily milk quantity and save it
    st.header("Add Milk Quantity")
    quantity_input = st.text_input("Enter the daily milk quantity in liters:", value="0")
    if st.button("Add Quantity"):
        try:
            daily_quantity = float(quantity_input)
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_day = datetime.now().strftime("%A")
            current_time = datetime.now().strftime("%H:%M:%S")
            total_price = daily_quantity * st.session_state.price_per_liter

            # Save data to MySQL
            save_data_to_db(current_date, current_day, current_time, daily_quantity, total_price)

            st.success(f"Added {daily_quantity} liters for {current_date} ({current_day}) at {current_time}.")
        except ValueError:
            st.error("Please enter a valid number for the quantity.")

    # Step 4: Show daily entries from MySQL in a table
    st.header("Daily Milk Entries")
    milk_data = load_data_from_db()

    if milk_data:
        df = pd.DataFrame(milk_data)
        st.dataframe(df)
    else:
        st.write("No data available.")

    # Step 5: Delete a specific entry from MySQL
    st.header("Delete Entry")
    if milk_data:
        options = [f"{entry['date']} - {entry['day']} at {entry['time']}" for entry in milk_data]
        selected_entry = st.selectbox("Select an entry to delete:", options)

        if st.button("Delete Selected Entry"):
            # Find the ID of the selected entry
            selected_id = milk_data[options.index(selected_entry)]['id']

            # Delete the selected entry from the database
            delete_data_from_db(selected_id)

            st.success(f"Deleted entry for {selected_entry}.")

            # Reload and display the updated data
            milk_data = load_data_from_db()
            if milk_data:
                df = pd.DataFrame(milk_data)
                st.dataframe(df)
            else:
                st.write("No entries available.")

    # Step 6: Calculate and show total
    st.header("Show Total")
    if st.button("Calculate Total"):
        total_quantity = sum(entry["quantity"] for entry in milk_data)
        total_price = sum(entry["total_price"] for entry in milk_data)
        st.write(f"**Total Milk Quantity:** {total_quantity} liters")
        st.write(f"**Total Price:** ₹{total_price}")

# Logout option
if st.session_state.logged_in:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("You have been logged out.")
