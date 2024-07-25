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
def calculate_total_interest_fixed(principal, annual_rate, years, amortization_years):
    monthly_rate = annual_rate / 12 / 100
    num_payments = int(amortization_years * 12)
    num_payment_given_years=int(years*12)
    monthly_payment = calculate_fixed_mortgage_payment(principal, annual_rate, amortization_years)
    balance = principal
    total_interest = 0
    data = []

    for i in range(num_payments):
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        data.append([i+1, annual_rate, monthly_rate * 100, monthly_payment, interest, balance])

    df = pd.DataFrame(data, columns=['Month', 'Yearly Interest Rate (%)', 'Monthly Interest Rate (%)', 'Monthly Payment', 'Monthly Interest', 'Remaining Balance'])

    return total_interest, df

# Function to calculate total interest paid for variable mortgage and monthly breakdown
def calculate_total_interest_variable(principal, start_rate, rate_drop, fixed_rate, variable_period_months, amortization_years):
    balance = principal
    total_interest = 0
    data = []
    month = 0

    # First variable months with decreasing rate
    for i in range(int(variable_period_months)):
        annual_rate = start_rate - i * rate_drop
        monthly_rate = annual_rate / 12 / 100
        monthly_payment = calculate_fixed_mortgage_payment(balance, annual_rate, (amortization_years * 12 - month) / 12)
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        month += 1
        data.append([month, annual_rate, monthly_rate * 100, monthly_payment, interest, balance])

    # Remaining months with fixed rate
    fixed_months = amortization_years * 12 - variable_period_months
    for i in range(int(fixed_months)):
        annual_rate = fixed_rate
        monthly_rate = annual_rate / 12 / 100
        monthly_payment = calculate_fixed_mortgage_payment(balance, annual_rate, (amortization_years * 12 - month) / 12)
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        month += 1
        data.append([month, annual_rate, monthly_rate * 100, monthly_payment, interest, balance])

    # Ensure balance reaches zero at the end of amortization period
    while balance > 0:
        annual_rate = fixed_rate
        monthly_rate = annual_rate / 12 / 100
        monthly_payment = balance * monthly_rate + balance
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        month += 1
        data.append([month, annual_rate, monthly_rate * 100, monthly_payment, interest, balance])

    df = pd.DataFrame(data, columns=['Month', 'Yearly Interest Rate (%)', 'Monthly Interest Rate (%)', 'Monthly Payment', 'Monthly Interest', 'Remaining Balance'])

    return total_interest, df

# Streamlit UI
st.title('Mortgage Interest Comparsion')

# Create columns for the split layout
col1, col2 = st.columns(2)

with col1:
    st.info("Fixed Rate Mortgage")
    # Input fields for fixed rate mortgage
    principal_fixed = st.number_input('Mortgage Amount (Fixed Rate)', value=400000.000, format="%.3f", key='principal_fixed')
    fixed_rate = st.number_input('Fixed Mortgage Interest Rate (%)', value=4.700, format="%.3f", key='fixed_rate')
    amortization_years_fixed = st.number_input('Amortization Period (years, Fixed Rate)', value=25.000, format="%.3f", key='amortization_years_fixed')

    renewal_period_fixed = st.number_input('Mortgage RenewaL Period (years)', value=3.000, format="%.3f", key='renewal_period_fixed')

    st.image("images/morrb.png", caption='Use your own judgement', use_column_width=True)

with col2:
    st.info("Variable Rate Mortgage")
    # Input fields for variable rate mortgage
    principal_variable = st.number_input('Mortgage Amount (Variable Rate)', value=400000.000, format="%.3f", key='principal_variable')
    variable_rate = st.number_input('Variable Interest Rate Start (%)', value=6.500, format="%.3f", key='variable_rate')
    rate_drop = st.number_input('Interest Rate Drop Each Month (%)', value=0.250, format="%.3f", key='rate_drop')
    variable_period_months = st.number_input('Variable Period (months)', value=6.000, format="%.3f", key='variable_period_months')
    fixed_rate_after_variable = st.number_input('Fixed Rate After Variable Period (%)', value=3.000, format="%.3f", key='fixed_rate_after_variable')
    amortization_years_variable = st.number_input('Amortization Period (years, Variable Rate)', value=25.000, format="%.3f", key='amortization_years_variable')
    renewal_period_variable = st.number_input('Mortgage RenewaL Period (years)', value=3.000, format="%.3f", key='renewal_period_variable')

# Initialize variables
total_interest_fixed = None
total_interest_variable = None
df_fixed = None
df_variable = None

# Calculate interest and compare
if st.button('Compare'):
    total_interest_fixed, df_fixed = calculate_total_interest_fixed(principal_fixed, fixed_rate, amortization_years_fixed, amortization_years_fixed)
    total_interest_variable, df_variable = calculate_total_interest_variable(principal_variable, variable_rate, rate_drop, fixed_rate_after_variable, variable_period_months, amortization_years_variable)

    if not df_fixed.empty and 'Monthly Interest' in df_fixed.columns:
        if len(df_fixed) >= renewal_period_fixed*12:
            mort_period_interest_total_fixed = sum(df_fixed['Monthly Interest'].values.tolist()[0:int(renewal_period_fixed)*12])
        else:
            mort_period_interest_total_fixed = sum(df_fixed['Monthly Interest'].values.tolist())
    else:
        mort_period_interest_total_fixed = 0

    if not df_variable.empty and 'Monthly Interest' in df_variable.columns:
        if len(df_variable) >= renewal_period_variable*12:
            mort_period_interest_total_variable = sum(df_variable['Monthly Interest'].values.tolist()[0:int(renewal_period_variable)*12])
        else:
            mort_period_interest_total_variable = sum(df_variable['Monthly Interest'].values.tolist())
    else:
        mort_period_interest_total_variable = 0



    col1.write(f"Total Interest Paid (Fixed Rate): ${total_interest_fixed:,.3f}")
    col1.write(f"Interest Paid in Renewal Period(Fixed Rate): ${mort_period_interest_total_fixed:,.3f}")

    col2.write(f"Total Interest Paid (Variable Rate): ${total_interest_variable:,.3f}")
    col2.write(f"Interest Paid in Renewal Period (Variable Rate): ${mort_period_interest_total_variable:,.3f}")


    if total_interest_fixed > total_interest_variable:
        st.write("The Variable Rate option is better based on the interest calculations.")
        st.markdown(f"<div style='background-color: green; padding: 10px;'>Total Interest Paid (Variable Rate): ${total_interest_variable:,.3f}</div>", unsafe_allow_html=True)
    else:
        st.write("The Fixed Rate option is better based on the interest calculations.")
        st.markdown(f"<div style='background-color: green; padding: 10px;'>Total Interest Paid (Fixed Rate): ${total_interest_fixed:,.3f}</div>", unsafe_allow_html=True)

    # Display monthly breakdowns
    st.write("Monthly Breakdown (Fixed Rate):")
    st.write(df_fixed)
    st.write("Monthly Breakdown (Variable Rate):")
    st.write(df_variable)

        # Download monthly breakdowns as CSV files
    @st.cache
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_fixed = convert_df_to_csv(df_fixed)
    csv_variable = convert_df_to_csv(df_variable)

    st.download_button(
        label="Download Fixed Rate Monthly Breakdown as CSV",
        data=csv_fixed,
        file_name='fixed_rate_monthly_breakdown.csv',
        mime='text/csv',
    )

    st.download_button(
        label="Download Variable Rate Monthly Breakdown as CSV",
        data=csv_variable,
        file_name='variable_rate_monthly_breakdown.csv',
        mime='text/csv',
    )