import pandas as pd
import numpy as np
import streamlit as st
import numpy_financial as npf
import plotly.graph_objects as go


####################################################
#                      PARAMS                      #
####################################################
st.set_page_config(layout="wide")


####################################################
#                   FUNCTION                       #
####################################################
def calculate_monthly_payment(principal, annual_interest_rate, term_years):
    monthly_interest_rate = annual_interest_rate / 100 / 12
    number_of_payments = term_years * 12
    if monthly_interest_rate == 0:
        return principal / number_of_payments
    else:
        return principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / ((1 + monthly_interest_rate) ** number_of_payments - 1)

def calculate_balloon_payment(principal, annual_interest_rate, term_years, balloon_years):
    monthly_interest_rate = annual_interest_rate / 100 / 12
    number_of_payments = term_years * 12
    balloon_payments = balloon_years * 12
    monthly_payment = calculate_monthly_payment(principal, annual_interest_rate, term_years)
    remaining_balance = npf.pv(monthly_interest_rate, number_of_payments - balloon_payments, -monthly_payment, 0)
    return remaining_balance

def optimize_terms(
        listing_price, 
        min_down_payment_pct, 
        max_down_payment_pct, 
        min_interest_rate, 
        max_interest_rate, 
        rental_income, 
        monthly_expenses, 
        balloon_years, 
        balloon_adjustable=False, 
        required_seller_earnings_pct=5):
    optimal_terms = None
    target_cash_on_cash_return = 0.07  # 7%
    required_seller_earnings = listing_price * (1 + required_seller_earnings_pct / 100)
    
    def search_optimal_terms(balloon_years_range):
        nonlocal optimal_terms, max_seller_earnings
        for down_payment_pct in range(min_down_payment_pct, max_down_payment_pct + 1):
            for interest_rate in range(min_interest_rate, max_interest_rate + 1):
                for offer_price in range(int(listing_price * 0.8), listing_price + 1, 1000):
                    for balloon_years in balloon_years_range:
                        down_payment = offer_price * (down_payment_pct / 100)
                        loan_amount = offer_price - down_payment
                        monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, 30)
                        annual_cash_flow = (rental_income - monthly_payment - monthly_expenses) * 12
                        initial_cash_investment = down_payment + (monthly_expenses * 12)
                        cash_on_cash_return = annual_cash_flow / initial_cash_investment

                        # Calculate total payments including balloon payment
                        total_payments = (monthly_payment * balloon_years * 12) + calculate_balloon_payment(loan_amount, interest_rate, 30, balloon_years)
                        seller_earnings = down_payment + total_payments

                        if cash_on_cash_return >= target_cash_on_cash_return and seller_earnings >= required_seller_earnings:
                            if seller_earnings > max_seller_earnings:
                                max_seller_earnings = seller_earnings
                                optimal_terms = {
                                    'offer_price': round(offer_price),
                                    'down_payment_pct': round(down_payment_pct),
                                    'interest_rate': round(interest_rate, 4),
                                    'monthly_payment': round(monthly_payment, 4),
                                    'monthly_cash_flow': round(round(annual_cash_flow / 12), 4),
                                    'cash_on_cash_return': round(cash_on_cash_return, 4),
                                    'total_payments': round(total_payments, 4),
                                    'seller_earnings': round(seller_earnings, 4),
                                    'balloon_years': balloon_years
                                }

    # First, search with a fixed 5-year balloon period
    max_seller_earnings = 0
    search_optimal_terms([balloon_years])

    # If no optimal terms found, search with flexible balloon period (5 to 10 years)
    if (not optimal_terms) and (balloon_adjustable == True):
        search_optimal_terms(range(5, 11))

    return optimal_terms


####################################################
#                      APP                         #
####################################################
st.title('Best Terms 📈')
st.subheader('Enter deal details to INSTANTLY calculate best offer terms')
st.markdown('Want to use the AI model? Check out 👉 [Coffee Clozers](https://bit.ly/3EJRAa5) 🏡, we help real estate investors find cash flowing deals🤑 in up-and-coming areas within minutes ⏱️ to support their journey of financial freedom.')

import hmac


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()


####################################################
#                      TABS                         #
####################################################
tab1, tab2 = st.tabs(["Calculator", "Code"])
#|------------------METRICS-------------------|#
with tab1:
    main1, main2 = st.columns([2,2])
    main1.markdown('## Inputs')
    param_list_price = main1.number_input("List price", min_value=0, max_value=10000000, value=359900, step=10000)

    # col1, col2, col3 = st.columns([1,1,2])
    param_rental_income = main1.number_input("Rental Income", min_value=0, max_value=100000, value=2000, step=100)
    param_monthly_expenses = main1.number_input("Monthly Expenses", min_value=0, max_value=100000, value=630, step=10)

    with main1.expander("Additional Parameters", expanded=False):
        col1, col2 = st.columns(2)
        param_min_down_payment_pct = col1.number_input("Minimum Down Payment %", min_value=0, max_value=100, value=10, step=1)
        param_max_down_payment_pct = col2.number_input("Maximum Down Payment %", min_value=0, max_value=100, value=30, step=1)
        param_min_interest_rate_pct = col1.number_input("Minimum Interest Rate %", min_value=0, max_value=100, value=1, step=1)
        param_max_interest_rate_pct = col2.number_input("Maximum Interest Rate %", min_value=0, max_value=100, value=7, step=1)
        param_balloon_years = col1.number_input("Balloon Years", min_value=0, max_value=30, value=5, step=1)
        param_balloon_adjustable = col2.checkbox("Balloon Adjustable", value=True)
        param_required_seller_earnings_prct = col1.number_input("Required Seller Earnings %", min_value=0, max_value=100, value=5, step=1)

    param_run_model = st.button("Run", type="primary")


    if param_run_model:
        best_terms = optimize_terms(
            listing_price=param_list_price,
            min_down_payment_pct=param_min_down_payment_pct,
            max_down_payment_pct=param_max_down_payment_pct, 
            min_interest_rate=param_min_interest_rate_pct, 
            max_interest_rate=param_max_interest_rate_pct, 
            rental_income=param_rental_income, 
            monthly_expenses=param_monthly_expenses, 
            balloon_years=param_balloon_years, 
            balloon_adjustable=param_balloon_adjustable,
            required_seller_earnings_pct=param_required_seller_earnings_prct
        )

        main2.markdown('## Best Terms')
        if best_terms != None:
            col1, col2 = main2.columns(2)
            # calcs
            offer_price_diff = best_terms["offer_price"] - param_list_price
            interest_amount = int(best_terms["seller_earnings"] - best_terms["offer_price"])
            
            # terms
            main2.markdown('### Terms')
            col1, col2 = main2.columns(2)
            col1.write('Offer price: ${:0,.0f}'.format(best_terms["offer_price"]))
            col2.write('Down payment rate: {}%'.format(best_terms["down_payment_pct"]))
            col2.write('Interest rate: {}%'.format(best_terms["interest_rate"]))
            col2.write('Balloon years: {}'.format(best_terms["balloon_years"]))

            main2.markdown('### Results')
            col1, col2 = main2.columns(2)
            col1.markdown('#### Buyer')
            col1.write('Monthly cash flow: ${:0,.0f}'.format(best_terms["monthly_cash_flow"]))
            col1.write('Cash on cash return: {}%'.format(round(best_terms["cash_on_cash_return"] * 100)))
            # col1.write('Monthly payment: ${:0,.0f}'.format(best_terms["monthly_payment"]))
            
            col2.markdown('#### Seller')
            col2.write('Offer price: ${:0,.0f}'.format(best_terms["offer_price"]))
            col2.write('Interest: ${:0,.0f}'.format(interest_amount))
            col2.write('Seller earnings: ${:0,.0f}'.format(int(best_terms["seller_earnings"])))

        else:
            main2.write('No ideal terms with current constraints')