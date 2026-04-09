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
# Initialize session table
# ------------------------------------
if "expense_table" not in st.session_state:
    st.session_state.expense_table = pd.DataFrame({
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Comment": [""],
        "Date": [None]
    })

# ------------------------------------
# Editable table
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
        "Comment": st.column_config.TextColumn(
            "Comment (optional)"
        ),
        "Date": st.column_config.DateColumn(
            "Date (optional)", required=False
        )
    }
)

# ------------------------------------
# Auto S/N (computed only)
# ------------------------------------
display_df = edited_df.copy()
display_df.insert(0, "S/N", range(1, len(display_df) + 1))

st.session_state.expense_table = edited_df

# ------------------------------------
# LIVE TOTAL (updates instantly)
# ------------------------------------
live_total = edited_df["Amount"].fillna(0).sum()

st.markdown("### 💰 Live Total")
st.metric("Current Total", f"₦{live_total:,.2f}")

# ------------------------------------
# Save to database
# ------------------------------------
if st.button("💾 Save All Expenses"):
    saved = 0

    for _, row in edited_df.iterrows():
        if not row["Item"] or row["Amount"] <= 0:
            continue

        final_date = (
            str(row["Date"]) if pd.notna(row["Date"]) else str(date.today())
        )

        # Build note intelligently
        note = row["Item"]
        if row["Category"] == "Other" and row["Comment"]:
            note = f"{row['Item']} — {row['Comment']}"

        db.add_expense(
            amount=row["Amount"],
            category=row["Category"],
            date=final_date,
            note=note
        )
        saved += 1

    st.success(f"✅ {saved} expenses saved successfully!")

    # Reset table
    st.session_state.expense_table = pd.DataFrame({
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Comment": [""],
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
        expenses, columns=["Date", "Category", "Amount", "Item / Comment"]
    )
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No expenses saved yet.")
