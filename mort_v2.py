
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Function to calculate fixed monthly mortgage payment
def calculate_fixed_mortgage_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100
    num_payments = int(years * 12)
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return monthly_payment

# Function to calculate total interest paid for fixed mortgage and monthly breakdown
def calculate_total_interest_fixed(principal, annual_rate, years):
    monthly_payment = calculate_fixed_mortgage_payment(principal, annual_rate, years)
    num_payments = int(years * 12)
    balance = principal
    total_interest = 0
    data = []

    for i in range(num_payments):
        monthly_rate = annual_rate / 12 / 100
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        data.append([i+1, annual_rate, monthly_rate * 100, monthly_payment, interest, balance])

    df = pd.DataFrame(data, columns=['Month', 'Yearly Interest Rate (%)', 'Monthly Interest Rate (%)', 'Monthly Payment', 'Monthly Interest', 'Remaining Balance'])
    total_paid = monthly_payment * num_payments
    total_interest = total_paid - principal

    return total_interest, df

# Function to calculate total interest paid for variable mortgage and monthly breakdown
def calculate_total_interest_variable(principal, start_rate, rate_drop, fixed_rate, drop_months, fixed_months):
    balance = principal
    total_interest = 0
    data = []
    month = 0

    # First variable months with decreasing rate
    for i in range(int(drop_months)):
        annual_rate = start_rate - i * rate_drop
        monthly_rate = annual_rate / 12 / 100
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = calculate_fixed_mortgage_payment(balance, annual_rate, (drop_months - i) / 12) - interest
        balance -= principal_payment
        month += 1
        data.append([month, annual_rate, monthly_rate * 100, principal_payment + interest, interest, balance])

    # Remaining months with fixed rate
    for i in range(int(fixed_months)):
        annual_rate = fixed_rate
        monthly_rate = annual_rate / 12 / 100
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = calculate_fixed_mortgage_payment(balance, annual_rate, (fixed_months - i) / 12) - interest
        balance -= principal_payment
        month += 1
        data.append([month, annual_rate, monthly_rate * 100, principal_payment + interest, interest, balance])

    df = pd.DataFrame(data, columns=['Month', 'Yearly Interest Rate (%)', 'Monthly Interest Rate (%)', 'Monthly Payment', 'Monthly Interest', 'Remaining Balance'])

    return total_interest, df

# Streamlit UI
st.title('Mortgage Interest Calculator')

# Create columns for the split layout
col1, col2 = st.columns(2)

with col1:
    st.info("Fixed Rate Mortgage")
    # Input fields for fixed rate mortgage
    principal_fixed = st.number_input('Mortgage Amount (Fixed Rate)', value=400000.000, format="%.3f", key='principal_fixed')
    fixed_rate = st.number_input('Fixed Mortgage Interest Rate (%)', value=4.700, format="%.3f", key='fixed_rate')
    total_years_fixed = st.number_input('Total Mortgage Period (years, Fixed Rate)', value=3.000, format="%.3f", key='total_years_fixed')
    st.image("images/morrb.png", caption='Use your own judgement', use_column_width=True)

with col2:
    st.info("Variable Rate Mortgage")
    # Input fields for variable rate mortgage
    principal_variable = st.number_input('Mortgage Amount (Variable Rate)', value=400000.000, format="%.3f", key='principal_variable')
    variable_rate = st.number_input('Variable Interest Rate Start (%)', value=6.500, format="%.3f", key='variable_rate')
    rate_drop = st.number_input('Interest Rate Drop Each Month (%)', value=0.250, format="%.3f", key='rate_drop')
    variable_period_months = st.number_input('Variable Period (months)', value=6.000, format="%.3f", key='variable_period_months')
    fixed_rate_after_variable = st.number_input('Fixed Rate After Variable Period (%)', value=3.000, format="%.3f", key='fixed_rate_after_variable')
    total_years_variable = st.number_input('Total Mortgage Period (years, Variable Rate)', value=3.000, format="%.3f", key='total_years_variable')

# Initialize variables
total_interest_fixed = None
total_interest_variable = None
df_fixed = None
df_variable = None

# Calculate interest and compare
if st.button('Compare'):
    total_interest_fixed, df_fixed = calculate_total_interest_fixed(principal_fixed, fixed_rate, total_years_fixed)
    drop_months = variable_period_months
    fixed_months = total_years_variable * 12 - drop_months
    total_interest_variable, df_variable = calculate_total_interest_variable(principal_variable, variable_rate, rate_drop, fixed_rate_after_variable, drop_months, fixed_months)

    col1.write(f"Total Interest Paid (Fixed Rate): ${total_interest_fixed:,.3f}")
    col2.write(f"Total Interest Paid (Variable Rate): ${total_interest_variable:,.3f}")

    if total_interest_fixed > total_interest_variable:
        st.write("The Variable Rate option is better based on the interest calculations.", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: green; padding: 10px; color: white;'>Total Interest Paid (Variable Rate): ${total_interest_variable:,.3f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: yellow; padding: 10px;'>Total Interest Paid (Fixed Rate): ${total_interest_fixed:,.3f}</div>", unsafe_allow_html=True)
    elif total_interest_fixed < total_interest_variable:
        st.write("The Fixed Rate option is better based on the interest calculations.", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: green; padding: 10px; color: white;'>Total Interest Paid (Fixed Rate): ${total_interest_fixed:,.3f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: yellow; padding: 10px;'>Total Interest Paid (Variable Rate): ${total_interest_variable:,.3f}</div>", unsafe_allow_html=True)
    else:
        st.write("Both options result in the same total interest paid.", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: cyan; padding: 10px; color: white;'>Total Interest Paid (Fixed Rate): ${total_interest_fixed:,.3f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: cyan; padding: 10px; color: white;'>Total Interest Paid (Variable Rate): ${total_interest_variable:,.3f}</div>", unsafe_allow_html=True)

    st.write("Download the detailed interest breakdown:")








    st.info("Fixed rate interest details:")
    st.write(df_fixed)

    st.info("Variable rate interest details:")
    st.write(df_variable)

