import streamlit as st
import pandas as pd
import os
import hashlib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# --- File Paths ---
USER_DB = "users.csv"
EXPENSE_FILE = "expenses.csv"
SALARY_FILE = "salary.txt"

# --- Initialize Files ---
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["Username", "Password", "Full Name", "Email"]).to_csv(USER_DB, index=False)

if not os.path.exists(EXPENSE_FILE):
    pd.DataFrame(columns=["Date", "Sector", "Amount"]).to_csv(EXPENSE_FILE, index=False)

if not os.path.exists(SALARY_FILE):
    with open(SALARY_FILE, "w") as f:
        f.write("0")

# --- Helper Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_user(username, password):
    users = pd.read_csv(USER_DB)
    hashed_password = hash_password(password)
    user_row = users[(users["Username"] == username) & (users["Password"] == hashed_password)]
    return not user_row.empty

def add_user(username, password, full_name, email):
    users = pd.read_csv(USER_DB)
    if username in users["Username"].values:
        return False, "Username already exists."
    new_user = {"Username": username, "Password": hash_password(password), "Full Name": full_name, "Email": email}
    users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
    users.to_csv(USER_DB, index=False)
    clear_expenses()
    save_salary(0)
    return True, "Account created successfully! Previous data cleared."

def load_expenses():
    return pd.read_csv(EXPENSE_FILE)

def save_expenses(df):
    df.to_csv(EXPENSE_FILE, index=False)

def add_expense(date, sector, amount):
    df = load_expenses()
    df = pd.concat([df, pd.DataFrame({"Date": [date], "Sector": [sector], "Amount": [amount]})], ignore_index=True)
    save_expenses(df)

def clear_expenses():
    pd.DataFrame(columns=["Date", "Sector", "Amount"]).to_csv(EXPENSE_FILE, index=False)

def load_salary():
    with open(SALARY_FILE, "r") as f:
        return float(f.read())

def save_salary(salary):
    with open(SALARY_FILE, "w") as f:
        f.write(str(salary))

def calculate_balance():
    salary = load_salary()
    total_expenses = load_expenses()["Amount"].sum()
    return salary - total_expenses

def plot_histogram():
    df = load_expenses()
    plt.figure(figsize=(10, 6))
    sns.histplot(df["Amount"], bins=10, kde=True)
    plt.title("Expense Distribution")
    plt.xlabel("Expense Amount")
    plt.ylabel("Frequency")
    st.pyplot()

def plot_pie_chart():
    df = load_expenses()
    sector_sums = df.groupby("Sector")["Amount"].sum()
    plt.figure(figsize=(8, 8))
    sector_sums.plot.pie(autopct='%1.1f%%', startangle=90, cmap="Set3")
    plt.title("Expenses by Sector")
    st.pyplot()

def plot_line_graph():
    df = load_expenses()
    df["Date"] = pd.to_datetime(df["Date"])
    daily_expenses = df.groupby("Date")["Amount"].sum()
    plt.figure(figsize=(10, 6))
    plt.plot(daily_expenses, marker='o')
    plt.title("Daily Expense Trends")
    plt.xlabel("Date")
    plt.ylabel("Total Expense")
    plt.grid()
    st.pyplot()

def predict_next_month():
    df = load_expenses()
    if df.empty or len(df["Amount"]) < 2:
        st.warning("Not enough data for prediction.")
        return
    df["Date"] = pd.to_datetime(df["Date"])
    df["Day"] = df["Date"].dt.day
    X = df["Day"].values.reshape(-1, 1)
    y = df["Amount"].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)

    # Predict expenses for the remaining days of the current month
    today = datetime.today()
    remaining_days = [today + timedelta(days=i) for i in range(1, 32 - today.day)]
    
    # Predict expenses for the next month
    next_month_start = today.replace(day=1) + timedelta(days=32)
    next_month_start = next_month_start.replace(day=1)
    next_month_days = [next_month_start + timedelta(days=i) for i in range(31)]
    
    remaining_days_nums = np.array([day.day for day in remaining_days]).reshape(-1, 1)
    next_month_days_nums = np.array([day.day for day in next_month_days]).reshape(-1, 1)
    
    remaining_predictions = model.predict(remaining_days_nums)
    next_month_predictions = model.predict(next_month_days_nums)
    
    st.subheader(translate("Remaining Days Predictions"))
    for day, pred in zip(remaining_days, remaining_predictions.flatten()):
        st.write(f"{day.date()}: ₹{round(pred, 2)}")

    st.subheader(translate("Next Month Predictions"))
    for day, pred in zip(next_month_days, next_month_predictions.flatten()):
        st.write(f"{day.date()}: ₹{round(pred, 2)}")

# --- Translation Function ---
translations = {
    "en": {
        "Login": "Login",
        "Sign Up": "Sign Up",
        "Create an Account": "Create an Account",
        "Username": "Username",
        "Password": "Password",
        "Full Name": "Full Name",
        "Email": "Email",
        "Enter Salary": "Enter Salary",
        "Save Salary": "Save Salary",
        "Add Expense": "Add Expense",
        "Date": "Date",
        "Sector": "Sector",
        "Amount": "Amount",
        "Expense Table": "Expense Table",
        "Balance": "Balance",
        "Visualizations": "Visualizations",
        "Future Predictions": "Future Predictions",
        "Remaining Days Predictions": "Remaining Days Predictions",
        "Next Month Predictions": "Next Month Predictions",
        "Expense added!": "Expense added!",
        "Dashboard cleared!": "Dashboard cleared!"
    },
    "hi": {
        "Login": "लॉग इन करें",
        "Sign Up": "साइन अप करें",
        "Create an Account": "खाता बनाएँ",
        "Username": "उपयोगकर्ता नाम",
        "Password": "पासवर्ड",
        "Full Name": "पूरा नाम",
        "Email": "ईमेल",
        "Enter Salary": "वेतन दर्ज करें",
        "Save Salary": "वेतन सहेजें",
        "Add Expense": "खर्च जोड़ें",
        "Date": "तारीख",
        "Sector": "खाता",
        "Amount": "राशि",
        "Expense Table": "खर्च तालिका",
        "Balance": "शेष राशि",
        "Visualizations": "दृश्य",
        "Future Predictions": "भविष्यवाणियां",
        "Remaining Days Predictions": "शेष दिनों की भविष्यवाणियां",
        "Next Month Predictions": "अगले महीने की भविष्यवाणियां",
        "Expense added!": "खर्च जोड़ा गया!",
        "Dashboard cleared!": "डैशबोर्ड साफ़ किया गया!"
    }
}

current_language = "en"

def translate(text):
    return translations[current_language].get(text, text)

# --- Streamlit App ---
def main():
    global current_language

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    st.sidebar.title(translate("Personal Finance Manager"))

    # Language toggle
    language = st.sidebar.selectbox("Language", ["English", "Hindi"])
    current_language = "hi" if language == "Hindi" else "en"

    if not st.session_state.logged_in:
        menu = [translate("Login"), translate("Sign Up")]
        choice = st.sidebar.selectbox(translate("Menu"), menu)

        if choice == translate("Sign Up"):
            st.subheader(translate("Create an Account"))
            full_name = st.text_input(translate("Full Name"))
            email = st.text_input(translate("Email"))
            username = st.text_input(translate("Username"))
            password = st.text_input(translate("Password"), type="password")
            if st.button(translate("Sign Up")):
                if not full_name or not email or not username or not password:
                    st.error(translate("All fields are required."))
                else:
                    success, message = add_user(username, password, full_name, email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        elif choice == translate("Login"):
            st.subheader(translate("Login"))
            username = st.text_input(translate("Username"))
            password = st.text_input(translate("Password"), type="password")
            if st.button(translate("Login")):
                if validate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(translate(f"Welcome, {username}!"))
                else:
                    st.error(translate("Invalid username or password."))
    else:
        st.sidebar.button(translate("Log Out"), on_click=lambda: logout_user())
        st.sidebar.header(translate("Set Your Salary"))
        salary = st.sidebar.number_input(translate("Enter Salary"), min_value=0.0)
        st.sidebar.button(translate("Save Salary"), on_click=lambda: save_salary(salary))

        st.subheader(translate("Add Expense"))
        date = st.date_input(translate("Date"))
        sector = st.text_input(translate("Sector"))
        amount = st.number_input(translate("Amount"), min_value=0.0)
        if st.button(translate("Add Expense")):
            add_expense(date, sector, amount)
            st.success(translate("Expense added!"))

        st.subheader(translate("Expense Table"))
        expense_df = load_expenses()
        st.dataframe(expense_df)

        st.subheader(translate("Balance"))
        st.write(f"₹{calculate_balance()}")

        st.subheader(translate("Visualizations"))
        plot_histogram()
        plot_pie_chart()
        plot_line_graph()

        st.subheader(translate("Future Predictions"))
        predict_next_month()

        if st.button(translate("Clear Dashboard")):
            clear_expenses()
            st.success(translate("Dashboard cleared!"))

def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = ""

if __name__ == "__main__":
    main()
