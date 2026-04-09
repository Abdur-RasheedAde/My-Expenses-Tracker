import streamlit as st
from datetime import date
import database as db

st.set_page_config(page_title="Expense Tracker", page_icon="💸")
db.create_table()

st.title("💸 Simple Expense Tracker")

st.subheader("Add New Expense")
amount = st.number_input("Amount", min_value=0.0, step=100.0)
category = st.selectbox("Category", ["Food", "Transport", "Rent", "Data", "Others"])
expense_date = st.date_input("Date", value=date.today())
note = st.text_input("Note (optional)")

if st.button("Save Expense"):
    db.add_expense(amount, category, str(expense_date), note)
    st.success("✅ Expense saved!")

st.divider()
st.subheader("Summary")
total = db.total_expense()
st.metric("Total Spending", f"₦{total:,.2f}")

st.divider()
st.subheader("Expense History")
expenses = db.fetch_expenses()
if expenses:
    for e in expenses:
        st.write(f"📅 {e[0]} | **{e[1]}** | ₦{e[2]:,.2f} — {e[3]}")
else:
    st.info("No expenses yet.")
