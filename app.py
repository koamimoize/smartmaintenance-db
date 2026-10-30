import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, get_connection, seed_demo_data

st.set_page_config(page_title="SmartMaintenance DB", page_icon="🏭", layout="wide")
init_db()
seed_demo_data()

st.title("🏭 SmartMaintenance DB")
st.caption("Industrial maintenance monitoring prototype • Demo data only")

conn = get_connection()

menu = st.sidebar.radio("Navigation", ["Dashboard", "Machines", "Failures", "Interventions"])
st.sidebar.divider()
st.sidebar.caption("Prototype pédagogique — aucune connexion machine réelle.")

if menu == "Dashboard":
    machines = pd.read_sql_query("SELECT * FROM machines", conn)
    failures = pd.read_sql_query("""
        SELECT f.*, m.machine_name
        FROM failures f JOIN machines m ON m.machine_id=f.machine_id
        ORDER BY failure_date DESC
    """, conn)
    total_failures = len(failures)
    total_downtime = float(failures["downtime_hours"].sum()) if total_failures else 0
    avg_downtime = total_downtime / total_failures if total_failures else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Machines", len(machines))
    c2.metric("Pannes", total_failures)
    c3.metric("Temps d'arrêt", f"{total_downtime:.1f} h")
    c4.metric("Arrêt moyen / panne", f"{avg_downtime:.2f} h")

    st.subheader("Temps d'arrêt par machine")
    if not failures.empty:
        chart_data = failures.groupby("machine_name", as_index=False)["downtime_hours"].sum()
        fig = px.bar(chart_data, x="machine_name", y="downtime_hours",
                     labels={"machine_name": "Machine", "downtime_hours": "Temps d'arrêt (h)"},
                     title="Downtime by machine")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune panne enregistrée.")

    st.subheader("Dernières pannes")
    st.dataframe(failures, use_container_width=True, hide_index=True)

elif menu == "Machines":
    st.subheader("Registre des machines")
    machines = pd.read_sql_query("SELECT * FROM machines ORDER BY machine_id", conn)
    st.dataframe(machines, use_container_width=True, hide_index=True)

    with st.expander("Ajouter une machine"):
        with st.form("add_machine"):
            name = st.text_input("Code machine", placeholder="CNC-002")
            kind = st.text_input("Type", placeholder="CNC Machine")
            location = st.text_input("Emplacement", placeholder="Workshop A")
            install_date = st.date_input("Date d'installation")
            status = st.selectbox("État", ["Operational", "Maintenance", "Out of service"])
            submitted = st.form_submit_button("Enregistrer")
            if submitted:
                if not name.strip() or not kind.strip():
                    st.error("Le code et le type sont obligatoires.")
                else:
                    try:
                        conn.execute("""INSERT INTO machines
                            (machine_name, machine_type, location, installation_date, status)
                            VALUES (?, ?, ?, ?, ?)""",
                            (name.strip(), kind.strip(), location, str(install_date), status))
                        conn.commit()
                        st.success("Machine enregistrée.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Impossible d'enregistrer : {e}")

elif menu == "Failures":
    st.subheader("Historique des pannes")
    failures = pd.read_sql_query("""
        SELECT f.failure_id, m.machine_name, f.failure_date, f.failure_type,
               f.description, f.downtime_hours, f.severity
        FROM failures f JOIN machines m ON m.machine_id=f.machine_id
        ORDER BY f.failure_date DESC
    """, conn)
    st.dataframe(failures, use_container_width=True, hide_index=True)

    with st.expander("Déclarer une panne"):
        machines = pd.read_sql_query("SELECT machine_id, machine_name FROM machines", conn)
        with st.form("add_failure"):
            selected = st.selectbox("Machine", machines["machine_name"].tolist())
            date = st.date_input("Date de panne")
            kind = st.selectbox("Type", ["Mechanical", "Electrical", "Hydraulic", "Pneumatic", "Other"])
            description = st.text_input("Description")
            downtime = st.number_input("Temps d'arrêt (heures)", min_value=0.0, step=0.5)
            severity = st.selectbox("Gravité", ["Low", "Medium", "High", "Critical"])
            submitted = st.form_submit_button("Enregistrer la panne")
            if submitted:
                machine_id = int(machines.loc[machines.machine_name == selected, "machine_id"].iloc[0])
                conn.execute("""INSERT INTO failures
                    (machine_id, failure_date, failure_type, description, downtime_hours, severity)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (machine_id, str(date), kind, description, downtime, severity))
                conn.commit()
                st.success("Panne enregistrée.")
                st.rerun()

elif menu == "Interventions":
    st.subheader("Interventions de maintenance")
    interventions = pd.read_sql_query("""
        SELECT i.intervention_id, m.machine_name, f.failure_date,
               i.intervention_type, i.repair_duration_hours,
               i.technician, i.labor_cost_eur, i.status
        FROM interventions i
        JOIN failures f ON f.failure_id=i.failure_id
        JOIN machines m ON m.machine_id=f.machine_id
        ORDER BY i.intervention_id DESC
    """, conn)
    st.dataframe(interventions, use_container_width=True, hide_index=True)

    failures = pd.read_sql_query("""
        SELECT f.failure_id, m.machine_name, f.failure_date, f.description
        FROM failures f JOIN machines m ON m.machine_id=f.machine_id
        ORDER BY f.failure_id
    """, conn)
    with st.expander("Ajouter une intervention"):
        if failures.empty:
            st.info("Ajoutez d'abord une panne.")
        else:
            labels = {
                f"{r.machine_name} • {r.failure_date} • {r.description} (ID {r.failure_id})": int(r.failure_id)
                for r in failures.itertuples()
            }
            with st.form("add_intervention"):
                selected = st.selectbox("Panne concernée", list(labels.keys()))
                kind = st.selectbox("Type d'intervention", ["Corrective", "Preventive", "Inspection"])
                duration = st.number_input("Durée réelle de réparation (h)", min_value=0.0, step=0.25)
                technician = st.text_input("Technicien")
                cost = st.number_input("Coût de main-d'œuvre (€)", min_value=0.0, step=5.0)
                status = st.selectbox("Statut", ["Completed", "In progress", "Planned"])
                submitted = st.form_submit_button("Enregistrer l'intervention")
                if submitted:
                    conn.execute("""INSERT INTO interventions
                        (failure_id, intervention_type, repair_duration_hours,
                         technician, labor_cost_eur, status)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (labels[selected], kind, duration, technician, cost, status))
                    conn.commit()
                    st.success("Intervention enregistrée.")
                    st.rerun()

conn.close()
