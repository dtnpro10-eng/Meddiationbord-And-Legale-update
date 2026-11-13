import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
import requests

st.set_page_config(page_title="Future Life Investments - Legal & Recovery Dashboard", layout="wide")

FILE_PATH = 'ALL Debtor_Report_with_WriteOff_Appended.xlsx'
LOGO_PATH = 'logo.png'
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/10bl8L7LH9kL3bylGO0GHUpmChXAwgK0a0xXmRaq3J7o/export?format=csv"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwiIyODN8PH9y4LEBAU29rvlSInRQDYL5XXIGLrRInJZDf2JqqVgTGNq6Y_pUdooclwCw/exec"

# Metric Cards & Header CSS Styling
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 8px 12px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-transform: uppercase;
        margin-bottom: 0px !important;
    }
    div[data-testid="stMetricValue"] div {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    .header-title {
        font-size: 26px;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0px;
    }
    .header-sub {
        font-size: 14px;
        color: #64748b;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ================= TOP HEADER WITH LOGO =================
header_col1, header_col2 = st.columns([1, 4])

with header_col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        alt_logo = 'Untitled-1-01.png'
        if os.path.exists(alt_logo):
            st.image(alt_logo, use_container_width=True)
        else:
            st.write("🏢 **FLI**")

with header_col2:
    st.markdown('<div class="header-title">ණය අයකරගැනීම් සහ නීතිමය ක්‍රියාමාර්ග අධීක්ෂණ පද්ධතිය</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-sub">Future Life Investments Limited | නීති සහ අයකරගැනීම් අංශය</div>', unsafe_allow_html=True)

st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

# LOAN SETTLE ඇතුළත් කළ Action Tracking Columns
DATE_TRACKING_COLUMNS = [
    'MEDIATION BORD',
    'NON SETELMENT',
    'STETMENT REQ',
    'LEGALLY',
    'PENDING MEDIATION BORD',
    'PENDING legally',
    'LOD REQ',
    'LOAN SETTLE'
]

EXTRA_FIELDS = [
    'Legal Status',
    'Legal Officer Name',
    'Court Case No',
    'Legal Remarks'
]

STATUS_OPTIONS = ["- තෝරන්න (Select) -", "Pending", "In Progress", "Done", "Rejected", "Settled"]

def load_data():
    df = None
    try:
        # Load directly from Google Sheet live
        df = pd.read_csv(GSHEET_CSV_URL)
    except Exception:
        if os.path.exists(FILE_PATH):
            df = pd.read_excel(FILE_PATH)
        else:
            st.error("දත්ත ලබා ගැනීමේ දෝෂයක් මතු විය.")
            st.stop()
            
    df['Loan Account'] = df['Loan Account'].astype(str).str.strip()
    df['NIC'] = df['NIC'].astype(str).str.strip()
    
    for col in DATE_TRACKING_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NaT
        else:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    for col in EXTRA_FIELDS:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].fillna("").astype(str)
            
    return df

def sync_to_cloud_and_local(df_to_save, updates_list=None):
    # 1. Save local Excel copy
    try:
        df_to_save.to_excel(FILE_PATH, index=False)
    except Exception:
        pass
        
    # 2. Sync to Google Sheet via Webhook
    if updates_list and len(updates_list) > 0:
        try:
            requests.post(WEBHOOK_URL, json={'updates': updates_list}, timeout=35)
        except Exception as e:
            st.warning(f"Google Sheet වෙත Sync වීමේ දෝෂයක්: {e}")

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# Sidebar Data Refresh for Multi-user sync
with st.sidebar:
    st.write("### ⚙️ Dashboard Controls")
    if st.button("🔄 නවතම දත්ත පූරණය කරන්න (Refresh Data)", use_container_width=True):
        st.session_state.df = load_data()
        st.success("නවතම දත්ත Google Sheet එකෙන් ලබා ගන්නා ලදී!")
        st.rerun()
    st.caption("🟢 Google Sheet සජීවීව සම්බන්ධ වී ඇත. ලෝකයේ ඕනෑම අයෙකු සිදු කළ වෙනස්කම් ලබා ගැනීමට මෙය ඔබන්න.")

df = st.session_state.df

tab1, tab2, tab3, tab4 = st.tabs([
    "📌 ණය නිලධාරී සාරාංශය (Summary)", 
    "⚡ සමූහ යාවත්කාලීන කිරීම (Bulk Update)",
    "🔍 තනි ගිණුම් සෙවීම සහ සංස්කරණය", 
    "📥 වාර්තා බාගත කිරීම (Download Reports)"
])

# ================= TAB 1: SUMMARY =================
with tab1:
    c_head, c_sel = st.columns([2, 1])
    with c_head:
        st.subheader("ක්‍රියාකාරීත්ව සාරාංශය (Overview Summary)")
    with c_sel:
        officers = ["සියලුම නිලධාරීන් (All Officers)"] + sorted([str(x) for x in df['Loan Officer'].dropna().unique()])
        selected_officer = st.selectbox("Loan Officer තෝරන්න:", officers, label_visibility="collapsed")
    
    if selected_officer != "සියලුම නිලධාරීන් (All Officers)":
        filtered_df = df[df['Loan Officer'] == selected_officer]
    else:
        filtered_df = df

    # Legal Status Section
    st.markdown("**නීතිමය තත්ත්වය (Legal Status):**")
    pending_count = int((filtered_df['Legal Status'] == 'Pending').sum())
    in_prog_count = int((filtered_df['Legal Status'] == 'In Progress').sum())
    done_count = int((filtered_df['Legal Status'] == 'Done').sum())
    settled_status_count = int((filtered_df['Legal Status'] == 'Settled').sum())
    total_assigned = int((filtered_df['Legal Status'].isin(['Pending', 'In Progress', 'Done', 'Rejected', 'Settled'])).sum())

    s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
    s_col1.metric("මුළු ගොනු ගණන", total_assigned)
    s_col2.metric("PENDING", pending_count)
    s_col3.metric("IN PROGRESS", in_prog_count)
    s_col4.metric("DONE", done_count)
    s_col5.metric("SETTLED", settled_status_count)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # Action Dates Section
    st.markdown("**දිනයන් සටහන් කර ඇති ගිණුම් (Action Dates):**")
    d_cols = st.columns(len(DATE_TRACKING_COLUMNS))
    for idx, col_name in enumerate(DATE_TRACKING_COLUMNS):
        cnt = int(filtered_df[col_name].notna().sum())
        d_cols[idx].metric(col_name, cnt)

    st.markdown("---")
    st.write("#### ණය නිලධාරී අනුව සම්පූර්ණ සාරාංශ වගුව")
    summary_data = []
    for officer, group in df.groupby('Loan Officer'):
        row = {
            'Loan Officer': officer,
            'Total Accounts': len(group),
            'Pending': (group['Legal Status'] == 'Pending').sum(),
            'Done': (group['Legal Status'] == 'Done').sum(),
            'Settled': (group['Legal Status'] == 'Settled').sum()
        }
        for c in DATE_TRACKING_COLUMNS:
            row[c] = group[c].notna().sum()
        summary_data.append(row)
        
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

# ================= TAB 2: BULK UPDATE & CORRECTIONS =================
with tab2:
    st.subheader("⚡ සමූහ යාවත්කාලීන කිරීම සහ වැරදි නිවැරදි කිරීම (Bulk Update & Corrections)")

    # 1. UNDO LAST ACTION BANNER (if available)
    if 'last_bulk_backup' in st.session_state and st.session_state['last_bulk_backup'] is not None:
        backup = st.session_state['last_bulk_backup']
        st.markdown(f"""
        <div style="background-color: #fffbeb; border: 1px solid #fde68a; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
            <b style="color: #b45309;">⚠️ මෑතකදී සිදු කළ වෙනස්කම:</b> {backup['action_desc']} (ගිණුම් {len(backup['accounts'])})
        </div>
        """, unsafe_allow_html=True)
        undo_c1, undo_c2 = st.columns([1, 2])
        with undo_c1:
            if st.button("↩️ අවසන් වෙනස්කම ආපසු හරවන්න (Undo Last Action)", type="secondary", use_container_width=True):
                try:
                    fresh_df = load_data()
                    undo_updates = []
                    for acc, prev_data in backup['prev_state'].items():
                        m = (fresh_df['Loan Account'].str.upper() == acc.upper()) | (fresh_df['NIC'].str.upper() == acc.upper())
                        if m.any():
                            idx = fresh_df[m].index[0]
                            fields = {}
                            for c, v in prev_data.items():
                                fresh_df.at[idx, c] = v
                                if pd.isna(v) or v is None:
                                    fields[c] = ""
                                elif isinstance(v, (pd.Timestamp, datetime)):
                                    fields[c] = v.strftime('%Y-%m-%d')
                                else:
                                    fields[c] = str(v)
                            undo_updates.append({'id': str(fresh_df.at[idx, 'Loan Account']), 'fields': fields})
                    sync_to_cloud_and_local(fresh_df, undo_updates)
                    st.session_state.df = fresh_df
                    st.session_state['last_bulk_backup'] = None
                    st.success("✅ අවසන් වරට කළ වෙනස්කම් සාර්ථකව අවලංගු කර Google Sheet එකේද Update කරන ලදී!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Undo කිරීමේදී දෝෂයක් මතු විය: {e}")

    # 2. SELECT BULK MODE
    bulk_mode = st.radio(
        "ක්‍රියාකාරීත්වය තෝරන්න (Select Mode):",
        [
            "➕ Action දිනයක් ඇතුළත් කිරීම (Set / Update Action Date)",
            "🗑️ වැරදීමකින් දැමූ දිනයක් ඉවත් කිරීම (Clear / Delete Action Date)",
            "🔄 Legal Status එක පමණක් යාවත්කාලීන කිරීම (Update Status Only)"
        ],
        horizontal=True
    )

    b_col1, b_col2 = st.columns([1, 2])

    with b_col2:
        raw_input = st.text_area(
            "Loan Account අංක හෝ NIC අංක මෙතැනට Paste කරන්න (එක පේළියට එකක් හෝ Comma දමා):",
            height=220,
            placeholder="උදාහරණයක් ලෙස:\nM3V7000878954\nM1V7000921005\n978441912V\n687053079V"
        )

    # MODE 1: SET DATE
    if bulk_mode == "➕ Action දිනයක් ඇතුළත් කිරීම (Set / Update Action Date)":
        with b_col1:
            selected_action = st.selectbox("යාවත්කාලීන කළ යුතු Action තීරුව:", DATE_TRACKING_COLUMNS, index=0)
            bulk_date = st.date_input(f"{selected_action} සඳහා දිනය:", value=datetime.today().date())
            st.markdown("---")
            set_status = st.checkbox("Legal Status එකත් වෙනස් කරන්නද?", value=False)
            bulk_status = "In Progress"
            if set_status:
                default_stat_idx = 5 if selected_action == 'LOAN SETTLE' else 2
                bulk_status = st.selectbox("Status එක තෝරන්න:", ["Pending", "In Progress", "Done", "Rejected", "Settled"], index=default_stat_idx)

        if st.button(f"🚀 සියලුම ගිණුම් සඳහා [{selected_action}] Update කරන්න", type="primary"):
            if not raw_input.strip():
                st.warning("කරුණාකර අවම වශයෙන් එක් Loan Account හෝ NIC අංකයක්වත් ඇතුළත් කරන්න.")
            else:
                tokens = [x.strip() for x in raw_input.replace(',', '\n').split('\n') if x.strip()]
                tokens_upper = [t.upper() for t in tokens]
                mask = df['Loan Account'].str.upper().isin(tokens_upper) | df['NIC'].str.upper().isin(tokens_upper)
                matched_indices = df[mask].index

                if len(matched_indices) == 0:
                    st.error("ඇතුළත් කළ කිසිදු Loan Account හෝ NIC අංකයක් Excel ගොනුවේ හමු නොවීය.")
                else:
                    try:
                        fresh_df = load_data()
                        fresh_mask = fresh_df['Loan Account'].str.upper().isin(tokens_upper) | fresh_df['NIC'].str.upper().isin(tokens_upper)
                        fresh_indices = fresh_df[fresh_mask].index

                        # Save undo backup
                        backup_records = {}
                        for idx in fresh_indices:
                            acc_no = str(fresh_df.at[idx, 'Loan Account'])
                            backup_records[acc_no] = {
                                selected_action: fresh_df.at[idx, selected_action],
                                'Legal Status': fresh_df.at[idx, 'Legal Status']
                            }
                        st.session_state['last_bulk_backup'] = {
                            'action_desc': f"[{selected_action}] දිනය [{bulk_date}] ලෙස Update කිරීම",
                            'accounts': list(backup_records.keys()),
                            'prev_state': backup_records
                        }

                        fresh_df.loc[fresh_indices, selected_action] = pd.to_datetime(bulk_date)
                        if set_status:
                            fresh_df.loc[fresh_indices, 'Legal Status'] = bulk_status

                        bulk_updates = []
                        for idx in fresh_indices:
                            acc_no = str(fresh_df.at[idx, 'Loan Account'])
                            f_dict = { selected_action: str(bulk_date) }
                            if set_status:
                                f_dict['Legal Status'] = bulk_status
                            bulk_updates.append({'id': acc_no, 'fields': f_dict})

                        sync_to_cloud_and_local(fresh_df, bulk_updates)
                        st.session_state.df = fresh_df
                        st.success(f"✅ ගිණුම් {len(fresh_indices)} ක [{selected_action}] දිනය [{bulk_date}] ලෙස සාර්ථකව Google Sheet එකට Save විය!")

                        st.write("##### යාවත්කාලීන වූ ගිණුම් ලැයිස්තුව:")
                        disp_cols = ['Branch', 'Loan Officer', 'Client Name', 'NIC', 'Loan Account', selected_action, 'Legal Status']
                        st.dataframe(fresh_df.loc[fresh_indices, disp_cols], use_container_width=True)
                    except Exception as e:
                        st.error(f"Save කිරීමේදී දෝෂයක් මතු විය: {e}")

    # MODE 2: CLEAR ACTION DATE
    elif bulk_mode == "🗑️ වැරදීමකින් දැමූ දිනයක් ඉවත් කිරීම (Clear / Delete Action Date)":
        with b_col1:
            clear_action = st.selectbox("ඉවත් කළ යුතු Action තීරුව තෝරන්න:", ["සියලු Actions (All Actions)"] + DATE_TRACKING_COLUMNS, index=0)
            st.markdown("---")
            reset_status_chk = st.checkbox("Legal Status එකත් වෙනස් / හිස් කරන්නද?", value=False)
            reset_status_val = "- තෝරන්න (Select) -"
            if reset_status_chk:
                reset_status_val = st.selectbox("Status එක මාරු කළ යුතු අගය:", STATUS_OPTIONS, index=0)

        if st.button(f"🗑️ තෝරාගත් ගිණුම් වලින් [{clear_action}] දිනය ඉවත් කරන්න (Clear Date)", type="primary"):
            if not raw_input.strip():
                st.warning("කරුණාකර අවම වශයෙන් එක් Loan Account හෝ NIC අංකයක්වත් ඇතුළත් කරන්න.")
            else:
                tokens = [x.strip() for x in raw_input.replace(',', '\n').split('\n') if x.strip()]
                tokens_upper = [t.upper() for t in tokens]
                mask = df['Loan Account'].str.upper().isin(tokens_upper) | df['NIC'].str.upper().isin(tokens_upper)
                matched_indices = df[mask].index

                if len(matched_indices) == 0:
                    st.error("ඇතුළත් කළ කිසිදු Loan Account හෝ NIC අංකයක් Excel ගොනුවේ හමු නොවීය.")
                else:
                    try:
                        fresh_df = load_data()
                        fresh_mask = fresh_df['Loan Account'].str.upper().isin(tokens_upper) | fresh_df['NIC'].str.upper().isin(tokens_upper)
                        fresh_indices = fresh_df[fresh_mask].index

                        cols_to_clear = DATE_TRACKING_COLUMNS if clear_action == "සියලු Actions (All Actions)" else [clear_action]

                        # Save undo backup
                        backup_records = {}
                        for idx in fresh_indices:
                            acc_no = str(fresh_df.at[idx, 'Loan Account'])
                            rec = {'Legal Status': fresh_df.at[idx, 'Legal Status']}
                            for c in cols_to_clear:
                                rec[c] = fresh_df.at[idx, c]
                            backup_records[acc_no] = rec

                        st.session_state['last_bulk_backup'] = {
                            'action_desc': f"[{clear_action}] දිනයන් ඉවත් කිරීම (Clear)",
                            'accounts': list(backup_records.keys()),
                            'prev_state': backup_records
                        }

                        for c in cols_to_clear:
                            fresh_df.loc[fresh_indices, c] = pd.NaT

                        if reset_status_chk:
                            fresh_df.loc[fresh_indices, 'Legal Status'] = reset_status_val if reset_status_val != "- තෝරන්න (Select) -" else ""

                        clear_updates = []
                        for idx in fresh_indices:
                            acc_no = str(fresh_df.at[idx, 'Loan Account'])
                            f_dict = { c: "" for c in cols_to_clear }
                            if reset_status_chk:
                                f_dict['Legal Status'] = reset_status_val if reset_status_val != "- තෝරන්න (Select) -" else ""
                            clear_updates.append({'id': acc_no, 'fields': f_dict})

                        sync_to_cloud_and_local(fresh_df, clear_updates)
                        st.session_state.df = fresh_df
                        st.success(f"✅ ගිණුම් {len(fresh_indices)} ක [{clear_action}] දිනය සාර්ථකව ඉවත් කර Google Sheet එකට Save කරන ලදී!")

                        st.write("##### ඉවත් කළ පසු ගිණුම් වල තත්ත්වය:")
                        disp_cols = ['Branch', 'Loan Officer', 'Client Name', 'NIC', 'Loan Account', 'Legal Status'] + [c for c in cols_to_clear if c in fresh_df.columns]
                        st.dataframe(fresh_df.loc[fresh_indices, disp_cols], use_container_width=True)
                    except Exception as e:
                        st.error(f"Save කිරීමේදී දෝෂයක් මතු විය: {e}")

    # MODE 3: STATUS ONLY
    else:
        with b_col1:
            only_status = st.selectbox("මාරු කළ යුතු Legal Status අගය:", STATUS_OPTIONS, index=1)
            st.caption("Action දිනයන් වෙනස් නොවේ. Legal Status පමණක් මාරු වේ.")

        if st.button(f"🔄 තෝරාගත් ගිණුම් වල Status එක [{only_status}] ලෙස මාරු කරන්න", type="primary"):
            if not raw_input.strip():
                st.warning("කරුණාකර අවම වශයෙන් එක් Loan Account හෝ NIC අංකයක්වත් ඇතුළත් කරන්න.")
            else:
                tokens = [x.strip() for x in raw_input.replace(',', '\n').split('\n') if x.strip()]
                tokens_upper = [t.upper() for t in tokens]
                mask = df['Loan Account'].str.upper().isin(tokens_upper) | df['NIC'].str.upper().isin(tokens_upper)
                matched_indices = df[mask].index

                if len(matched_indices) == 0:
                    st.error("ඇතුළත් කළ කිසිදු Loan Account හෝ NIC අංකයක් Excel ගොනුවේ හමු නොවීය.")
                else:
                    try:
                        fresh_df = load_data()
                        fresh_mask = fresh_df['Loan Account'].str.upper().isin(tokens_upper) | fresh_df['NIC'].str.upper().isin(tokens_upper)
                        fresh_indices = fresh_df[fresh_mask].index

                        backup_records = {}
                        for idx in fresh_indices:
                            acc_no = str(fresh_df.at[idx, 'Loan Account'])
                            backup_records[acc_no] = {'Legal Status': fresh_df.at[idx, 'Legal Status']}

                        st.session_state['last_bulk_backup'] = {
                            'action_desc': f"Legal Status [{only_status}] ලෙස මාරු කිරීම",
                            'accounts': list(backup_records.keys()),
                            'prev_state': backup_records
                        }

                        val = only_status if only_status != "- තෝරන්න (Select) -" else ""
                        fresh_df.loc[fresh_indices, 'Legal Status'] = val

                        status_updates = []
                        for idx in fresh_indices:
                            acc_no = str(fresh_df.at[idx, 'Loan Account'])
                            status_updates.append({'id': acc_no, 'fields': {'Legal Status': val}})

                        sync_to_cloud_and_local(fresh_df, status_updates)
                        st.session_state.df = fresh_df
                        st.success(f"✅ ගිණුම් {len(fresh_indices)} ක Legal Status සාර්ථකව [{only_status}] ලෙස Google Sheet එකට Save කරන ලදී!")
                        disp_cols = ['Branch', 'Loan Officer', 'Client Name', 'NIC', 'Loan Account', 'Legal Status']
                        st.dataframe(fresh_df.loc[fresh_indices, disp_cols], use_container_width=True)
                    except Exception as e:
                        st.error(f"Save කිරීමේදී දෝෂයක් මතු විය: {e}")

# ================= TAB 3: SEARCH & UPDATE =================
with tab3:
    st.subheader("තනි ගිණුමක් සෙවීම සහ තොරතුරු යාවත්කාලීන කිරීම")
    search_query = st.text_input("NIC අංකය හෝ Loan Account අංකය ඇතුළත් කර Enter ඔබන්න:").strip()
    
    if search_query:
        match = df[(df['NIC'].str.upper() == search_query.upper()) | 
                   (df['Loan Account'].str.upper() == search_query.upper())]
        
        if match.empty:
            st.warning("මෙම NIC හෝ Loan Account අංකයට අදාළ දත්ත හමු නොවීය.")
        else:
            row_idx = match.index[0]
            record = match.iloc[0]
            
            st.success(f"නම: **{record['Client Name']}** | Loan Account: **{record['Loan Account']}** | NIC: **{record['NIC']}**")
            
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Branch:** {record['Branch']}")
            c1.write(f"**Loan Officer:** {record['Loan Officer']}")
            c2.write(f"**Center:** {record['Center']}")
            c2.write(f"**Total Arrears:** {record.get('Total Arrears', 'N/A')}")
            c3.write(f"**Total Outstanding:** {record.get('Total Outstanding', 'N/A')}")
            c3.write(f"**Mobile:** {record.get('Mobile No', 'N/A')}")
            
            st.markdown("---")
            with st.form("update_single_form"):
                st.write("### 1. Legal / Case විස්තර:")
                f_c1, f_c2, f_c3 = st.columns(3)
                
                curr_status = record.get('Legal Status', '')
                status_idx = STATUS_OPTIONS.index(curr_status) if curr_status in STATUS_OPTIONS else 0
                new_status = f_c1.selectbox("Legal Status", STATUS_OPTIONS, index=status_idx)
                
                new_officer = f_c2.text_input("Legal Officer ගේ නම", value=str(record.get('Legal Officer Name', '')))
                new_case_no = f_c3.text_input("උසාවි නඩු අංකය (Court Case No)", value=str(record.get('Court Case No', '')))
                
                new_remarks = st.text_area("සටහන් (Notes / Remarks)", value=str(record.get('Legal Remarks', '')))
                
                st.write("### 2. අදාළ දිනයන් (Action Dates):")
                st.caption("💡 දිනයක් ඉවත් කිරීමට අවශ්‍ය නම් අදාළ Checkbox එක Uncheck (ටික් එක අයින්) කර Save කරන්න.")
                date_input_cols = st.columns(2)
                updated_dates = {}
                
                for idx, col in enumerate(DATE_TRACKING_COLUMNS):
                    curr_val = record[col]
                    default_date = curr_val.date() if pd.notna(curr_val) else None
                    
                    with date_input_cols[idx % 2]:
                        enable = st.checkbox(f"{col} දිනය ඇතුළත් කරන්න", value=(default_date is not None), key=f"chk_single_{col}")
                        if enable:
                            updated_dates[col] = st.date_input(
                                f"{col} දිනය", 
                                value=default_date if default_date else datetime.today().date(),
                                key=f"date_single_{col}"
                            )
                        else:
                            updated_dates[col] = None
                            
                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    save_btn = st.form_submit_button("💾 වෙනස්කම් Google Sheet එකට Save කරන්න", type="primary", use_container_width=True)
                with btn_c2:
                    clear_all_dates_btn = st.form_submit_button("🗑️ Action Dates සියල්ල ඉවත් කරන්න (Clear All Dates)", use_container_width=True)
                
                if save_btn:
                    try:
                        fresh_df = load_data()
                        target_mask = (fresh_df['Loan Account'].str.upper() == str(record['Loan Account']).upper()) | (fresh_df['NIC'].str.upper() == str(record['NIC']).upper())
                        if target_mask.any():
                            target_idx = fresh_df[target_mask].index[0]
                            fresh_df.at[target_idx, 'Legal Status'] = new_status if new_status != "- තෝරන්න (Select) -" else ""
                            fresh_df.at[target_idx, 'Legal Officer Name'] = new_officer
                            fresh_df.at[target_idx, 'Court Case No'] = new_case_no
                            fresh_df.at[target_idx, 'Legal Remarks'] = new_remarks
                            
                            for col, val in updated_dates.items():
                                fresh_df.at[target_idx, col] = pd.to_datetime(val) if val else pd.NaT

                            single_fields = {
                                'Legal Status': new_status if new_status != "- තෝරන්න (Select) -" else "",
                                'Legal Officer Name': new_officer,
                                'Court Case No': new_case_no,
                                'Legal Remarks': new_remarks
                            }
                            for col, val in updated_dates.items():
                                single_fields[col] = str(val) if val else ""

                            single_updates = [{'id': str(fresh_df.at[target_idx, 'Loan Account']), 'fields': single_fields}]
                            sync_to_cloud_and_local(fresh_df, single_updates)
                            st.session_state.df = fresh_df
                            st.success("✅ සාර්ථකව Google Sheet එකෙහි Save විය!")
                            st.rerun()
                        else:
                            st.error("දත්ත යාවත්කාලීන කිරීමට අදාළ ගිණුම හමු නොවීය.")
                    except Exception as e:
                        st.error(f"Save කිරීමේදී දෝෂයක් මතු විය: {e}")

                if clear_all_dates_btn:
                    try:
                        fresh_df = load_data()
                        target_mask = (fresh_df['Loan Account'].str.upper() == str(record['Loan Account']).upper()) | (fresh_df['NIC'].str.upper() == str(record['NIC']).upper())
                        if target_mask.any():
                            target_idx = fresh_df[target_mask].index[0]
                            for col in DATE_TRACKING_COLUMNS:
                                fresh_df.at[target_idx, col] = pd.NaT

                            clear_fields = { col: "" for col in DATE_TRACKING_COLUMNS }
                            clear_updates = [{'id': str(fresh_df.at[target_idx, 'Loan Account']), 'fields': clear_fields}]
                            sync_to_cloud_and_local(fresh_df, clear_updates)
                            st.session_state.df = fresh_df
                            st.success("✅ මෙම ගිණුමේ සියලු Action Dates සාර්ථකව ඉවත් කර Google Sheet එකෙහි Save කරන ලදී!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Save කිරීමේදී දෝෂයක් මතු විය: {e}")

# ================= TAB 4: DOWNLOAD REPORTS =================
with tab4:
    st.subheader("📥 වාර්තා Filter කිරීම සහ Excel ලෙස Download කිරීම")
    
    f1, f2, f3 = st.columns(3)
    rep_officer = f1.selectbox("Loan Officer අනුව Filter කරන්න:", ["All"] + sorted([str(x) for x in df['Loan Officer'].dropna().unique()]), key="rep_off")
    rep_status = f2.selectbox("Status එක අනුව Filter කරන්න:", ["All", "Pending", "In Progress", "Done", "Rejected", "Settled"], key="rep_stat")
    rep_action = f3.selectbox("Action Date Column එක අනුව Filter කරන්න:", ["All"] + DATE_TRACKING_COLUMNS, key="rep_act")
    
    rep_df = df.copy()
    if rep_officer != "All":
        rep_df = rep_df[rep_df['Loan Officer'] == rep_officer]
    if rep_status != "All":
        rep_df = rep_df[rep_df['Legal Status'] == rep_status]
    if rep_action != "All":
        rep_df = rep_df[rep_df[rep_action].notna()]
        
    st.write(f"**හමු වූ මුළු වාර්තා ගණන: {len(rep_df)}**")
    
    preview_cols = ['Branch', 'Loan Officer', 'Center', 'Client Name', 'NIC', 'Loan Account', 'Total Arrears', 'Legal Status', 'Legal Officer Name', 'Court Case No', 'Legal Remarks'] + DATE_TRACKING_COLUMNS
    preview_cols = [c for c in preview_cols if c in rep_df.columns]
    
    st.dataframe(rep_df[preview_cols], use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        rep_df.to_excel(writer, index=False, sheet_name='Filtered_Report')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 මෙම වාර්තාව Excel ගොනුවක් ලෙස Download කරගන්න (.xlsx)",
        data=excel_data,
        file_name=f"Legal_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )