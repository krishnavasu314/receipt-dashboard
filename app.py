import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.title("Receipt/Bill Uploader & Analyzer")

# Upload section
st.header("Upload a Receipt or Bill")
uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf", "txt"])
submit = st.button("Submit")
if uploaded_file is not None and submit:
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    response = requests.post(f"{API_URL}/upload", files=files)
    if response.status_code == 200:
        result = response.json()
        if result.get("parsed", {}).get("vendor") == "Unknown Vendor" and result.get("parsed", {}).get("amount") == 0.0:
            st.warning("Warning: We could not extract receipt data from your file. Please check the file or enter the details manually.")
        st.success(f"Uploaded and parsed: {uploaded_file.name}")
        st.json(result)
    else:
        st.error(f"Upload failed: {response.text}")

# Search and sort section
st.header("Receipts Table")
search_query = st.text_input("Search receipts (vendor, category, etc.)")
sort_field = st.selectbox("Sort by", ["amount", "date", "vendor"])
sort_order = st.radio("Order", ["desc", "asc"])

# Range filters
col1, col2 = st.columns(2)
with col1:
    date_from = st.date_input("Date from", value=None, key="date_from")
    date_to = st.date_input("Date to", value=None, key="date_to")
with col2:
    amount_from = st.number_input("Amount from", value=0.0, step=1.0, key="amount_from")
    amount_to = st.number_input("Amount to", value=0.0, step=1.0, key="amount_to")

if search_query:
    resp = requests.get(f"{API_URL}/search", params={"q": search_query})
else:
    resp = requests.get(f"{API_URL}/sort", params={"field": sort_field, "order": sort_order})

edit_id = st.session_state.get("edit_id", None)

if resp.status_code == 200:
    data = resp.json()
    if data:
        df = pd.DataFrame(data)
        # Show warning if any row is likely unparsed
        if any((df["vendor"] == "Unknown Vendor") & (df["amount"] == 0.0)):
            st.warning("Some files could not be parsed as receipts. Please check and edit them manually.")
        # Apply range filters
        if date_from:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df[df["date"] >= pd.to_datetime(date_from)]
        if date_to:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df[df["date"] <= pd.to_datetime(date_to)]
        if amount_from:
            df = df[df["amount"] >= amount_from]
        if amount_to and amount_to > 0:
            df = df[df["amount"] <= amount_to]
        st.dataframe(df)
        # Export buttons
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="receipts.csv",
            mime="text/csv"
        )
        json_data = df.to_json(orient="records")
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="receipts.json",
            mime="application/json"
        )
        for i, row in df.iterrows():
            with st.expander(f"Edit Receipt ID {row['id']}"):
                with st.form(f"edit_form_{row['id']}"):
                    vendor = st.text_input("Vendor", value=row["vendor"])
                    date = st.text_input("Date", value=row["date"])
                    amount = st.number_input("Amount", value=row["amount"], format="%f")
                    category = st.text_input("Category", value=row["category"] if pd.notnull(row["category"]) else "")
                    submit_edit = st.form_submit_button("Save Changes")
                    if submit_edit:
                        update_data = {
                            "vendor": vendor,
                            "date": date,
                            "amount": amount,
                            "category": category
                        }
                        patch_resp = requests.patch(f"{API_URL}/update/{row['id']}", json=update_data)
                        if patch_resp.status_code == 200:
                            st.success("Receipt updated!")
                            st.experimental_rerun()
                        else:
                            st.error(f"Update failed: {patch_resp.text}")
    else:
        st.info("No receipts found.")
else:
    st.error("Failed to fetch receipts.")

# Stats section
st.header("Statistics & Insights")
stats_resp = requests.get(f"{API_URL}/stats")
if stats_resp.status_code == 200:
    stats = stats_resp.json()
    st.metric("Total Spend", stats["total"])
    st.metric("Mean Spend", stats["mean"])
    st.metric("Median Spend", stats["median"])
    st.metric("Mode Spend", stats["mode"])
    st.subheader("Vendor Frequency")
    vendor_freq = stats["vendor_frequency"]
    if vendor_freq:
        freq_df = pd.DataFrame(list(vendor_freq.items()), columns=["Vendor", "Count"])
        st.bar_chart(freq_df.set_index("Vendor"))
    else:
        st.info("No vendor data yet.")
    # Time-series spend chart
    st.subheader("Monthly Spend Trend")
    # Fetch all receipts for time-series
    receipts_resp = requests.get(f"{API_URL}/receipts")
    if receipts_resp.status_code == 200:
        receipts = receipts_resp.json()
        if receipts:
            df = pd.DataFrame(receipts)
            # Parse date and group by month
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])
            df["month"] = df["date"].dt.to_period("M").astype(str)
            monthly = df.groupby("month")["amount"].sum().reset_index()
            monthly = monthly.sort_values("month")
            monthly = monthly.set_index("month")
            st.line_chart(monthly)
        else:
            st.info("No receipts for time-series chart.")
    else:
        st.error("Failed to fetch receipts for time-series chart.")
else:
    st.error("Failed to fetch statistics.") 