# hermes_app.py
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt

# ----------------------
# DATACLASSES
# ----------------------
@dataclass
class ProjectMasterData:
    project_name: str = ""
    client: str = ""
    project_manager: str = ""
    user_representative: str = ""
    start_date: str = ""
    budget: float = 0.0
    approach: str = "classical"  # 'classical' or 'agile'
    project_size: str = "medium"  # small/medium/large
    language: str = "en"  # 'en' or 'de'

@dataclass
class PhaseResult:
    name: str
    description: str = ""
    status: str = "not_started"  # not_started/in_progress/completed/approved
    approval_required: bool = False
    approval_date: str = ""
    responsible_role: str = ""

@dataclass
class ProjectPhase:
    name: str
    results: Dict[str, PhaseResult] = field(default_factory=dict)
    required_documents: List[str] = field(default_factory=list)
    checklist_results: Dict[str, bool] = field(default_factory=dict)
    status: str = "not_started"
    start_date: str = ""
    end_date: str = ""

@dataclass
class HermesDocument:
    name: str
    responsible: str = ""
    status: str = "not_started"  # not_started/in_progress/completed
    required: bool = True
    linked_result: str = ""
    content: str = ""

@dataclass
class HermesMilestone:
    name: str
    phase: str
    date: str = ""
    status: str = "planned"  # planned/reached/delayed
    mandatory: bool = True

@dataclass
class Iteration:
    number: int
    name: str
    start_date: str
    end_date: str
    total_user_stories: int = 0
    completed_user_stories: int = 0
    release_candidate: bool = False
    release_approved: bool = False
    status: str = "planned"
    goals: List[str] = field(default_factory=list)

    def progress(self) -> float:
        return (self.completed_user_stories / self.total_user_stories * 100) if self.total_user_stories > 0 else 0.0

@dataclass
class BudgetTransaction:
    date: str = ""
    category: str = ""
    amount: float = 0.0
    description: str = ""
    type: str = "actual"  # actual or planned

@dataclass
class HermesProject:
    master_data: ProjectMasterData = field(default_factory=ProjectMasterData)
    phases: Dict[str, ProjectPhase] = field(default_factory=dict)
    documents: Dict[str, HermesDocument] = field(default_factory=dict)
    milestones: List[HermesMilestone] = field(default_factory=list)
    iterations: List[Iteration] = field(default_factory=list)
    budget_entries: List[BudgetTransaction] = field(default_factory=list)
    actual_costs: float = 0.0
    tailoring: Dict = field(default_factory=dict)
    current_phase: str = "initialization"
    risks: List[Dict] = field(default_factory=list)

# ----------------------
# CONSTANTS: Roles, Checklists, Project size tailoring
# ----------------------
HERMES_ROLES = [
    "Steering Committee", "Project Manager", "User Representative",
    "Quality Assurance", "Operations", "Project Controller"
]

# Checklists: full & simplified (extendable)
HERMES_CHECKLISTS = {
    "initialization": {
        "full": [
            "Project Charter approved by Steering Committee",
            "Stakeholders identified and analysed",
            "Initial risk assessment completed",
            "Project organization defined",
            "Budget estimation completed"
        ],
        "simplified": [
            "Project Charter created",
            "Stakeholders listed",
            "Budget rough estimation"
        ]
    },
    "concept": {
        "full": [
            "Requirements documented and validated",
            "Solution architecture defined",
            "Feasibility study completed",
            "Risks updated and accepted",
            "Cost-benefit analysis done"
        ],
        "simplified": [
            "Requirements documented",
            "Solution draft created"
        ]
    },
    "implementation": {
        "full": [
            "Development completed according to specification",
            "Integration tests executed",
            "Acceptance tests executed",
            "Operational documentation prepared"
        ],
        "simplified": [
            "Core features implemented",
            "Basic tests passed"
        ]
    },
    "introduction": {
        "full": [
            "Acceptance by client completed",
            "Operational handover completed",
            "Training of operations staff completed",
            "Support organization defined"
        ],
        "simplified": [
            "Acceptance completed",
            "Handover done"
        ]
    },
    "completion": {
        "full": [
            "Lessons learned documented",
            "Final acceptance signed",
            "Project finances closed",
            "All deliverables archived"
        ],
        "simplified": [
            "Final acceptance",
            "Lessons learned short report"
        ]
    }
}

PROJECT_SIZE_CONFIGS = {
    "small": {
        "simplified_checklists": True,
        "required_documents": ["Project Charter", "Acceptance Protocol"],
        "optional_documents": ["Study", "Operating Handbook"],
        "mandatory_milestones": ["Project Start", "Project Completed"]
    },
    "medium": {
        "simplified_checklists": False,
        "required_documents": ["Project Charter", "Project Management Plan", "Solution Requirements"],
        "optional_documents": ["Migration Concept"],
        "mandatory_milestones": ["Project Start", "Implementation Decision", "Project Completed"]
    },
    "large": {
        "simplified_checklists": False,
        "required_documents": ["Project Charter", "Study", "Project Management Plan", "Solution Architecture", "Test Concept"],
        "optional_documents": [],
        "mandatory_milestones": ["Project Start", "Implementation Decision", "Phase Release Concept", "Phase Release Realization", "Project Completed"]
    }
}

# ----------------------
# SERIALIZATION HELPERS
# ----------------------
def dataclass_to_dict(obj):
    """Recursively convert dataclass instances to dictionaries (for JSON export)"""
    if isinstance(obj, list):
        return [dataclass_to_dict(i) for i in obj]
    elif hasattr(obj, "__dataclass_fields__"):
        result = {}
        for k, v in asdict(obj).items():
            result[k] = dataclass_to_dict(v)
        result["_type"] = obj.__class__.__name__
        return result
    elif isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    else:
        return obj

def dict_to_dataclass(d):
    """Convert the top-level structure (expects HermesProject-like dict)."""
    # This is a practical approach assuming exported structure from dataclass_to_dict
    # We'll manually reconstruct HermesProject
    try:
        md = d.get("master_data", {})
        master = ProjectMasterData(**md)
        project = HermesProject(master_data=master)
        # phases
        for pname, pdata in d.get("phases", {}).items():
            phase = ProjectPhase(name=pdata.get("name", pname),
                                 status=pdata.get("status", "not_started"),
                                 start_date=pdata.get("start_date", ""),
                                 end_date=pdata.get("end_date", ""))
            # results
            for rname, rdata in pdata.get("results", {}).items():
                rr = PhaseResult(
                    name=rdata.get("name", rname),
                    description=rdata.get("description", ""),
                    status=rdata.get("status", "not_started"),
                    approval_required=rdata.get("approval_required", False),
                    approval_date=rdata.get("approval_date", ""),
                    responsible_role=rdata.get("responsible_role", "")
                )
                phase.results[rname] = rr
            # checklist
            phase.checklist_results = pdata.get("checklist_results", {})
            project.phases[pname] = phase
        # documents
        for dname, ddata in d.get("documents", {}).items():
            doc = HermesDocument(
                name=ddata.get("name", dname),
                responsible=ddata.get("responsible", ""),
                status=ddata.get("status", "not_started"),
                required=ddata.get("required", True),
                linked_result=ddata.get("linked_result", ""),
                content=ddata.get("content", "")
            )
            project.documents[dname] = doc
        # milestones
        for ms in d.get("milestones", []):
            m = HermesMilestone(
                name=ms.get("name", ""),
                phase=ms.get("phase", ""),
                date=ms.get("date", ""),
                status=ms.get("status", "planned"),
                mandatory=ms.get("mandatory", True)
            )
            project.milestones.append(m)
        # iterations
        for it in d.get("iterations", []):
            iteration = Iteration(
                number=it.get("number", 1),
                name=it.get("name", f"Sprint {it.get('number',1)}"),
                start_date=it.get("start_date", ""),
                end_date=it.get("end_date", ""),
                total_user_stories=it.get("total_user_stories", 0),
                completed_user_stories=it.get("completed_user_stories", 0),
                release_candidate=it.get("release_candidate", False),
                release_approved=it.get("release_approved", False),
                status=it.get("status", "planned"),
                goals=it.get("goals", [])
            )
            project.iterations.append(iteration)
        # budget
        for t in d.get("budget_entries", []):
            tr = BudgetTransaction(
                date=t.get("date", ""),
                category=t.get("category", ""),
                amount=t.get("amount", 0.0),
                description=t.get("description", ""),
                type=t.get("type", "actual")
            )
            project.budget_entries.append(tr)
        project.actual_costs = d.get("actual_costs", 0.0)
        project.current_phase = d.get("current_phase", "initialization")
        project.tailoring = d.get("tailoring", {})
        return project
    except Exception as e:
        st.error(f"Error parsing project JSON: {e}")
        return HermesProject()

# ----------------------
# INIT / DEFAULTS
# ----------------------
def init_session_state():
    if 'hermes_project' not in st.session_state:
        st.session_state.hermes_project = HermesProject()
        # initialize default classical phases
        default_phases = {
            "initialization": ProjectPhase("Initialization"),
            "concept": ProjectPhase("Concept"),
            "implementation": ProjectPhase("Implementation"),
            "introduction": ProjectPhase("Introduction"),
            "completion": ProjectPhase("Completion")
        }
        st.session_state.hermes_project.phases = default_phases
        # default required docs (can be tailored)
        default_docs = ["Project Charter", "Project Management Plan", "Solution Requirements", "Acceptance Protocol"]
        for dn in default_docs:
            st.session_state.hermes_project.documents[dn] = HermesDocument(name=dn, responsible="Project Manager", required=True)
        # default milestones
        st.session_state.hermes_project.milestones = [
            HermesMilestone("Project Start", "initialization", mandatory=True),
            HermesMilestone("Implementation Decision", "concept", mandatory=True),
            HermesMilestone("Project Completed", "completion", mandatory=True)
        ]

# ----------------------
# CALCULATIONS & UTILITIES
# ----------------------
def calculate_budget_usage(project: HermesProject) -> float:
    actual_costs = sum(t.amount for t in project.budget_entries if t.type == "actual")
    if project.master_data.budget and project.master_data.budget > 0:
        return actual_costs / project.master_data.budget
    return 0.0

def calculate_phase_progress(phase: ProjectPhase) -> float:
    total = len(phase.results)
    if total == 0:
        return 0.0
    completed = sum(1 for r in phase.results.values() if r.status in ["completed", "approved"])
    return completed / total * 100.0

def calculate_total_progress(project: HermesProject) -> float:
    phases = project.phases.values()
    if not phases:
        return 0.0
    return sum(calculate_phase_progress(p) for p in phases) / len(list(phases))

def calculate_risk_level(project: HermesProject) -> str:
    # simple heuristic
    progress = calculate_total_progress(project)
    usage = calculate_budget_usage(project)
    if progress > 80 and usage < 0.8:
        return "low"
    if progress > 50 or usage < 0.9:
        return "medium"
    return "high"

def calculate_quality_score(project: HermesProject) -> int:
    total_items = 0
    good_items = 0
    for p in project.phases.values():
        for checklist_val in p.checklist_results.values():
            total_items += 1
            if checklist_val:
                good_items += 1
        for r in p.results.values():
            total_items += 1
            if r.status == "approved":
                good_items += 1
    return int((good_items / total_items * 100) if total_items > 0 else 0)

# ----------------------
# INSTRUCTIONS HELPER (multilingual)
# ----------------------
INSTRUCTIONS = {
    "en": {
        "dashboard": "Overview of budget, phases, milestones and health indicators. Tip: update costs frequently.",
        "initialization": "Enter master data, choose approach (classical/agile) and project size. Tailoring will be applied automatically.",
        "results": "Create and manage results for each phase. Mark results complete and request approvals where required.",
        "budget": "Add budget transactions (planned/actual) and monitor usage. Export for stakeholders.",
        "milestones": "Visualize milestones, run governance checks and reach milestones only when prerequisites met.",
        "iterations": "Create iterations (sprints), track progress and approve releases when criteria fulfilled.",
        "documents": "Manage documents, link them to results. Completed documents automatically update result status.",
        "info": "HERMES methodology adapted for configurable classical/agile projects."
    },
    "de": {
        "dashboard": "Übersicht zu Budget, Phasen, Meilensteinen und Gesundheitsindikatoren. Tipp: Kosten regelmässig aktualisieren.",
        "initialization": "Geben Sie Stammdaten ein, wählen Sie Vorgehen (klassisch/agil) und Projektgröße. Tailoring wird automatisch angewendet.",
        "results": "Erstellen und verwalten Sie Ergebnisse für jede Phase. Markieren Sie Ergebnisse als abgeschlossen und fordern Sie Genehmigungen an.",
        "budget": "Fügen Sie Budgettransaktionen (geplant/tatsächlich) hinzu und überwachen Sie die Nutzung. Export für Stakeholder möglich.",
        "milestones": "Visualisieren Sie Meilensteine, führen Sie Governance-Checks durch und erreichen Sie Meilensteine nur bei Erfüllung der Voraussetzungen.",
        "iterations": "Erstellen Sie Iterationen (Sprints), verfolgen Sie den Fortschritt und genehmigen Releases, wenn Kriterien erfüllt sind.",
        "documents": "Verwalten Sie Dokumente und verknüpfen Sie diese mit Ergebnissen. Abgeschlossene Dokumente aktualisieren Ergebnisstatus automatisch.",
        "info": "HERMES-Methodik, angepasst für konfigurierbare klassische/agile Projekte."
    }
}

def t(key: str, project: HermesProject) -> str:
    lang = project.master_data.language if project and project.master_data else "en"
    return INSTRUCTIONS.get(lang, INSTRUCTIONS["en"]).get(key, "")

def show_instructions(title: str, text: str):
    with st.expander(f"ℹ️ {title} - Instructions", expanded=False):
        st.markdown(text)

# ----------------------
# PROJECT INITIALIZATION
# ----------------------
def project_initialization():
    st.header("🚀 Project Initialization")
    project = st.session_state.hermes_project
    show_instructions("Project Initialization", t("initialization", project))
    with st.form("init_form"):
        col1, col2 = st.columns(2)
        with col1:
            project.master_data.project_name = st.text_input("Project Name", project.master_data.project_name)
            project.master_data.client = st.text_input("Client", project.master_data.client)
            project.master_data.project_manager = st.text_input("Project Manager", project.master_data.project_manager)
            project.master_data.user_representative = st.text_input("User Representative", project.master_data.user_representative)
        with col2:
            sd = datetime.now() if not project.master_data.start_date else datetime.strptime(project.master_data.start_date, "%Y-%m-%d")
            project.master_data.start_date = st.date_input("Start Date", sd).strftime("%Y-%m-%d")
            project.master_data.budget = st.number_input("Budget (CHF)", min_value=0.0, value=float(project.master_data.budget or 100000.0))
            project.master_data.approach = st.selectbox("Approach", ["classical", "agile"], index=0 if project.master_data.approach=="classical" else 1)
            project.master_data.project_size = st.selectbox("Project Size", ["small","medium","large"], index=["small","medium","large"].index(project.master_data.project_size))
            project.master_data.language = st.selectbox("Language / Sprache", ["en","de"], index=0 if project.master_data.language=="en" else 1)
        if st.form_submit_button("Initialize Project"):
            # apply tailoring
            apply_tailoring(project)
            st.success("Project initialized and tailoring applied!")

def apply_tailoring(project: HermesProject):
    cfg = PROJECT_SIZE_CONFIGS.get(project.master_data.project_size, PROJECT_SIZE_CONFIGS["medium"])
    # mark documents
    for docname, doc in project.documents.items():
        doc.required = docname in cfg["required_documents"]
    # add any missing required documents
    for dn in cfg["required_documents"]:
        if dn not in project.documents:
            project.documents[dn] = HermesDocument(name=dn, responsible="Project Manager", required=True)
    project.tailoring = {"size": project.master_data.project_size, "simplified_checklists": cfg["simplified_checklists"]}
    # ensure mandatory milestones present
    for mn in cfg["mandatory_milestones"]:
        if not any(m.name == mn for m in project.milestones):
            # map names to phases roughly
            phase_map = {
                "Project Start":"initialization",
                "Implementation Decision":"concept",
                "Phase Release Concept":"concept",
                "Phase Release Realization":"implementation",
                "Project Completed":"completion"
            }
            project.milestones.append(HermesMilestone(name=mn, phase=phase_map.get(mn, "implementation"), mandatory=True))

# ----------------------
# RESULTS MANAGEMENT
# ----------------------
def results_management():
    st.header("📋 Results Management")
    project = st.session_state.hermes_project
    show_instructions("Results Management", t("results", project))
    for phase_key, phase in project.phases.items():
        with st.expander(f"{phase.name} (status: {phase.status})", expanded=False):
            # create results if empty (defaults)
            if not phase.results:
                # add example results depending on phase
                if phase_key == "initialization":
                    phase.results["Project Charter"] = PhaseResult(name="Project Charter", approval_required=True, responsible_role="Project Manager")
                    phase.results["Stakeholder Analysis"] = PhaseResult(name="Stakeholder Analysis", responsible_role="Project Manager")
                elif phase_key == "concept":
                    phase.results["Solution Requirements"] = PhaseResult(name="Solution Requirements", approval_required=True, responsible_role="User Representative")
                    phase.results["Solution Architecture"] = PhaseResult(name="Solution Architecture", approval_required=True, responsible_role="Project Manager")
                elif phase_key == "implementation":
                    phase.results["Increment Delivery"] = PhaseResult(name="Increment Delivery", responsible_role="Project Manager")
                elif phase_key == "introduction":
                    phase.results["Operational Handover"] = PhaseResult(name="Operational Handover", responsible_role="Project Manager")
                elif phase_key == "completion":
                    phase.results["Project Completion Report"] = PhaseResult(name="Project Completion Report", approval_required=True, responsible_role="Project Manager")
            for rkey, result in phase.results.items():
                cols = st.columns([3,1,1])
                with cols[0]:
                    st.write(f"**{result.name}**")
                    if result.description:
                        st.caption(result.description)
                    st.caption(f"Responsible Role: {result.responsible_role or '—'}")
                with cols[1]:
                    new_status = st.selectbox(f"Status {phase_key}_{rkey}", ["not_started","in_progress","completed","approved"], index=["not_started","in_progress","completed","approved"].index(result.status))
                    if new_status != result.status:
                        result.status = new_status
                        if new_status == "approved":
                            result.approval_date = datetime.now().strftime("%Y-%m-%d")
                with cols[2]:
                    if result.approval_required and result.status == "completed":
                        if st.button(f"Request Approval {phase_key}_{rkey}"):
                            result.status = "approved"
                            result.approval_date = datetime.now().strftime("%Y-%m-%d")
                            st.success("Result approved")

# ----------------------
# DOCUMENTS CENTER
# ----------------------
def documents_center():
    st.header("📄 Documents")
    project = st.session_state.hermes_project
    show_instructions("Documents", t("documents", project))
    if not project.documents:
        st.info("No documents configured yet. Initialize project first.")
        return
    # stats
    st.metric("Total documents", len(project.documents))
    for dname, doc in project.documents.items():
        with st.expander(f"{dname} - {doc.status}", expanded=False):
            cols = st.columns([3,1])
            with cols[0]:
                st.write(f"**Responsible:** {doc.responsible}")
                st.write(f"**Linked Result:** {doc.linked_result or '—'}")
                doc.content = st.text_area(f"Content for {dname}", value=doc.content, key=f"content_{dname}")
            with cols[1]:
                new = st.selectbox(f"Status_{dname}", ["not_started","in_progress","completed"], index=["not_started","in_progress","completed"].index(doc.status))
                if new != doc.status:
                    doc.status = new
                    # sync to result if applicable
                    if doc.status == "completed" and doc.linked_result:
                        for p in project.phases.values():
                            if doc.linked_result in p.results:
                                p.results[doc.linked_result].status = "completed"
                                st.success(f"Linked result '{doc.linked_result}' updated to completed")
                                break

# ----------------------
# BUDGET MANAGEMENT
# ----------------------
def budget_management():
    st.header("💰 Budget Management")
    project = st.session_state.hermes_project
    show_instructions("Budget Management", t("budget", project))
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Planned Budget", f"CHF {project.master_data.budget:,.2f}")
        actual = sum(t.amount for t in project.budget_entries if t.type=="actual")
        st.metric("Actual Costs", f"CHF {actual:,.2f}")
        st.metric("Remaining", f"CHF {project.master_data.budget - actual:,.2f}")
        usage = calculate_budget_usage(project)
        if usage < 0.7:
            st.success(f"Budget Usage: {usage:.1%}")
        elif usage < 0.9:
            st.warning(f"Budget Usage: {usage:.1%}")
        else:
            st.error(f"Budget Usage: {usage:.1%}")
    with col2:
        with st.form("tx_form"):
            date = st.date_input("Date", datetime.now())
            cat = st.selectbox("Category", ["Personnel","Hardware","Software","External Services","Training","Travel","Other"])
            amt = st.number_input("Amount (CHF)", min_value=0.0, value=0.0, step=100.0)
            desc = st.text_input("Description")
            typ = st.selectbox("Type", ["actual","planned"])
            if st.form_submit_button("Add Transaction"):
                tx = BudgetTransaction(date=date.strftime("%Y-%m-%d"), category=cat, amount=amt, description=desc, type=typ)
                project.budget_entries.append(tx)
                st.success("Transaction added")
                st.experimental_rerun()
    # show table and charts
    if project.budget_entries:
        df = pd.DataFrame([asdict(t) for t in project.budget_entries])
        st.dataframe(df, use_container_width=True)
        # pie by category (actual)
        df_act = df[df['type']=='actual']
        if not df_act.empty:
            cat_sum = df_act.groupby('category')['amount'].sum()
            fig = px.pie(values=cat_sum.values, names=cat_sum.index, title="Spending by Category")
            st.plotly_chart(fig, use_container_width=True)
            # cumulative
            df_act['date'] = pd.to_datetime(df_act['date'])
            ts = df_act.groupby('date')['amount'].sum().cumsum()
            fig2 = px.line(x=ts.index, y=ts.values, title="Cumulative Spending")
            st.plotly_chart(fig2, use_container_width=True)
        # export
        if st.button("Export transactions to Excel"):
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as w:
                df.to_excel(w, sheet_name='Transactions', index=False)
            st.download_button("Download Excel", data=buf.getvalue(), file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ----------------------
# MILESTONES (visual + governance)
# ----------------------
def validate_milestone_completion(ms: HermesMilestone, project: HermesProject) -> Dict[str,bool]:
    result = {"phase_results_complete": True, "required_documents_complete": True, "checklists_complete": True, "can_reach": True}
    phase = project.phases.get(ms.phase)
    if phase:
        for r in phase.results.values():
            if r.approval_required and r.status != "approved":
                result["phase_results_complete"]=False
                break
        for doc_name in phase.required_documents:
            d = project.documents.get(doc_name)
            if d and d.required and d.status != "completed":
                result["required_documents_complete"]=False
                break
        if phase.checklist_results:
            if not all(phase.checklist_results.values()):
                result["checklists_complete"]=False
    result["can_reach"] = all([result["phase_results_complete"], result["required_documents_complete"], result["checklists_complete"]])
    return result

def milestones_view():
    st.header("🎯 Milestones")
    project = st.session_state.hermes_project
    show_instructions("Milestone Management", t("milestones", project))
    if not project.milestones:
        st.info("No milestones configured.")
        return
    # plot
    dates = []
    labels = []
    colors_map = []
    for i, ms in enumerate(project.milestones):
        d = datetime.now() if not ms.date else datetime.strptime(ms.date, "%Y-%m-%d")
        dates.append(d)
        labels.append(ms.name)
        colors_map.append("green" if ms.status=="reached" else "blue")
    fig = go.Figure()
    for i,(d,l,c) in enumerate(zip(dates, labels, colors_map)):
        fig.add_trace(go.Scatter(x=[d], y=[i], mode='markers+text', marker=dict(size=14, color=c), text=[l], textposition='middle right'))
    fig.update_layout(yaxis=dict(showticklabels=False), height=350, title="Milestone timeline")
    st.plotly_chart(fig, use_container_width=True)
    # details
    for ms in project.milestones:
        with st.expander(f"{ms.name} ({ms.phase}) - {ms.status}", expanded=False):
            st.write(f"Mandatory: {'Yes' if ms.mandatory else 'No'}")
            if ms.date:
                st.write("Date:", ms.date)
            validation = validate_milestone_completion(ms, project)
            if validation["phase_results_complete"]:
                st.success("Phase results OK")
            else:
                st.error("Phase results not OK")
            if validation["required_documents_complete"]:
                st.success("Required docs OK")
            else:
                st.error("Required docs missing")
            if validation["checklists_complete"]:
                st.success("Checklists OK")
            else:
                st.error("Checklists not OK")
            if ms.status != "reached":
                if validation["can_reach"]:
                    if st.button(f"Reach milestone: {ms.name}"):
                        ms.status = "reached"
                        ms.date = datetime.now().strftime("%Y-%m-%d")
                        st.success("Milestone reached")
                        st.experimental_rerun()
                else:
                    st.info("Milestone prerequisites not fulfilled")

# ----------------------
# ITERATIONS & RELEASES
# ----------------------
def iterations_view():
    st.header("🔄 Iterations & Releases")
    project = st.session_state.hermes_project
    show_instructions("Iterations & Releases", t("iterations", project))
    if project.master_data.approach != "agile":
        st.info("Switch project approach to 'agile' to manage iterations.")
        return
    with st.expander("➕ Create new iteration", expanded=False):
        with st.form("it_form"):
            num = st.number_input("Iteration number", min_value=1, value=1)
            name = st.text_input("Name", f"Sprint {num}")
            sd = st.date_input("Start date", datetime.now())
            ed = st.date_input("End date", datetime.now()+timedelta(days=14))
            total = st.number_input("Total user stories", min_value=0, value=10)
            rc = st.checkbox("Release candidate")
            goals = st.text_area("Goals (one per line)").splitlines()
            if st.form_submit_button("Create iteration"):
                it = Iteration(number=int(num), name=name, start_date=sd.strftime("%Y-%m-%d"), end_date=ed.strftime("%Y-%m-%d"),
                               total_user_stories=int(total), release_candidate=rc, goals=[g.strip() for g in goals if g.strip()])
                project.iterations.append(it)
                # create release result and doc
                release_result_name = f"Release {it.number}"
                impl = project.phases.get("implementation")
                if impl and release_result_name not in impl.results:
                    impl.results[release_result_name] = PhaseResult(name=release_result_name, approval_required=True, responsible_role="Project Manager")
                release_doc_name = f"Release Report {it.number}"
                if release_doc_name not in project.documents:
                    project.documents[release_doc_name] = HermesDocument(name=release_doc_name, responsible="Project Manager", linked_result=release_result_name)
                st.success("Iteration created")
                st.experimental_rerun()
    # display iterations
    for it in project.iterations:
        with st.expander(f"{it.number} - {it.name} ({it.status})", expanded=False):
            st.write(f"Period: {it.start_date} to {it.end_date}")
            st.write(f"Progress: {it.progress():.1f}%")
            it.completed_user_stories = st.number_input(f"Completed stories {it.number}", min_value=0, max_value=it.total_user_stories, value=it.completed_user_stories, key=f"comp_{it.number}")
            it.status = st.selectbox(f"Status {it.number}", ["planned","active","completed"], index=["planned","active","completed"].index(it.status), key=f"status_{it.number}")
            if it.release_candidate:
                st.info("Release candidate")
                # validation for approval
                validation = validate_release_approval(it, project)
                st.write("Release validation:")
                for k,v in validation.items():
                    st.write(f"{k}: {'OK' if v else 'NO'}")
                if not it.release_approved and validation.get("can_approve", False):
                    if st.button(f"Approve release {it.number}"):
                        it.release_approved = True
                        it.status = "completed"
                        # mark release result approved
                        impl = project.phases.get("implementation")
                        rr = f"Release {it.number}"
                        if impl and rr in impl.results:
                            impl.results[rr].status = "approved"
                            impl.results[rr].approval_date = datetime.now().strftime("%Y-%m-%d")
                        # add milestone
                        project.milestones.append(HermesMilestone(name=f"Release {it.number}", phase="implementation", date=datetime.now().strftime("%Y-%m-%d"), status="reached", mandatory=False))
                        st.success("Release approved")

# release validation (safe)
def validate_release_approval(iteration: Iteration, project: HermesProject) -> Dict[str,bool]:
    res = {"release_document_complete": True, "release_result_approved": True, "budget_healthy": True, "milestones_on_track": True, "can_approve": True}
    rdoc = project.documents.get(f"Release Report {iteration.number}")
    if not rdoc or rdoc.status != "completed":
        res["release_document_complete"] = False
    impl = project.phases.get("implementation")
    rr = f"Release {iteration.number}"
    if not impl or rr not in impl.results or impl.results[rr].status not in ["completed","approved"]:
        res["release_result_approved"] = False
    # budget health: safe calc
    usage = calculate_budget_usage(project)
    if usage > 0.9:
        res["budget_healthy"] = False
    # mandatory implementation-phase milestones reached?
    cms = [m for m in project.milestones if m.mandatory and m.phase=="implementation"]
    if any(m.status != "reached" for m in cms):
        res["milestones_on_track"] = False
    res["can_approve"] = all([res["release_document_complete"], res["release_result_approved"], res["budget_healthy"], res["milestones_on_track"]])
    return res

# ----------------------
# REPORTS (PDF & EXCEL) WITH CHARTS
# ----------------------
def generate_budget_chart_png(project: HermesProject) -> BytesIO:
    actual = sum(t.amount for t in project.budget_entries if t.type=="actual")
    planned = project.master_data.budget or 0.0
    remaining = max(planned - actual, 0.0)
    labels = ["Actual", "Remaining"]
    vals = [actual, remaining]
    fig, ax = plt.subplots(figsize=(4,3))
    ax.pie(vals, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Budget Usage")
    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_status_report_pdf(project: HermesProject) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"HERMES Project Status Report - {project.master_data.project_name}", styles['Title']))
    story.append(Spacer(1,12))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Spacer(1,8))
    # executive summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    tot = calculate_total_progress(project)
    usage = calculate_budget_usage(project)
    story.append(Paragraph(f"Overall progress: {tot:.1f}%, Budget used: {usage:.1%}", styles['Normal']))
    story.append(Spacer(1,8))
    # budget chart
    chart = generate_budget_chart_png(project)
    story.append(Image(chart, width=300, height=200))
    story.append(Spacer(1,12))
    # phases table (simple)
    data = [["Phase","Status","Progress"]]
    for k,p in project.phases.items():
        data.append([p.name, p.status, f"{calculate_phase_progress(p):.1f}%"])
    tbl = Table(data, colWidths=[150,150,150])
    tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.darkblue),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    story.append(tbl)
    story.append(Spacer(1,12))
    # milestones
    msdata = [["Milestone","Phase","Status","Date"]]
    for m in project.milestones:
        msdata.append([m.name, m.phase, m.status, m.date or "Not set"])
    ms_tbl = Table(msdata, colWidths=[150,120,100,100])
    ms_tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.darkblue),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    story.append(ms_tbl)
    story.append(Spacer(1,12))
    # recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    if usage > 0.8:
        story.append(Paragraph("Review budget allocation - high usage detected", styles['Normal']))
    # build and return
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

def generate_status_report_excel(project: HermesProject) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        # Master
        md = project.master_data
        dfm = pd.DataFrame([{"Project Name": md.project_name, "Client": md.client, "Project Manager": md.project_manager, "Start Date": md.start_date, "Budget": md.budget, "Approach": md.approach, "Size": md.project_size}])
        dfm.to_excel(writer, sheet_name='Master', index=False)
        # phases
        phases_list = []
        for k,p in project.phases.items():
            phases_list.append({"Phase": p.name, "Status": p.status, "Progress": f"{calculate_phase_progress(p):.1f}%"})
        pd.DataFrame(phases_list).to_excel(writer, sheet_name='Phases', index=False)
        # milestones
        pd.DataFrame([asdict(m) for m in project.milestones]).to_excel(writer, sheet_name='Milestones', index=False)
        # budget transactions
        if project.budget_entries:
            pd.DataFrame([asdict(t) for t in project.budget_entries]).to_excel(writer, sheet_name='Transactions', index=False)
        # results
        results = []
        for pk,p in project.phases.items():
            for rn,r in p.results.items():
                results.append({"Phase": p.name, "Result": r.name, "Status": r.status, "Approval required": r.approval_required, "Approval date": r.approval_date, "Responsible": r.responsible_role})
        pd.DataFrame(results).to_excel(writer, sheet_name='Results', index=False)
    buf.seek(0)
    return buf.getvalue()

# ----------------------
# PERSISTENCE: export/import project JSON
# ----------------------
def export_project_json(project: HermesProject) -> bytes:
    d = dataclass_to_dict(project)
    return json.dumps(d, indent=2).encode("utf-8")

def import_project_json_bytes(b: bytes) -> HermesProject:
    try:
        d = json.loads(b.decode("utf-8"))
        return dict_to_dataclass(d)
    except Exception as e:
        st.error(f"Import error: {e}")
        return HermesProject()

# ----------------------
# DASHBOARD
# ----------------------
def dashboard_view():
    project = st.session_state.hermes_project
    st.header("🏠 Dashboard")
    show_instructions("Dashboard", t("dashboard", project))
    if not project.master_data.project_name:
        st.info("Initialize project first")
        return
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric("Project", project.master_data.project_name)
    with col2:
        st.metric("Approach", project.master_data.approach.title())
    with col3:
        st.metric("Size", project.master_data.project_size.title())
    with col4:
        st.metric("Language", project.master_data.language.upper())
    # phase progress
    st.subheader("Phase progress")
    for k,p in project.phases.items():
        prog = calculate_phase_progress(p)
        st.write(f"**{p.name}**: {prog:.1f}%")
        st.progress(prog/100)
    # next milestones
    st.subheader("Next milestones")
    nextms = [m for m in project.milestones if m.status == "planned"][:5]
    if nextms:
        for m in nextms:
            st.write(f"- {m.name} ({m.phase})")
    else:
        st.write("No upcoming milestones")
    # reports
    st.markdown("---")
    st.subheader("Reports")
    if st.button("Download PDF Report"):
        pdf = generate_status_report_pdf(project)
        st.download_button("Download PDF", data=pdf, file_name=f"status_{project.master_data.project_name}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")
    if st.button("Download Excel Report"):
        x = generate_status_report_excel(project)
        st.download_button("Download Excel", data=x, file_name=f"status_{project.master_data.project_name}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ----------------------
# SIDEBAR: save/load
# ----------------------
def sidebar_persistence():
    st.sidebar.header("Project persistence")
    project = st.session_state.hermes_project
    # export JSON
    if st.sidebar.button("Export project (JSON)"):
        data = export_project_json(project)
        st.sidebar.download_button("Download project JSON", data=data, file_name=f"hermes_project_{project.master_data.project_name or 'project'}_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")
    # import JSON
    uploaded = st.sidebar.file_uploader("Import project JSON", type=["json"])
    if uploaded is not None:
        try:
            newproj = import_project_json_bytes(uploaded.read())
            st.session_state.hermes_project = newproj
            st.sidebar.success("Project imported")
            st.experimental_rerun()
        except Exception as e:
            st.sidebar.error(f"Import failed: {e}")

# ----------------------
# ENTRY POINT
# ----------------------
def main():
    st.set_page_config(page_title="HERMES 2022 App", layout="wide")
    init_session_state()
    sidebar_persistence()
    st.title("HERMES 2022 — Project Management Toolkit")
    # navigation
    menu = st.sidebar.radio("Navigation", ["Dashboard","Project Initialization","Results","Documents","Budget","Milestones","Iterations","Reports","Information"])
    if menu == "Dashboard":
        dashboard_view()
    elif menu == "Project Initialization":
        project_initialization()
    elif menu == "Results":
        results_management()
    elif menu == "Documents":
        documents_center()
    elif menu == "Budget":
        budget_management()
    elif menu == "Milestones":
        milestones_view()
    elif menu == "Iterations":
        iterations_view()
    elif menu == "Reports":
        st.header("Reports")
        project = st.session_state.hermes_project
        show_instructions("Reports","Generate professional PDF/Excel reports including charts and export project JSON.")
        if st.button("Generate PDF report"):
            pdf = generate_status_report_pdf(project)
            st.download_button("Download PDF", data=pdf, file_name=f"status_{project.master_data.project_name}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")
        if st.button("Generate Excel report"):
            x = generate_status_report_excel(project)
            st.download_button("Download Excel", data=x, file_name=f"status_{project.master_data.project_name}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif menu == "Information":
        st.header("Information")
        project = st.session_state.hermes_project
        show_instructions("Info", t("info", project))
        st.write("This HERMES app supports classical and agile projects with tailoring, checklists, documents, milestones and reporting.")
    # footer: show quick status
    st.markdown("---")
    project = st.session_state.hermes_project
    st.caption(f"Project: {project.master_data.project_name or '[none]'} | Phase: {project.current_phase} | Progress: {calculate_total_progress(project):.1f}%")

if __name__ == "__main__":
    main()
