import streamlit as st
import pandas as pd
from datetime import date
import database as db

st.set_page_config(page_title="Expense Tracker", page_icon="💸")
db.create_table()

st.title("💸 Simple Expense Tracker")

st.subheader("Add Expenses (Bulk Entry)")

# -----------------------------
# 1. Expense Entry Table
# -----------------------------
categories = [
    "Food", "Transport", "Appliance", "Wear", "Gadget",
    "Donation", "Investment", "Gift", "Repairs", "Other"
]

if "expense_table" not in st.session_state:
    st.session_state.expense_table = pd.DataFrame({
        "S/N": [1],
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Date": [date.today()]
    })

edited_df = st.data_editor(
    st.session_state.expense_table,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "S/N": st.column_config.NumberColumn(
            "S/N", disabled=True
        ),
        "Item": st.column_config.TextColumn(
            "Item", required=True
        ),
        "Amount": st.column_config.NumberColumn(
            "Amount (₦)", min_value=0.0, step=100.0, required=True
        ),
        "Category": st.column_config.SelectboxColumn(
            "Category",
            options=categories,
            required=True
        ),
        "Date": st.column_config.DateColumn(
            "Date", required=True
        )
    }
)

# Re-number S/N automatically
edited_df["S/N"] = range(1, len(edited_df) + 1)
st.session_state.expense_table = edited_df

# -----------------------------
# 2. Custom Category Input
# -----------------------------
custom_category = st.text_input(
    "Add custom category (optional)",
    help="Use this if category is not in the list"
)

# -----------------------------
# 3. Save All Expenses
# -----------------------------
if st.button("💾 Save All Expenses"):
    saved_rows = 0

    for _, row in edited_df.iterrows():
        category = (
            custom_category
            if row["Category"] == "Other" and custom_category
            else row["Category"]
        )

        if row["Item"] and row["Amount"] > 0:
            db.add_expense(
                amount=row["Amount"],
                category=category,
                date=str(row["Date"]),
                note=row["Item"]
            )
            saved_rows += 1

    st.success(f"✅ {saved_rows} expenses saved successfully!")

    # Clear table after save
    st.session_state.expense_table = pd.DataFrame({
        "S/N": [1],
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Date": [date.today()]
    })

# -----------------------------
# 4. Summary Section
# -----------------------------
st.divider()
st.subheader("Summary")

total = db.total_expense()
st.metric("Total Spending", f"₦{total:,.2f}")

# -----------------------------
# 5. Expense History
# -----------------------------
st.divider()
st.subheader("Expense History")

expenses = db.fetch_expenses()
if expenses:
    history_df = pd.DataFrame(
        expenses,
        columns=["Date", "Category", "Amount", "Item"]
    )
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No expenses yet.")
