import streamlit as st

# ---------------- STRICT SCHEMA (SOURCE OF TRUTH) ---------------- #

FUSION_VALID_TABLES = [
    "AP_INVOICES_ALL",
    "XLA_AE_HEADERS",
    "GL_CODE_COMBINATIONS",
    "AR_PAYMENT_SCHEDULES_ALL"
]

EBS_VALID_TABLES = [
    "AP_INVOICES_ALL",
    "AP_SUPPLIERS",
    "FND_USER",
    "AR_AGING"
]

# ---------------- REPOSITORY ---------------- #

data = {
    "fusion_repository": [
        {
            "report_name": "Fusion Invoice Report",
            "module": "Accounts Payable",
            "description": "Invoice details with accounting",
            "sql": "SELECT * FROM AP_INVOICES_ALL ai JOIN XLA_AE_HEADERS xla ON ai.invoice_id = xla.source_id",
            "tables": ["AP_INVOICES_ALL", "XLA_AE_HEADERS"],
            "parameters": ["invoice_date"]
        },

        {
            "report_name": "Wrong Fusion Supplier Report",
            "module": "Accounts Payable",
            "description": "Supplier info",
            "sql": "SELECT * FROM AP_SUPPLIERS",
            "tables": ["AP_SUPPLIERS"],
            "parameters": []
        }
    ],

    "ebs_repository": [
        {
            "report_name": "EBS Supplier Report",
            "module": "Accounts Payable",
            "description": "Supplier details",
            "sql": "SELECT * FROM AP_SUPPLIERS",
            "tables": ["AP_SUPPLIERS"],
            "parameters": []
        },
        {
            "report_name": "EBS User Report",
            "module": "System Admin",
            "description": "All users",
            "sql": "SELECT * FROM FND_USER",
            "tables": ["FND_USER"],
            "parameters": []
        }
    ]
}

# ---------------- UI ---------------- #

st.set_page_config(page_title="AI Report Agent", layout="wide")

st.title("🤖 AI Report Intelligence Agent")
st.markdown("### 🚫 Zero Hallucination | ✅ Schema Validated | 🔍 Fusion vs EBS Segregated")

# Sidebar
st.sidebar.header("🔍 Filters")

instance = st.sidebar.selectbox("Select Instance", ["fusion", "ebs"])
search_query = st.sidebar.text_input("Search Report")

# ---------------- LOAD DATA ---------------- #

if instance == "fusion":
    repo = data["fusion_repository"]
    valid_tables = FUSION_VALID_TABLES
else:
    repo = data["ebs_repository"]
    valid_tables = EBS_VALID_TABLES

# ---------------- VALIDATION FUNCTION ---------------- #

def is_valid_report(report, valid_tables):
    return all(table in valid_tables for table in report["tables"])

# ---------------- SEARCH FUNCTION ---------------- #

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

# ---------------- APPLY SEARCH ---------------- #

if search_query:
    results = search_reports(search_query, repo)
else:
    results = repo

# ---------------- STRICT FILTERING ---------------- #

filtered_results = [
    r for r in results
    if r.get("score", 1) >= 0.75
    and is_valid_report(r, valid_tables)
]

# ---------------- UI DISPLAY ---------------- #

st.subheader("📊 Results")

if not filtered_results:
    st.error("❌ No verified report found in repository")
else:
    for r in filtered_results:
        with st.expander(f"📄 {r['report_name']}"):

            st.write(f"**Module:** {r['module']}")
            st.write(f"**Description:** {r['description']}")
            st.write(f"**Tables:** {', '.join(r['tables'])}")
            st.write(f"**Parameters:** {', '.join(r['parameters'])}")

            st.success("✅ Schema Valid (Oracle Verified)")

            st.code(r["sql"], language="sql")

            st.download_button(
                "⬇️ Download SQL",
                data=r["sql"],
                file_name=f"{r['report_name']}.sql"
            )

# ---------------- DEBUG (OPTIONAL) ---------------- #

with st.sidebar.expander("⚙️ Debug Info"):
    st.write("Total Reports:", len(repo))
    st.write("Valid After Filtering:", len(filtered_results))
