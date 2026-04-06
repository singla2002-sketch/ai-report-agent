import streamlit as st

# ---------------- SAMPLE DATA (YOU CAN REPLACE LATER) ---------------- #

data = {
    "fusion_repository": [
        {
            "report_name": "AP Invoice Report",
            "module": "Accounts Payable",
            "description": "Fetch invoice details with supplier",
            "sql": "SELECT * FROM AP_INVOICES_ALL ai JOIN AP_SUPPLIERS s ON ai.vendor_id = s.vendor_id",
            "tables": ["AP_INVOICES_ALL", "AP_SUPPLIERS"],
            "parameters": ["invoice_date", "org_id"]
        },
        {
            "report_name": "AR Aging Report",
            "module": "Accounts Receivable",
            "description": "Customer outstanding balances aging",
            "sql": "SELECT * FROM AR_AGING",
            "tables": ["AR_AGING"],
            "parameters": ["customer_id"]
        }
    ],
    "ebs_repository": [
        {
            "report_name": "EBS User Report",
            "module": "System Admin",
            "description": "Fetch all users",
            "sql": "SELECT * FROM FND_USER",
            "tables": ["FND_USER"],
            "parameters": []
        }
    ],
    "fusion_valid_tables": ["AP_INVOICES_ALL", "AP_SUPPLIERS", "AR_AGING"],
    "ebs_valid_tables": ["FND_USER"]
}

# ---------------- UI ---------------- #

st.set_page_config(page_title="AI Report Agent", layout="wide")

st.title("🤖 AI Report Intelligence Agent")
st.write("Search Oracle reports without dependency on functional team")

# Sidebar
st.sidebar.header("🔍 Filters")

instance = st.sidebar.selectbox("Select Instance", ["fusion", "ebs"])
client_name = st.sidebar.text_input("Client Name (optional)")
search_query = st.sidebar.text_input("Search Report")

# Load data
if instance == "fusion":
    repo = data["fusion_repository"]
    valid_tables = data["fusion_valid_tables"]
else:
    repo = data["ebs_repository"]
    valid_tables = data["ebs_valid_tables"]

# Search logic
def search_reports(query, repo):
    results = []
    for r in repo:
        score = 0
        if query.lower() in r["description"].lower():
            score += 0.5
        if query.lower() in r["report_name"].lower():
            score += 0.5

        if score > 0:
            r["score"] = score
            results.append(r)

    return sorted(results, key=lambda x: x["score"], reverse=True)

# Apply search
if search_query:
    results = search_reports(search_query, repo)
else:
    results = repo

# Confidence filter
filtered_results = [r for r in results if r.get("score", 1) >= 0.75]

# Display results
st.subheader("📊 Results")

if not filtered_results:
    st.error("No verified report found in repository")
else:
    for r in filtered_results:
        with st.expander(f"📄 {r['report_name']}"):

            st.write(f"**Module:** {r['module']}")
            st.write(f"**Description:** {r['description']}")
            st.write(f"**Tables:** {', '.join(r['tables'])}")
            st.write(f"**Parameters:** {', '.join(r['parameters'])}")

            # Schema validation
            if not all(t in valid_tables for t in r["tables"]):
                st.error("❌ Invalid tables for selected instance")
            else:
                st.success("✅ Schema Valid")

            # SQL
            st.code(r["sql"], language="sql")

            # Download
            st.download_button(
                "⬇️ Download SQL",
                data=r["sql"],
                file_name=f"{r['report_name']}.sql"
            )
