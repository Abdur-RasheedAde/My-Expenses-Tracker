import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import io
import database as db

# ==========================
# APP CONFIG
# ==========================
st.set_page_config(page_title="Expense Tracker", page_icon="💸")
db.create_table()

st.title("💸 Simple Expense Tracker")

# ==========================
# BULK EXPENSE ENTRY
# ==========================
st.subheader("Add Expenses (Bulk Entry)")

categories = [
    "Food", "Transport", "Appliance", "Wear", "Gadget",
    "Donation", "Investment", "Gift", "Repairs", "Other"
]

# Initialize table in session
if "expense_table" not in st.session_state:
    st.session_state.expense_table = pd.DataFrame({
        "Item": [""],
        "Amount": [0.0],
        "Category": ["Food"],
        "Comment": [""],
        "Date": [None]
    })

# Editable table (KEY is critical)
edited_df = st.data_editor(
    st.session_state.expense_table,
    num_rows="dynamic",
    use_container_width=True,
    key="expense_editor",
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

# ==========================
# LIVE TOTAL
# ==========================
live_total = edited_df["Amount"].fillna(0).sum()
st.metric("💰 Current Total (Not Yet Saved)", f"₦{live_total:,.2f}")

# ==========================
# ACTION BUTTONS
# ==========================
col1, col2 = st.columns(2)

with col1:
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

        st.success(f"✅ {saved} expenses saved successfully!")

        # Reset table after save
        st.session_state.expense_table = pd.DataFrame({
            "Item": [""],
            "Amount": [0.0],
            "Category": ["Food"],
            "Comment": [""],
            "Date": [None]
        })
        st.rerun()

with col2:
    if st.button("🧹 Clear Current Entries"):
        st.session_state.expense_table = pd.DataFrame({
            "Item": [""],
            "Amount": [0.0],
            "Category": ["Food"],
            "Comment": [""],
            "Date": [None]
        })
        st.rerun()

# ==========================
# ANALYTICS
# ==========================
st.divider()
st.header("📊 Analytics")

df = db.fetch_expenses_df()

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])

    # Weekly labels → Wk-01
    df["week_no"] = df["date"].dt.isocalendar().week
    df["week_label"] = df["week_no"].apply(lambda x: f"Wk-{x:02d}")

    # Monthly labels → Jan
    df["month_no"] = df["date"].dt.month
    df["month_label"] = df["date"].dt.strftime("%b")

    # ---------- PIE CHART (SMALL & FIXED) ----------
    st.subheader("Spending by Category")
    cat_df = df.groupby("category")["amount"].sum()

    fig, ax = plt.subplots(figsize=(3.2, 3.2), dpi=90)
    ax.pie(
        cat_df.values,
        labels=cat_df.index,
        autopct="%1.0f%%",
        startangle=90,
        textprops={"fontsize": 9}
    )
    ax.axis("equal")
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)

    # ---------- WEEKLY ----------
    st.subheader("Weekly Spending Trend")
    week_df = (
        df.groupby(["week_no", "week_label"], as_index=False)["amount"]
        .sum()
        .sort_values("week_no")
    )
    st.line_chart(week_df, x="week_label", y="amount")

    # ---------- MONTHLY ----------
    st.subheader("Monthly Spending")
    month_df = (
        df.groupby(["month_no", "month_label"], as_index=False)["amount"]
        .sum()
        .sort_values("month_no")
    )
    st.bar_chart(month_df, x="month_label", y="amount")

else:
    st.info("No saved data yet for analytics.")

# ==========================
# EXPORT TO EXCEL
# ==========================
st.divider()
st.header("📤 Export Data")

if not df.empty:
    df_export = df.rename(columns={
        "date": "Date",
        "category": "Category",
        "amount": "Amount",
        "note": "Item / Comment"
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False)

    st.download_button(
        label="📥 Download Excel File",
        data=buffer.getvalue(),
        file_name="expenses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("No data available to export.")
