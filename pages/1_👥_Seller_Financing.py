import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go


####################################################
#                      PARAMS                      #
####################################################
st.set_page_config(layout="wide")


####################################################
#                   FUNCTION                       #
####################################################
def seller_financing_calculator(sale_price, down_payment_rate, annual_interest_rate, loan_term_years, balloon_due_years=None, interest_only_years=None):
    # Calculate the initial loan amount
    down_payment = int(sale_price * (down_payment_rate/100))
    loan_amount = sale_price - down_payment
    
    # Monthly interest rate
    monthly_interest_rate = annual_interest_rate / 100 / 12
    # Total number of payments
    total_payments = loan_term_years * 12
    
    # Calculate the monthly payment for a fully amortizing loan
    if monthly_interest_rate > 0:
        monthly_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_payments)
    else:
        monthly_payment = loan_amount / total_payments
    
    # Create amortization table
    amortization_table = []
    balance = loan_amount
    for month in range(1, total_payments + 1):
        interest_payment = balance * monthly_interest_rate
        if interest_only_years and month <= interest_only_years * 12:
            principal_payment = 0
            monthly_payment_during_interest_only = loan_amount * monthly_interest_rate
            amortization_table.append([month, monthly_payment_during_interest_only, interest_payment, principal_payment, balance])
        else:
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment
            amortization_table.append([month, monthly_payment, interest_payment, principal_payment, max(balance, 0)])
        
        if balloon_due_years and month == balloon_due_years * 12:
            balloon_payment = balance
            amortization_table.append([month, monthly_payment, interest_payment, principal_payment, 0])
            break

    # Convert amortization table to DataFrame for better display
    df_amortization_table = pd.DataFrame(amortization_table, columns=["Month", "Monthly Payment", "Interest", "Principal", "Remaining Balance"])
    
    # Total interest paid
    total_interest_paid = df_amortization_table["Interest"].sum()
    
    # Total payments
    total_payments_made = df_amortization_table["Monthly Payment"].sum() + (balloon_payment if balloon_due_years else 0)
    
    return {
        "Down Payment": down_payment,
        "Balloon Amount": df_amortization_table.iloc[-2]['Remaining Balance'],
        "Monthly Payment Interest Only": round(df_amortization_table.iloc[0]['Monthly Payment'], 2),
        "Monthly Payment Non Interest Only": round(df_amortization_table.iloc[-1]['Monthly Payment'], 2),
        "Monthly Payment": round(monthly_payment, 2),
        "Total Interest Paid": round(total_interest_paid, 2),
        "Total Payment Amount": round(total_payments_made, 2),
        "Amortization Table": df_amortization_table.iloc[:-1]
    }


####################################################
#                      APP                         #
####################################################
st.title('Seller Financing Calculator 👥')
st.subheader('Enter details to calculate offer terms')
st.markdown('Want to see the properties 🏡 behind the numbers? Check out 👉 [Coffee Clozers](https://bit.ly/3EJRAa5) 🏡, we help real estate investors find cash flowing deals🤑 in up-and-coming areas within minutes ⏱️ to support their journey of financial freedom.')



####################################################
#                      TABS                         #
####################################################
tab1, tab2 = st.tabs(["Calculator", "Python Code"])
#|------------------METRICS-------------------|#
with tab1:
    col1, col2, col3 = st.columns([1,1,2])

    # inputs
    param_sale_price = col1.number_input("Sale price", min_value=0, max_value=10000000, value=400000, step=10000, help="Enter the value of your house, or the amount you would like to sell it for. This amount may represent what you would receive in a traditional sale, before paying agent commissions.")
    param_down_payment_rate = col2.number_input("Down payment rate", min_value=0, max_value=100, value=10, step=1, help="This is the amount you want to receive upfront. It can range from $0 to whatever portion of the sale price you need to make the deal worthwhile.")
    param_annual_interest_rate = col1.number_input("Interest rate", min_value=0, max_value=100, value=5, step=1, help="Enter the interest rate that you would like to charge for financing the remainder of the sale price (the portion not received as a down payment). The interest rate gives the sale its investment component, which would not be there in a traditional sale.")
    param_loan_term_years = col2.number_input("Loan Term (Years)", min_value=0, max_value=50, value=30, step=1, help="This is the timeframe in which you want the loan to be repaid, and is referred to as the amortization period. Monthly payments during this period include a mix of principal and interest (unless you include an “Interest Only” period). The Loan Term is most commonly used to control the amount of the monthly payment, since there are other ways to control when the loan actually ends (e.g. with the “Balloon” option).")

    # options
    param_balloon = col1.toggle("Balloon", value=True, help="Selecting this option allows you to input when you want the loan paid off. The balloon cuts off amortization and makes everything due at the time of the balloon. Sellers use a balloon to control the length of time they want income, as well as when the rest of their principal is due.")
    if param_balloon:
        balloon_due_years = col1.number_input("Balloon Due in (Years)", min_value=0, max_value=50, value=5, step=1, help="Selecting both options allows you to configure a scenario where you only receive interest for some time, and then a mix of principal and interest until the time of the balloon, at which point the remainder of the loan is paid off.")
    else:
        balloon_due_years = None
    param_interest_only = col1.toggle("Interest only", value=True, help="Selecting this option allows you to control the length of time for which you will receive interest only. During this period, there is no principal paydown, which means that the loan amount does not go down. This can be great as an income stream for the seller, while providing the buyer a period of increased affordability.")
    if param_interest_only:
        interest_only_years = col1.number_input("Interest Only for (Years)", min_value=0, max_value=100, value=1, step=1, help="Selecting both options allows you to configure a scenario where you only receive interest for some time, and then a mix of principal and interest until the time of the balloon, at which point the remainder of the loan is paid off.")
    else:
        interest_only_years = 0

    #|---------------RESULTS--------------#
    result = seller_financing_calculator(param_sale_price, param_down_payment_rate, param_annual_interest_rate, param_loan_term_years, balloon_due_years, interest_only_years)

    # output
    down_payment = result["Down Payment"]
    balloon_amount = result["Balloon Amount"]
    monthly_income_interest_only = result["Monthly Payment Interest Only"]
    monthly_income_non_interest_only = result["Monthly Payment Non Interest Only"]
    total_interest_paid = result["Total Interest Paid"]
    total_payment_amount = result["Total Payment Amount"]
    seller_total_payment = total_payment_amount + down_payment

    # table
    df = pd.DataFrame(result["Amortization Table"])
    df.loc[df['Month'] == 60, 'Remaining Balance'] = 0
    for c in list(df.columns)[1:]:
        # df[c] = df[c].apply(lambda x: '{:,.2f}'.format(x)) # str
        df[c] = df[c].apply(lambda x: round(x, 2))

    # chart
    labels = ['Payment Amount', 'Interest Amount']
    values = [total_payment_amount, total_interest_paid]

    # pull is given as a fraction of the pie radius
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0.2], textinfo='label+percent')])
    col3.plotly_chart(fig)

    col1, col2 = st.columns(2)
    col1.markdown('### Summary')
    col1.write("Down payment: ${:0,.0f}".format(down_payment))
    col1.write("Balloon amount: ${:0,.0f}".format(balloon_amount))
    col1.write("Monthly Income During Interest Only: ${:0,.0f}".format(monthly_income_interest_only))
    col1.write("Monthly Income After Interest Onlyt: ${:0,.0f}".format(monthly_income_non_interest_only))
    col1.write("Total Interest Paid: ${:0,.0f}".format(total_interest_paid))
    col1.write("Total Payment Amount: ${:0,.0f}".format(total_payment_amount))
    col1.write("Seller Grand Total: ${:0,.0f}".format(seller_total_payment))

    col2.markdown('### Amoritization Schedule')
    col2.write(df)


with tab2:
    st.code(
        '''def seller_financing_calculator(sale_price, down_payment_rate, annual_interest_rate, loan_term_years, balloon_due_years=None, interest_only_years=None):
    # Calculate the initial loan amount
    down_payment = int(sale_price * (down_payment_rate/100))
    loan_amount = sale_price - down_payment
    
    # Monthly interest rate
    monthly_interest_rate = annual_interest_rate / 100 / 12
    # Total number of payments
    total_payments = loan_term_years * 12
    
    # Calculate the monthly payment for a fully amortizing loan
    if monthly_interest_rate > 0:
        monthly_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_payments)
    else:
        monthly_payment = loan_amount / total_payments
    
    # Create amortization table
    amortization_table = []
    balance = loan_amount
    for month in range(1, total_payments + 1):
        interest_payment = balance * monthly_interest_rate
        if interest_only_years and month <= interest_only_years * 12:
            principal_payment = 0
            monthly_payment_during_interest_only = loan_amount * monthly_interest_rate
            amortization_table.append([month, monthly_payment_during_interest_only, interest_payment, principal_payment, balance])
        else:
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment
            amortization_table.append([month, monthly_payment, interest_payment, principal_payment, max(balance, 0)])
        
        if balloon_due_years and month == balloon_due_years * 12:
            balloon_payment = balance
            amortization_table.append([month, monthly_payment, interest_payment, principal_payment, 0])
            break

    # Convert amortization table to DataFrame for better display
    df_amortization_table = pd.DataFrame(amortization_table, columns=["Month", "Monthly Payment", "Interest", "Principal", "Remaining Balance"])
    
    # Total interest paid
    total_interest_paid = df_amortization_table["Interest"].sum()
    
    # Total payments
    total_payments_made = df_amortization_table["Monthly Payment"].sum() + (balloon_payment if balloon_due_years else 0)
    
    return {
        "Down Payment": down_payment,
        "Balloon Amount": df_amortization_table.iloc[-2]['Remaining Balance'],
        "Monthly Payment Interest Only": round(df_amortization_table.iloc[0]['Monthly Payment'], 2),
        "Monthly Payment Non Interest Only": round(df_amortization_table.iloc[-1]['Monthly Payment'], 2),
        "Monthly Payment": round(monthly_payment, 2),
        "Total Interest Paid": round(total_interest_paid, 2),
        "Total Payment Amount": round(total_payments_made, 2),
        "Amortization Table": df_amortization_table.iloc[:-1]
    }
''', 
        language='python')