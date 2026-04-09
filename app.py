import streamlit as st
import pandas as pd
from datetime import date
import database as db
import matplotlib.pyplot as plt

st.set_page_config(page_title="Expense Tracker", page_icon="💸")
db.create_table()

st.title("💸 Simple Expense Tracker")

# ====================================
# BULK EXPENSE ENTRY
# ====================================
st.subheader("Add Expenses (Bulk Entry)")

categories = [
    "Food", "Transport", "Appliance", "Wear", "Gadget",
    "Donation", "Investment", "Gift", "Repairs", "Other"
]

if "expense_table" not in st.session_state:
    st.session_state.expense_table = pd.DataFrame({
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Comment": [""],
        "Date": [None]
    })

edited_df = st.data_editor(
    st.session_state.expense_table,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Item": st.column_config.TextColumn("Item", required=True),
        "Amount": st.column_config.NumberColumn(
            "Amount (₦)", min_value=0.0, step=100.0, required=True
        ),
        "Category": st.column_config.SelectboxColumn(
            "Category", options=categories, required=True
        ),
        "Comment": st.column_config.TextColumn("Comment (optional)"),
        "Date": st.column_config.DateColumn("Date (optional)", required=False),
    }
)

st.session_state.expense_table = edited_df

# LIVE TOTAL
live_total = edited_df["Amount"].fillna(0).sum()
st.metric("💰 Current Total (Not Yet Saved)", f"₦{live_total:,.2f}")

# SAVE
if st.button("💾 Save All Expenses"):
    saved = 0
    for _, row in edited_df.iterrows():
        if not row["Item"] or row["Amount"] <= 0:
            continue

        expense_date = (
            str(row["Date"]) if pd.notna(row["Date"]) else str(date.today())
        )

        note = row["Item"]
        if row["Category"] == "Other" and row["Comment"]:
            note = f"{row['Item']} — {row['Comment']}"

        db.add_expense(
            amount=row["Amount"],
            category=row["Category"],
            date=expense_date,
            note=note
        )
        saved += 1

    st.success(f"✅ {saved} expenses saved!")
    st.session_state.expense_table = st.session_state.expense_table.iloc[0:0]

# ====================================
# ANALYTICS SECTION
# ====================================
st.divider()
st.header("📊 Analytics")

df = db.fetch_expenses_df()

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.to_period("W").astype(str)
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # CATEGORY PIE
    st.subheader("Spending by Category")
    cat_df = df.groupby("category")["amount"].sum()
    st.pyplot(cat_df.plot(kind="pie", autopct="%1.1f%%", ylabel="").figure)

    # WEEKLY LINE
    st.subheader("Weekly Spending Trend")
    week_df = df.groupby("week")["amount"].sum().reset_index()
    st.line_chart(week_df, x="week", y="amount")

    # MONTHLY BAR
    st.subheader("Monthly Spending")
    month_df = df.groupby("month")["amount"].sum().reset_index()
    st.bar_chart(month_df, x="month", y="amount")

else:
    st.info("No saved data yet for analytics.")

# ====================================
# EXPORT SECTION
# ====================================
st.divider()
st.header("📤 Export Data")

if not df.empty:
    excel_file = "expenses.xlsx"
    df_export = df.rename(columns={
        "date": "Date",
        "category": "Category",
        "amount": "Amount",
        "note": "Item / Comment"
    })

    st.download_button(
        label="📥 Download Excel File",
        data=df_export.to_excel(index=False, engine="openpyxl"),
        file_name=excel_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("No data available to export.")
