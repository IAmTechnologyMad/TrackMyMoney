import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File path for transaction history
FILE_PATH = 'transactions.csv'

st.title('Track My Money 💰')

# Function to load transactions from a CSV file
def load_transactions():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    else:
        return pd.DataFrame(columns=['Date', 'Type', 'Amount', 'Description', 'Balance After'])

# Function to save transactions to a CSV file
def save_transactions(transactions_df):
    transactions_df.to_csv(FILE_PATH, index=False)

# Initialize session state
if 'balance' not in st.session_state:
    st.session_state.balance = 13245.93  # Updated initial balance (₹13,245.93)

if 'transactions' not in st.session_state:
    st.session_state.transactions = load_transactions()
    if not st.session_state.transactions.empty:
        st.session_state.balance = st.session_state.transactions['Balance After'].iloc[-1]

# Title of the app with emoji
st.title('Track My Money 💰')

# Custom CSS to style the buttons and center them
st.markdown("""
    <style>
        .center-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stButton button {
            width: 150px;
        }
        .stButton button.credit-button {
            color: green !important;
        }
        @media (max-width: 768px) {
            .stButton button {
                width: 100px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# Create a placeholder for the balance display
balance_placeholder = st.empty()

# Function to display balance with arrow
def display_balance_with_arrow(balance, transactions):
    if not transactions.empty:
        last_transaction_type = transactions['Type'].iloc[-1]
        if last_transaction_type == 'Credit':
            arrow = "&#x2191;"  # Up arrow
            color = "green"
        elif last_transaction_type == 'Debit':
            arrow = "&#x2193;"  # Down arrow
            color = "red"
        else:
            arrow = ""
            color = "black"
    else:
        arrow = ""
        color = "black"
    
    balance_placeholder.markdown(f"""
    <h3 style='display: flex; align-items: center; justify-content: center;'>
        Current Balance: ₹{balance}
        <span style='color: {color}; font-size: 30px; margin-left: 15px;'>{arrow}</span>
    </h3>
    """, unsafe_allow_html=True)

# Display initial balance
display_balance_with_arrow(st.session_state.balance, st.session_state.transactions)

# Section to add a new transaction
st.header('Add Transaction')

# Input for amount (blank input without + and - buttons)
amount_input = st.text_input("Enter the amount:")

# Validate the input to ensure it's numeric
if amount_input and amount_input.isdigit():
    amount = int(amount_input)
else:
    amount = 0  # Set amount to 0 if input is invalid or empty

# Dropdown for description
description_options = ["Groceries", "Fuel", "Medicine", "Other"]
description = st.selectbox("Select a description:", description_options)

# Input for custom description if "Other" is selected
custom_description = st.text_input("Enter custom description:") if description == "Other" else ""

# Function to add a new transaction and update balance
def add_transaction(transaction_type, amount, description):
    if transaction_type == 'Credit':
        st.session_state.balance += amount
    elif transaction_type == 'Debit':
        st.session_state.balance -= amount
    
    # Get current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Append transaction to history
    new_transaction = pd.DataFrame({
        'Date': [current_datetime],
        'Type': [transaction_type],
        'Amount': [amount],
        'Description': [description if description != "Other" else custom_description],
        'Balance After': [st.session_state.balance]
    })
    
    # Reorder columns to put 'Date' before 'Type'
    new_transaction = new_transaction[['Date', 'Type', 'Amount', 'Description', 'Balance After']]
    
    # Update the transactions DataFrame
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
    
    # Save updated transactions to CSV
    save_transactions(st.session_state.transactions)

    # Update balance display
    display_balance_with_arrow(st.session_state.balance, st.session_state.transactions)

# Use the new CSS class to center the buttons side by side
st.markdown('<div class="center-buttons">', unsafe_allow_html=True)

# Display "Credit" button with custom CSS class
if st.button('Credit', key="credit", use_container_width=True):
    if amount > 0:
        add_transaction('Credit', amount, description)
        st.success(f"Credit of ₹{amount} for {description} successful!")
    else:
        st.error("Amount should be greater than 0!")

# Display "Debit" button normally
if st.button('Debit'):
    if amount > st.session_state.balance:
        st.error("Insufficient balance!")
    elif amount > 0:
        add_transaction('Debit', amount, description)
        st.success(f"Debit of ₹{amount} for {description} successful!")
    else:
        st.error("Amount should be greater than 0!")

st.markdown('</div>', unsafe_allow_html=True)

# Display transaction history
st.header('Transaction History')
st.dataframe(st.session_state.transactions)
