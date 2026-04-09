import streamlit as st
import pandas as pd
from datetime import date
import database as db

st.set_page_config(page_title="Expense Tracker", page_icon="💸")
db.create_table()

st.title("💸 Simple Expense Tracker")

st.subheader("Add Expenses (Bulk Entry)")

# ------------------------------------
# Categories
# ------------------------------------
categories = [
    "Food", "Transport", "Appliance", "Wear", "Gadget",
    "Donation", "Investment", "Gift", "Repairs", "Other"
]

# ------------------------------------
# Initialize table in session
# ------------------------------------
if "expense_table" not in st.session_state:
    st.session_state.expense_table = pd.DataFrame({
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Date": [None]
    })

# ------------------------------------
# Editable table (no S/N column yet)
# ------------------------------------
edited_df = st.data_editor(
    st.session_state.expense_table,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Item": st.column_config.TextColumn(
            "Item", required=True
        ),
        "Amount": st.column_config.NumberColumn(
            "Amount (₦)", min_value=0.0, step=100.0, required=True
        ),
        "Category": st.column_config.SelectboxColumn(
            "Category", options=categories, required=True
        ),
        "Date": st.column_config.DateColumn(
            "Date (optional)", required=False
        )
    }
)

# ------------------------------------
# Auto S/N (computed, not editable)
# ------------------------------------
edited_df.insert(0, "S/N", range(1, len(edited_df) + 1))

st.session_state.expense_table = edited_df.drop(columns=["S/N"])

# ------------------------------------
# LIVE TOTAL (no save button needed)
# ------------------------------------
live_total = edited_df["Amount"].fillna(0).sum()

st.markdown("### 💰 Live Total")
st.metric("Current Total", f"₦{live_total:,.2f}")

# ------------------------------------
# Custom category
# ------------------------------------
custom_category = st.text_input(
    "Add custom category (if Category = Other)",
    placeholder="e.g. School fees, Medical, Charity"
)

# ------------------------------------
# Save to database
# ------------------------------------
if st.button("💾 Save All Expenses"):
    saved = 0

    for _, row in edited_df.iterrows():
        if not row["Item"] or row["Amount"] <= 0:
            continue

        expense_date = (
            str(row["Date"]) if pd.notna(row["Date"]) else str(date.today())
        )

        final_category = (
            custom_category
            if row["Category"] == "Other" and custom_category
            else row["Category"]
        )

        db.add_expense(
            amount=row["Amount"],
            category=final_category,
            date=expense_date,
            note=row["Item"]
        )
        saved += 1

    st.success(f"✅ {saved} expenses saved successfully!")

    # reset table
    st.session_state.expense_table = pd.DataFrame({
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Date": [None]
    })

# ------------------------------------
# DATABASE SUMMARY
# ------------------------------------
st.divider()
st.subheader("Saved Expenses Summary")

total_db = db.total_expense()
st.metric("Total Saved Spending", f"₦{total_db:,.2f}")

# ------------------------------------
# Expense History
# ------------------------------------
st.subheader("Expense History")

expenses = db.fetch_expenses()
if expenses:
    history_df = pd.DataFrame(
        expenses, columns=["Date", "Category", "Amount", "Item"]
    )
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No expenses saved yet.")
