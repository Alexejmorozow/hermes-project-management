# app.py
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# =========================================
# DATACLASSES (KERN)
# =========================================
@dataclass
class ProjectMasterData:
    project_name: str = ""
    client: str = ""
    project_manager: str = ""
    user_representative: str = ""
    start_date: str = ""
    budget: float = 0.0
    approach: str = "classical"
    project_size: str = "medium"
    current_phase: str = "initialization"

@dataclass
class PhaseResult:
    name: str
    description: str = ""
    status: str = "not_started"  # not_started, in_progress, completed, approved
    approval_required: bool = False
    approval_date: str = ""
    responsible_role: str = ""

@dataclass
class ProjectPhase:
    name: str
    results: Dict[str, PhaseResult] = field(default_factory=dict)
    required_documents: List[str] = field(default_factory=list)
    checklist_results: Dict[str, bool] = field(default_factory=dict)
    status: str = "not_started"  # not_started, active, completed
    start_date: str = ""
    end_date: str = ""

@dataclass
class HermesDocument:
    name: str
    responsible: str = ""
    status: str = "not_started"  # not_started, in_progress, completed
    required: bool = True
    linked_result: str = ""
    content: str = ""

@dataclass
class HermesMilestone:
    name: str
    phase: str
    date: str = ""
    status: str = "planned"  # planned, reached, delayed
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
    roles: Dict[str, str] = field(default_factory=dict)  # role -> person

# =========================================
# KONFIGURATIONEN / TEMPLATES / CHECKLISTS
# =========================================
# Phase labels used in UI
HERMES_PHASE_LABELS_CLASSICAL = {
    "initialization": "Initialization",
    "concept": "Concept",
    "realization": "Realization",
    "introduction": "Introduction",
    "completion": "Completion"
}
HERMES_PHASE_LABELS_AGILE = {
    "initialization": "Initialization",
    "implementation": "Implementation",
    "completion": "Completion"
}

# Minimal results templates (can be extended)
RESULT_TEMPLATES = {
    "Project Charter": {"description": "Formal project initiation document", "approval_required": True, "role": "project_manager"},
    "Stakeholder Analysis": {"description": "Identification and analysis of stakeholders", "approval_required": False, "role": "project_manager"},
    "Requirements Specification": {"description": "Detailed requirements", "approval_required": True, "role": "user_representative"},
    "Solution Concept": {"description": "High-level solution description", "approval_required": True, "role": "project_manager"},
    # Releases for agile
    "Release 1": {"description": "First product release", "approval_required": True, "role": "project_manager"},
    "Release 2": {"description": "Second product release", "approval_required": True, "role": "project_manager"},
}

# Project size configs (tailoring)
@dataclass
class ProjectSizeConfig:
    required_documents: List[str] = field(default_factory=list)
    optional_documents: List[str] = field(default_factory=list)
    simplified_checklists: bool = False
    mandatory_milestones: List[str] = field(default_factory=list)
    extra_roles: List[str] = field(default_factory=list)

PROJECT_SIZE_CONFIGS = {
    "small": ProjectSizeConfig(
        required_documents=["Project Charter", "Acceptance Protocol"],
        optional_documents=["Study", "Migration Concept"],
        simplified_checklists=True,
        mandatory_milestones=["Project Initialization", "Project Completion"],
        extra_roles=[]
    ),
    "medium": ProjectSizeConfig(
        required_documents=["Project Charter", "Project Management Plan", "Requirements Specification", "Solution Concept", "Acceptance Protocol"],
        optional_documents=["Migration Concept"],
        simplified_checklists=False,
        mandatory_milestones=["Project Initialization", "Implementation Decision", "Project Completion"],
        extra_roles=["project_controller"]
    ),
    "large": ProjectSizeConfig(
        required_documents=["Project Charter", "Project Management Plan", "Requirements Specification", "Solution Concept", "Test Concept", "Acceptance Protocol", "Project Completion Report"],
        optional_documents=[],
        simplified_checklists=False,
        mandatory_milestones=["Project Initialization", "Implementation Decision", "Phase Release Concept", "Phase Release Realization", "Project Completion"],
        extra_roles=["project_controller", "quality_manager"]
    )
}

# Checklists
HERMES_CHECKLISTS = {
    "initialization_comprehensive": [
        "Project mandate verified",
        "Stakeholder analysis performed",
        "Budget & resources sufficient",
        "High-level risks identified",
        "Project approach decided"
    ],
    "initialization_simplified": [
        "Project mandate exists",
        "Responsible persons assigned"
    ],
    "concept_comprehensive": [
        "Requirements validated with users",
        "Solution alternatives assessed",
        "Economic efficiency proven",
        "Security & protection considered"
    ],
    "concept_simplified": [
        "Requirements discussed",
        "Solution direction agreed"
    ],
    "implementation_comprehensive": [
        "Test strategy defined",
        "Migration concept finalized",
        "Operational readiness planned"
    ],
    "completion_comprehensive": [
        "Operational handover completed",
        "Final acceptance signed",
        "Lessons learned documented",
        "Financial closure performed"
    ],
    "completion_simplified": [
        "Handover done",
        "Acceptance obtained"
    ]
}

# Default roles
DEFAULT_HERMES_ROLES = {
    "client": "Client",
    "project_manager": "Project Manager",
    "user_representative": "User Representative",
    "project_controller": "Project Controller",
    "quality_manager": "Quality Manager"
}

# =========================================
# INSTRUCTIONS HELPER
# =========================================
def show_instructions(title: str, text: str, expanded: bool = True):
    """Show an instruction block with a title and text"""
    with st.expander(f"ℹ️ {title} — Instructions", expanded=expanded):
        st.markdown(text)

# =========================================
# INITIALIZATION / SESSION STATE
# =========================================
def init_session_state():
    if "hermes_project" not in st.session_state:
        p = HermesProject()
        # By default create classical phases
        p.master_data.current_phase = "initialization"
        st.session_state.hermes_project = p
    # ensure some helper containers exist
    proj = st.session_state.hermes_project
    if not proj.phases:
        initialize_standard_phases(proj)
    if not proj.documents:
        init_project_structure(proj)
    if not proj.roles:
        proj.roles = DEFAULT_HERMES_ROLES.copy()

def initialize_standard_phases(project: HermesProject):
    """Initialize phases depending on approach (default classical)"""
    labels = HERMES_PHASE_LABELS_CLASSICAL if project.master_data.approach == "classical" else HERMES_PHASE_LABELS_AGILE
    project.phases.clear()
    for key, lbl in labels.items():
        project.phases[key] = ProjectPhase(name=lbl)
        # Add default checklist based on size and phase later when tailoring applied

def init_project_structure(project: HermesProject):
    """Initialize default documents and some default results from templates"""
    # create standard documents (from templates and required lists)
    docs = {
        "Project Charter": HermesDocument(name="Project Charter", responsible="Project Manager", required=True, linked_result="Project Charter"),
        "Stakeholder Analysis": HermesDocument(name="Stakeholder Analysis", responsible="Project Manager", required=True, linked_result="Stakeholder Analysis"),
        "Requirements Specification": HermesDocument(name="Requirements Specification", responsible="User Representative", required=True, linked_result="Requirements Specification"),
        "Solution Concept": HermesDocument(name="Solution Concept", responsible="Project Manager", required=True, linked_result="Solution Concept"),
        "Acceptance Protocol": HermesDocument(name="Acceptance Protocol", responsible="Client", required=True),
        "Project Completion Report": HermesDocument(name="Project Completion Report", responsible="Project Manager", required=True)
    }
    project.documents.update(docs)

    # init default results in phases from RESULT_TEMPLATES where reasonable
    for phase_key, phase in project.phases.items():
        # common mapping (simplified for demo)
        if phase_key == "initialization":
            names = ["Project Charter", "Stakeholder Analysis"]
        elif phase_key == "concept":
            names = ["Requirements Specification", "Solution Concept"]
        elif phase_key == "implementation" or phase_key == "realization":
            names = ["Test Concept"]
        elif phase_key == "introduction":
            names = ["Acceptance Protocol", "Operational Handover"] if "Operational Handover" in RESULT_TEMPLATES else ["Acceptance Protocol"]
        else:
            names = []
        for name in names:
            tmpl = RESULT_TEMPLATES.get(name, {"description": "", "approval_required": False, "role": ""})
            phase.results[name] = PhaseResult(
                name=name,
                description=tmpl["description"],
                status="not_started",
                approval_required=tmpl.get("approval_required", False),
                responsible_role=tmpl.get("role", "")
            )

# =========================================
# TAILORING (project size)
# =========================================
def apply_project_size_tailoring(project: HermesProject):
    """Apply tailoring according to project.master_data.project_size"""
    config = PROJECT_SIZE_CONFIGS.get(project.master_data.project_size, PROJECT_SIZE_CONFIGS["medium"])
    # mark docs required/optional
    for name, doc in project.documents.items():
        if name in config.required_documents:
            doc.required = True
        elif name in config.optional_documents:
            doc.required = False
    # set checklist items for phases
    for key, phase in project.phases.items():
        if config.simplified_checklists:
            # choose simplified variant if exists
            checklist_key = f"{key}_simplified"
            # fallback to comprehensive
            checklist_items = HERMES_CHECKLISTS.get(checklist_key, HERMES_CHECKLISTS.get(f"{key}_comprehensive", []))
        else:
            checklist_items = HERMES_CHECKLISTS.get(f"{key}_comprehensive", [])
        # initialize checklist results if not present
        for item in checklist_items:
            if item not in phase.checklist_results:
                phase.checklist_results[item] = False
    # apply roles extras
    for r in config.extra_roles:
        if r not in project.roles:
            project.roles[r] = r.replace("_", " ").title()
    project.tailoring = {"applied_size": project.master_data.project_size, "config": config}

# =========================================
# VALIDATION, GOVERNANCE, HELPERS
# =========================================
def validate_minimal_roles(project: HermesProject) -> List[str]:
    missing = []
    if not project.master_data.project_manager:
        missing.append("Project Manager")
    if not project.master_data.user_representative:
        missing.append("User Representative")
    if not project.master_data.client:
        missing.append("Client")
    return missing

def validate_phase_completion(phase: ProjectPhase) -> Dict[str, bool]:
    """Check whether a phase can be completed: all approval-required results approved, required docs completed, checklist items done"""
    result_ok = True
    for r in phase.results.values():
        if r.approval_required and r.status != "approved":
            result_ok = False
            break
    docs_ok = True
    # find documents linked to results in this phase and required docs specifically listed
    for doc_name in phase.required_documents:
        doc = st.session_state.hermes_project.documents.get(doc_name)
        if doc and doc.required and doc.status != "completed":
            docs_ok = False
            break
    checklist_ok = all(phase.checklist_results.values()) if phase.checklist_results else True
    return {
        "results_completed": result_ok,
        "documents_ready": docs_ok,
        "checklists_completed": checklist_ok,
        "can_complete": result_ok and docs_ok and checklist_ok
    }

def validate_milestone_completion(milestone: HermesMilestone, project: HermesProject) -> Dict[str, bool]:
    """Check milestone against its phase prerequisites"""
    validation = {
        "phase_results_complete": True,
        "required_documents_complete": True,
        "checklists_complete": True,
        "can_reach": True
    }
    phase = project.phases.get(milestone.phase)
    if not phase:
        validation["can_reach"] = False
        return validation
    # phase results
    for r in phase.results.values():
        if r.approval_required and r.status != "approved":
            validation["phase_results_complete"] = False
            break
    # required docs
    for doc_name in phase.required_documents:
        doc = project.documents.get(doc_name)
        if doc and doc.required and doc.status != "completed":
            validation["required_documents_complete"] = False
            break
    # checklists
    if phase.checklist_results:
        if not all(phase.checklist_results.values()):
            validation["checklists_complete"] = False
    validation["can_reach"] = validation["phase_results_complete"] and validation["required_documents_complete"] and validation["checklists_complete"]
    return validation

def calculate_total_progress(project: HermesProject) -> float:
    if not project.phases:
        return 0.0
    vals = []
    for p in project.phases.values():
        vals.append(calculate_phase_progress(p))
    return sum(vals) / len(vals) if vals else 0.0

def calculate_phase_progress(phase: ProjectPhase) -> float:
    total = len(phase.results)
    if total == 0:
        return 0.0
    completed = sum(1 for r in phase.results.values() if r.status in ("completed", "approved"))
    return (completed / total) * 100

def calculate_budget_usage(project: HermesProject) -> float:
    actual = sum(t.amount for t in project.budget_entries if t.type == "actual")
    if project.master_data.budget and project.master_data.budget > 0:
        return actual / project.master_data.budget
    return 0.0

def calculate_risk_level(project: HermesProject) -> str:
    # simple heuristic: based on percent completed
    prog = calculate_total_progress(project)
    if prog > 80:
        return "low"
    elif prog > 50:
        return "medium"
    else:
        return "high"

def calculate_quality_score(project: HermesProject) -> int:
    # basic: ratio of approved results + completed checklists
    total_items = 0
    completed_items = 0
    for p in project.phases.values():
        for r in p.results.values():
            total_items += 1
            if r.status == "approved":
                completed_items += 1
        for done in p.checklist_results.values():
            total_items += 1
            if done:
                completed_items += 1
    return int((completed_items / total_items) * 100) if total_items > 0 else 0

def sync_document_to_result(document: HermesDocument, project: HermesProject):
    """If doc is completed and linked to a result, mark that result completed"""
    if document.linked_result and document.status == "completed":
        for phase in project.phases.values():
            if document.linked_result in phase.results:
                res = phase.results[document.linked_result]
                if res.status not in ("completed", "approved"):
                    res.status = "completed"

def auto_advance_phase(project: HermesProject):
    """Try to move current_phase forward automatically if criteria met"""
    current = project.master_data.current_phase
    phase_keys = list(project.phases.keys())
    if current not in phase_keys:
        return
    idx = phase_keys.index(current)
    phase = project.phases[current]
    validation = validate_phase_completion(phase)
    # find milestone for release of this phase (heuristic: milestone exists that's mandatory and refers to this phase)
    milestone_ready = any(ms.phase == current and ms.status == "reached" for ms in project.milestones)
    if validation["can_complete"] and milestone_ready:
        # complete current and activate next
        phase.status = "completed"
        phase.end_date = datetime.now().strftime("%Y-%m-%d")
        if idx + 1 < len(phase_keys):
            next_key = phase_keys[idx + 1]
            project.master_data.current_phase = next_key
            project.phases[next_key].status = "active"
            project.phases[next_key].start_date = datetime.now().strftime("%Y-%m-%d")
            st.success(f"Phase '{phase.name}' completed — next phase '{project.phases[next_key].name}' activated")

# =========================================
# REPORT GENERATION (PDF + EXCEL)
# =========================================
def generate_project_status_report_pdf(project: HermesProject) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    # Title
    story.append(Paragraph(f"HERMES Project Status Report - {project.master_data.project_name}", styles['Title']))
    story.append(Spacer(1, 12))
    # Executive summary
    total_progress = calculate_total_progress(project)
    budget_usage = calculate_budget_usage(project)
    summary = f"Project is {total_progress:.1f}% complete. Budget usage is {budget_usage:.1%}."
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 12))
    # Master data table
    master_table = [
        ["Project Name", project.master_data.project_name],
        ["Client", project.master_data.client],
        ["Project Manager", project.master_data.project_manager],
        ["User Representative", project.master_data.user_representative],
        ["Approach", project.master_data.approach],
        ["Project Size", project.master_data.project_size],
        ["Start Date", project.master_data.start_date],
        ["Budget (CHF)", f"{project.master_data.budget:,.2f}"]
    ]
    t = Table(master_table, colWidths=[180, 300])
    t.setStyle(TableStyle([('BACKGROUND', (0,0),(0,-1), colors.lightgrey), ('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    story.append(t)
    story.append(Spacer(1, 12))
    # Phase table
    phase_data = [["Phase", "Status", "Progress", "Completed Results"]]
    for key, phase in project.phases.items():
        completed_results = sum(1 for r in phase.results.values() if r.status in ("completed","approved"))
        total_results = len(phase.results)
        phase_data.append([phase.name, phase.status, f"{calculate_phase_progress(phase):.1f}%", f"{completed_results}/{total_results}"])
    pt = Table(phase_data, colWidths=[150, 80, 80, 120])
    pt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.darkblue), ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke), ('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    story.append(pt)
    story.append(Spacer(1, 12))
    # Milestones
    ms_data = [["Milestone","Phase","Status","Date"]]
    for ms in project.milestones:
        ms_data.append([ms.name, ms.phase, ms.status, ms.date or "Not set"])
    mst = Table(ms_data, colWidths=[160, 120, 80, 100])
    mst.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.darkblue), ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke), ('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    story.append(mst)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_project_status_report_excel(project: HermesProject) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Executive summary
        summary = {
            "Metric": ["Overall Progress","Budget Usage","Completed Phases","Reached Milestones"],
            "Value": [f"{calculate_total_progress(project):.1f}%", f"{calculate_budget_usage(project):.1%}", f"{sum(1 for p in project.phases.values() if p.status=='completed')}/{len(project.phases)}", f"{sum(1 for m in project.milestones if m.status=='reached')}/{len(project.milestones)}"]
        }
        pd.DataFrame(summary).to_excel(writer, sheet_name="Executive Summary", index=False)
        # Master data
        md = asdict(project.master_data)
        pd.DataFrame([md]).to_excel(writer, sheet_name="Master Data", index=False)
        # budget transactions
        if project.budget_entries:
            df = pd.DataFrame([asdict(t) for t in project.budget_entries])
            df.to_excel(writer, sheet_name="Budget Transactions", index=False)
        # phases/results
        rows = []
        for key, phase in project.phases.items():
            for r in phase.results.values():
                rows.append({
                    "Phase": phase.name,
                    "Result": r.name,
                    "Status": r.status,
                    "Approval Required": r.approval_required,
                    "Approval Date": r.approval_date,
                    "Responsible Role": r.responsible_role
                })
        pd.DataFrame(rows).to_excel(writer, sheet_name="Results", index=False)
        # docs
        docs = [asdict(d) for d in project.documents.values()]
        pd.DataFrame(docs).to_excel(writer, sheet_name="Documents", index=False)
        # milestones
        mss = [asdict(m) for m in project.milestones]
        pd.DataFrame(mss).to_excel(writer, sheet_name="Milestones", index=False)
    buffer.seek(0)
    return buffer.getvalue()

# =========================================
# UI: DASHBOARD, INITIALIZATION, RESULTS, DOCUMENTS, MILESTONES, BUDGET, ITERATIONS
# =========================================
def hermes_header():
    st.image("https://via.placeholder.com/200x60/0055A4/ffffff?text=HERMES", width=200)
    st.title("HERMES 2022 — Project Management Assistant")
    st.caption("Enhanced tool demonstrating HERMES concepts: tailoring, governance, checklists, roles, and reporting")

def project_dashboard():
    show_instructions("Project Dashboard", """
    The Dashboard gives you a high-level view:
    - Budget & timeline summary
    - Phase progress and current phase
    - Upcoming milestones and risks
    Tip: Use the export buttons below to create stakeholder reports.
    """)
    project = st.session_state.hermes_project
    if not project.master_data.project_name:
        st.info("Please initialize your project in 'Project Initialization'.")
        return
    # metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Project", project.master_data.project_name)
    with col2:
        st.metric("Approach", project.master_data.approach.title())
    with col3:
        st.metric("Project Size", project.master_data.project_size.title())
    with col4:
        st.metric("Current Phase", project.master_data.current_phase.title())
    # budget overview
    budget_usage = calculate_budget_usage(project)
    st.subheader("Budget")
    st.metric("Budget (CHF)", f"{project.master_data.budget:,.2f}")
    st.metric("Budget Usage", f"{budget_usage:.1%}")
    # phases progress
    st.subheader("Phase Progress")
    for k, ph in project.phases.items():
        st.write(f"**{ph.name}** — {ph.status.title()}")
        prog = calculate_phase_progress(ph)
        st.progress(prog / 100)
        st.caption(f"{sum(1 for r in ph.results.values() if r.status in ('completed','approved'))}/{len(ph.results)} results done")
    # next milestones
    st.subheader("Upcoming Milestones")
    upcoming = [m for m in project.milestones if m.status in ("planned","delayed")]
    if upcoming:
        for m in upcoming[:5]:
            st.write(f"- {m.name} ({m.phase}) — {m.status}")
    else:
        st.info("No upcoming milestones defined.")

    # report exports
    st.markdown("---")
    st.subheader("Export Reports")
    col1, col2 = st.columns(2)
    with col1:
        pdf = generate_project_status_report_pdf(project)
        st.download_button("Download PDF Status Report", data=pdf, file_name=f"status_{project.master_data.project_name}.pdf", mime="application/pdf")
    with col2:
        xl = generate_project_status_report_excel(project)
        st.download_button("Download Excel Status Report", data=xl, file_name=f"status_{project.master_data.project_name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def enhanced_project_initialization():
    show_instructions("Project Initialization", """
    Initialize project: provide master data, choose approach (classical or agile) and project size.
    Tailoring will be applied automatically after initialization.
    """)
    project = st.session_state.hermes_project
    with st.form("init_form"):
        col1, col2 = st.columns(2)
        with col1:
            project.master_data.project_name = st.text_input("Project Name*", project.master_data.project_name)
            project.master_data.client = st.text_input("Client*", project.master_data.client)
            project.master_data.project_manager = st.text_input("Project Manager*", project.master_data.project_manager)
            project.master_data.user_representative = st.text_input("User Representative*", project.master_data.user_representative)
        with col2:
            start_val = datetime.now() if not project.master_data.start_date else datetime.strptime(project.master_data.start_date, "%Y-%m-%d")
            project.master_data.start_date = st.date_input("Start Date*", start_val).strftime("%Y-%m-%d")
            project.master_data.budget = st.number_input("Budget (CHF)*", min_value=0.0, value=project.master_data.budget or 100000.0, step=1000.0)
            approach = st.selectbox("Approach*", ["classical","agile"], index=0 if project.master_data.approach=="classical" else 1)
            project.master_data.approach = approach
            size = st.selectbox("Project Size*", ["small","medium","large"], index=["small","medium","large"].index(project.master_data.project_size))
            project.master_data.project_size = size
        submitted = st.form_submit_button("Initialize Project")
        if submitted:
            missing = validate_minimal_roles(project)
            if missing:
                st.error(f"Missing mandatory roles: {', '.join(missing)}")
            elif not project.master_data.project_name:
                st.error("Project name is required.")
            else:
                initialize_standard_phases(project)
                init_project_structure(project)
                apply_project_size_tailoring(project)
                # create mandatory milestones from size config
                config = PROJECT_SIZE_CONFIGS.get(project.master_data.project_size)
                project.milestones = []
                for i, ms_name in enumerate(config.mandatory_milestones):
                    phase = "initialization" if "Initialization" in ms_name else project.master_data.current_phase
                    project.milestones.append(HermesMilestone(name=ms_name, phase=phase, mandatory=True))
                st.success("Project initialized and tailoring applied.")
                st.experimental_rerun()

def results_management():
    show_instructions("Results Management", """
    Manage phase results: update statuses, request approvals (if required), and assign responsible roles.
    Approved results are required for phase completion.
    """)
    project = st.session_state.hermes_project
    for key, phase in project.phases.items():
        with st.expander(f"{phase.name} — {phase.status}", expanded=False):
            # add ability to add a result from templates
            st.write("Add result from templates:")
            tmpl = st.selectbox(f"Choose template to add ({phase.name})", [""] + list(RESULT_TEMPLATES.keys()), key=f"tmpl_{key}")
            if tmpl:
                if st.button(f"Add '{tmpl}' to {phase.name}", key=f"addres_{key}_{tmpl}"):
                    t = RESULT_TEMPLATES[tmpl]
                    phase.results[tmpl] = PhaseResult(name=tmpl, description=t.get("description",""), approval_required=t.get("approval_required", False), responsible_role=t.get("role",""))
                    st.success(f"Result '{tmpl}' added to phase {phase.name}")
            # show results
            for rname, r in phase.results.items():
                col1, col2, col3 = st.columns([3,2,2])
                with col1:
                    st.write(f"**{rname}**")
                    st.caption(r.description)
                    st.write(f"Responsible role: {r.responsible_role or '—'}")
                with col2:
                    new_status = st.selectbox("Status", ["not_started","in_progress","completed","approved"], index=["not_started","in_progress","completed","approved"].index(r.status), key=f"resstat_{key}_{rname}")
                    if new_status != r.status:
                        r.status = new_status
                        if new_status == "approved":
                            r.approval_date = datetime.now().strftime("%Y-%m-%d")
                with col3:
                    if r.approval_required:
                        st.write("Approval required")
                    else:
                        st.write("No approval required")

def enhanced_documents_center():
    show_instructions("Document Center", """
    Manage project documents: assign responsibles, update statuses and link documents to results.
    When a linked document is completed, the linked result is automatically updated to 'completed'.
    """)
    project = st.session_state.hermes_project
    if not project.documents:
        st.info("No documents available. Initialize project first.")
        return
    # stats
    status_counts = {}
    for d in project.documents.values():
        status_counts[d.status] = status_counts.get(d.status,0)+1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Docs", len(project.documents))
    with col2:
        st.metric("Completed", status_counts.get("completed",0))
    with col3:
        st.metric("In Progress", status_counts.get("in_progress",0))
    # list and edit
    for dname, doc in project.documents.items():
        with st.expander(f"{dname} — {doc.status}", expanded=False):
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"Responsible: {doc.responsible}")
                if doc.linked_result:
                    st.write(f"Linked result: {doc.linked_result}")
                doc.content = st.text_area("Content / Notes", value=doc.content, key=f"doccont_{dname}")
            with col2:
                new_status = st.selectbox("Status", ["not_started","in_progress","completed"], index=["not_started","in_progress","completed"].index(doc.status), key=f"docstat_{dname}")
                doc.responsible = st.selectbox("Responsible", list(project.roles.values()), index=list(project.roles.values()).index(doc.responsible) if doc.responsible in project.roles.values() else 0, key=f"docresp_{dname}")
                if new_status != doc.status:
                    doc.status = new_status
                    if doc.status == "completed" and doc.linked_result:
                        sync_document_to_result(doc, project)
                        st.success(f"Document completed and linked result '{doc.linked_result}' updated.")
            # quick download placeholder
            if st.button("Export Document (txt)", key=f"export_{dname}"):
                st.download_button(label=f"Download {dname}.txt", data=doc.content or f"{dname}\n\n(no content)", file_name=f"{dname.replace(' ', '_')}.txt", mime="text/plain")

def enhanced_milestone_timeline():
    show_instructions("Milestone Management", """
    Visualize and manage milestones. Milestones can only be 'reached' when all governance checks for the associated phase pass.
    Use "Reach" to mark the milestone reached (requires checks to pass).
    """)
    project = st.session_state.hermes_project
    if not project.milestones:
        st.info("No milestones configured. They are created during initialization (tailoring).")
        return
    # prepare timeline
    fig = go.Figure()
    for i, ms in enumerate(project.milestones):
        x = datetime.now() if not ms.date else datetime.strptime(ms.date, "%Y-%m-%d")
        color = "green" if ms.status=="reached" else "orange" if validate_milestone_completion(ms, project)["can_reach"] else "blue"
        fig.add_trace(go.Scatter(x=[x], y=[i], mode='markers+text', text=[ms.name], textposition="middle right", marker=dict(size=15, color=color)))
    fig.update_layout(title="Milestones", xaxis_title="Date", yaxis=dict(showticklabels=False), height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    # details
    for ms in project.milestones:
        with st.expander(f"{ms.name} ({ms.phase}) — {ms.status}", expanded=False):
            val = validate_milestone_completion(ms, project)
            st.write("Completion checks:")
            st.write(f"- Phase results complete: {'✅' if val['phase_results_complete'] else '❌'}")
            st.write(f"- Required documents complete: {'✅' if val['required_documents_complete'] else '❌'}")
            st.write(f"- Checklists complete: {'✅' if val['checklists_complete'] else '❌'}")
            if ms.status != "reached":
                if val["can_reach"]:
                    if st.button(f"Reach milestone: {ms.name}", key=f"reach_{ms.name}"):
                        ms.status = "reached"
                        ms.date = datetime.now().strftime("%Y-%m-%d")
                        st.success(f"Milestone '{ms.name}' reached.")
                        st.experimental_rerun()
                else:
                    st.info("Milestone cannot be reached yet — complete requirements first.")

def enhanced_budget_management():
    show_instructions("Budget Management", """
    Add transactions (planned or actual). Actual transactions reduce remaining budget and affect release approvals.
    Use the charts and export functions to analyze spend.
    """)
    project = st.session_state.hermes_project
    if not project.master_data.project_name:
        st.info("Please initialize the project first.")
        return
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Budget (CHF)", f"{project.master_data.budget:,.2f}")
        actual = sum(t.amount for t in project.budget_entries if t.type=="actual")
        st.metric("Actual Costs", f"{actual:,.2f}")
        st.metric("Remaining", f"{project.master_data.budget-actual:,.2f}")
        # traffic light
        usage = calculate_budget_usage(project)
        if usage < 0.7:
            st.success(f"Usage: {usage:.1%}")
        elif usage < 0.9:
            st.warning(f"Usage: {usage:.1%}")
        else:
            st.error(f"Usage: {usage:.1%}")
    with col2:
        with st.form("tx_form"):
            tx_date = st.date_input("Date", datetime.now()).strftime("%Y-%m-%d")
            category = st.selectbox("Category", ["Personnel","Hardware","Software","External Services","Training","Travel","Other"])
            amount = st.number_input("Amount (CHF)", min_value=0.0, step=100.0)
            desc = st.text_input("Description")
            tx_type = st.selectbox("Type", ["actual","planned"])
            if st.form_submit_button("Add Transaction"):
                project.budget_entries.append(BudgetTransaction(date=tx_date, category=category, amount=amount, description=desc, type=tx_type))
                st.success("Transaction added.")
                st.experimental_rerun()
    # show table and charts
    if project.budget_entries:
        df = pd.DataFrame([asdict(t) for t in project.budget_entries])
        st.dataframe(df, use_container_width=True)
        # pie by category (actual only)
        actual_df = df[df["type"]=="actual"]
        if not actual_df.empty:
            cat = actual_df.groupby("category")["amount"].sum()
            fig = px.pie(values=cat.values, names=cat.index, title="Spending by Category")
            st.plotly_chart(fig, use_container_width=True)
        # export
        if st.button("Export Budget (Excel)"):
            out = BytesIO()
            with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Transactions")
                summary = pd.DataFrame([{"Metric":"Budget","Value":project.master_data.budget},{"Metric":"Actual","Value":sum(actual_df['amount'])}])
                summary.to_excel(writer, index=False, sheet_name="Summary")
            out.seek(0)
            st.download_button("Download Budget Excel", data=out.getvalue(), file_name=f"budget_{project.master_data.project_name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def enhanced_iteration_management():
    show_instructions("Iterations & Releases", """
    Create iterations (sprints) for agile projects. For release candidates the governance checks are performed before approval.
    Approving a release will create a milestone and mark the release result as approved.
    """)
    project = st.session_state.hermes_project
    if project.master_data.approach != "agile":
        st.info("Switch project approach to 'agile' in Project Initialization to manage iterations.")
        return
    with st.expander("Add New Iteration"):
        with st.form("iter_form"):
            num = st.number_input("Iteration Number", min_value=1, value=1)
            name = st.text_input("Iteration Name", f"Sprint {num}")
            start = st.date_input("Start Date", datetime.now())
            end = st.date_input("End Date", datetime.now() + timedelta(days=14))
            total = st.number_input("Total User Stories", min_value=0, value=10)
            release_candidate = st.checkbox("Release Candidate")
            goals = st.text_area("Goals (one per line)").split("\n")
            if st.form_submit_button("Create Iteration"):
                it = Iteration(number=int(num), name=name, start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"), total_user_stories=int(total), release_candidate=release_candidate, goals=[g.strip() for g in goals if g.strip()])
                project.iterations.append(it)
                # ensure release result exists in implementation phase
                release_res_name = f"Release {it.number}"
                impl_phase_key = "implementation" if "implementation" in project.phases else "realization"
                if impl_phase_key in project.phases and release_res_name not in project.phases[impl_phase_key].results:
                    project.phases[impl_phase_key].results[release_res_name] = PhaseResult(name=release_res_name, description=f"Release result for {it.name}", approval_required=True, responsible_role="project_manager")
                # create release doc placeholder
                docname = f"Release Report {it.number}"
                if docname not in project.documents:
                    project.documents[docname] = HermesDocument(name=docname, responsible="Project Manager", status="not_started", linked_result=release_res_name, required=True)
                st.success("Iteration created.")
                st.experimental_rerun()
    # list iterations
    for it in sorted(project.iterations, key=lambda x: x.number):
        with st.expander(f"Iteration {it.number}: {it.name} ({it.status})"):
            st.write(f"Period: {it.start_date} — {it.end_date}")
            st.write(f"Progress: {it.progress():.1f}%")
            comp = st.number_input("Completed Stories", min_value=0, max_value=it.total_user_stories, value=it.completed_user_stories, key=f"comp_{it.number}")
            it.completed_user_stories = comp
            it.status = st.selectbox("Status", ["planned","active","completed"], index=["planned","active","completed"].index(it.status), key=f"stat_{it.number}")
            if it.release_candidate:
                st.info("This iteration is a release candidate.")
                # perform validation for approval
                val = validate_release_approval(it, project)
                st.write("Release checks:")
                st.write(f"- Release document complete: {'✅' if val['release_document_complete'] else '❌'}")
                st.write(f"- Release result approved: {'✅' if val['release_result_approved'] else '❌'}")
                st.write(f"- Budget healthy: {'✅' if val['budget_healthy'] else '❌'}")
                st.write(f"- Milestones on track: {'✅' if val['milestones_on_track'] else '❌'}")
                if not it.release_approved and val["can_approve"]:
                    if st.button(f"Approve Release {it.number}", key=f"approve_{it.number}"):
                        it.release_approved = True
                        it.status = "completed"
                        # mark release result approved
                        release_result_name = f"Release {it.number}"
                        impl_key = "implementation" if "implementation" in project.phases else "realization"
                        if impl_key in project.phases and release_result_name in project.phases[impl_key].results:
                            project.phases[impl_key].results[release_result_name].status = "approved"
                            project.phases[impl_key].results[release_result_name].approval_date = datetime.now().strftime("%Y-%m-%d")
                        # create milestone
                        project.milestones.append(HermesMilestone(name=f"Release {it.number} - {it.name}", phase=impl_key, date=datetime.now().strftime("%Y-%m-%d"), status="reached", mandatory=False))
                        st.success("Release approved.")
                elif it.release_approved:
                    st.success("Release already approved.")

# comprehensive release approval validation used above
def validate_release_approval(iteration: Iteration, project: HermesProject) -> Dict[str, bool]:
    res = {"release_document_complete": True, "release_result_approved": True, "budget_healthy": True, "milestones_on_track": True, "can_approve": True}
    # release doc
    docname = f"Release Report {iteration.number}"
    doc = project.documents.get(docname)
    if not doc or doc.status != "completed":
        res["release_document_complete"] = False
    # release result
    release_name = f"Release {iteration.number}"
    impl_key = "implementation" if "implementation" in project.phases else "realization"
    if impl_key in project.phases and release_name in project.phases[impl_key].results:
        r = project.phases[impl_key].results[release_name]
        if r.status != "completed":
            res["release_result_approved"] = False
    else:
        res["release_result_approved"] = False
    # budget health
    usage = calculate_budget_usage(project)
    if usage > 0.9:
        res["budget_healthy"] = False
    # critical milestones in implementation
    for ms in project.milestones:
        if ms.mandatory and ms.phase == impl_key and ms.status != "reached":
            res["milestones_on_track"] = False
    res["can_approve"] = all(res.values())
    return res

def phase_governance():
    show_instructions("Phase Governance", """
    Governance area for each phase: complete checklists, ensure docs & results are ready, then complete phases and move forward.
    """)
    project = st.session_state.hermes_project
    for key, phase in project.phases.items():
        with st.expander(f"{phase.name} — {phase.status}"):
            st.write("Checklist:")
            # display checklist items and allow toggling
            if phase.checklist_results:
                for item, val in list(phase.checklist_results.items()):
                    new = st.checkbox(item, value=val, key=f"chk_{key}_{item}")
                    if new != val:
                        phase.checklist_results[item] = new
            else:
                st.write("No checklist items configured for this phase.")
            st.write("Required documents:")
            for docname in phase.required_documents:
                doc = project.documents.get(docname)
                status = doc.status if doc else "not defined"
                st.write(f"- {docname}: {status}")
            # show results summary
            st.write("Results:")
            for r in phase.results.values():
                st.write(f"- {r.name}: {r.status} {'(approval required)' if r.approval_required else ''}")
            # complete phase action
            val = validate_phase_completion(phase)
            st.write(f"Can complete? {'✅' if val['can_complete'] else '❌'}")
            if val["can_complete"] and st.button(f"Complete Phase {phase.name}", key=f"complete_{key}"):
                phase.status = "completed"
                phase.end_date = datetime.now().strftime("%Y-%m-%d")
                # auto-advance
                auto_advance_phase(project)
                st.experimental_rerun()

def show_hermes_info():
    st.header("ℹ️ About this HERMES Assistant")
    st.write("""
    This app is a demo assistant implementing many HERMES concepts:
    - Tailoring per project size (small / medium / large)
    - Phase-based governance with checklists and milestone gating
    - Document <-> result synchronization
    - Agile iterations / release governance
    - Roles and responsibilities
    - Reporting (PDF / Excel)
    """)
    st.write("Use the left menu to navigate the features. Each page has an instructions panel to guide you.")

# =========================================
# MAIN NAVIGATION
# =========================================
def main():
    st.set_page_config(page_title="HERMES 2022 Assistant", layout="wide")
    init_session_state()
    hermes_header()
    menu = st.sidebar.radio("Navigation", ["Dashboard", "Project Initialization", "Results Management", "Documents", "Milestones", "Phase Governance", "Iterations & Releases", "Budget Management", "Information"])
    if menu == "Dashboard":
        project_dashboard()
    elif menu == "Project Initialization":
        enhanced_project_initialization()
    elif menu == "Results Management":
        results_management()
    elif menu == "Documents":
        enhanced_documents_center()
    elif menu == "Milestones":
        enhanced_milestone_timeline()
    elif menu == "Phase Governance":
        phase_governance()
    elif menu == "Iterations & Releases":
        enhanced_iteration_management()
    elif menu == "Budget Management":
        enhanced_budget_management()
    elif menu == "Information":
        show_hermes_info()

if __name__ == "__main__":
    main()
