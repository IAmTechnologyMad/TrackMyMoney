import streamlit as st
import pandas as pd
import os

# File path for transaction history
FILE_PATH = 'transactions.csv'

# Function to load transactions from a CSV file
def load_transactions():
    try:
        if os.path.exists(FILE_PATH):
            return pd.read_csv(FILE_PATH)
        else:
            return pd.DataFrame(columns=['Type', 'Amount', 'Description', 'Balance After'])
    except Exception as e:
        st.error(f"Error loading transactions: {e}")
        return pd.DataFrame(columns=['Type', 'Amount', 'Description', 'Balance After'])

# Function to save transactions to a CSV file
def save_transactions(transactions_df):
    try:
        transactions_df.to_csv(FILE_PATH, index=False)
    except Exception as e:
        st.error(f"Error saving transactions: {e}")

# Initialize session state
if 'balance' not in st.session_state:
    st.session_state.balance = 7000  # Initial balance (₹7,000)

if 'transactions' not in st.session_state:
    st.session_state.transactions = load_transactions()
    if not st.session_state.transactions.empty:
        st.session_state.balance = st.session_state.transactions['Balance After'].iloc[-1]

# Title of the app with emoji
st.title('Track My Money 💰')

# Create a placeholder for the balance display
balance_placeholder = st.empty()

# Function to display balance with arrow
def display_balance_with_arrow(balance, transactions):
    try:
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
        <h3 style='display: flex; align-items: center;'>
            Current Balance: ₹{balance}
            <span style='color: {color}; font-size: 30px; margin-left: 15px;'>{arrow}</span>
        </h3>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying balance: {e}")

# Display initial balance
display_balance_with_arrow(st.session_state.balance, st.session_state.transactions)

# Section to add a new transaction
st.header('Add Transaction')

# Input for amount
amount = st.number_input("Enter the amount:", min_value=0, value=0, step=100)

# Dropdown for description
description_options = ["Groceries", "Fuel", "Medicine", "Other"]
description = st.selectbox("Select a description:", description_options)

# Input for custom description if "Other" is selected
custom_description = st.text_input("Enter custom description:") if description == "Other" else ""

# Function to add a new transaction and update balance
def add_transaction(transaction_type, amount, description):
    try:
        if transaction_type == 'Credit':
            st.session_state.balance += amount
        elif transaction_type == 'Debit':
            st.session_state.balance -= amount
        
        # Append transaction to history
        new_transaction = pd.DataFrame({
            'Type': [transaction_type],
            'Amount': [amount],
            'Description': [description if description != "Other" else custom_description],
            'Balance After': [st.session_state.balance]
        })
        st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
        # Save updated transactions to CSV
        save_transactions(st.session_state.transactions)

        # Update balance display
        display_balance_with_arrow(st.session_state.balance, st.session_state.transactions)
    except Exception as e:
        st.error(f"Error adding transaction: {e}")

# Create buttons for credit and debit transactions
col1, col2 = st.columns(2)  # Two equal-width columns

with col1:
    if st.button('Credit'):
        if amount > 0:
            add_transaction('Credit', amount, description)
            st.success(f"Credit of ₹{amount} for {description} successful!")
        else:
            st.error("Amount should be greater than 0!")

with col2:
    if st.button('Debit'):
        if amount > st.session_state.balance:
            st.error("Insufficient balance!")
        elif amount > 0:
            add_transaction('Debit', amount, description)
            st.success(f"Debit of ₹{amount} for {description} successful!")
        else:
            st.error("Amount should be greater than 0!")

# Display transaction history
st.header('Transaction History')
st.dataframe(st.session_state.transactions)
