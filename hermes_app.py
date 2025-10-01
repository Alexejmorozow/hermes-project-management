# hermes_app.py - KORRIGIERTE VERSION OHNE xlsxwriter ABHÄNGIGKEIT
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
# INTERNATIONALISIERUNG - VEREINFACHTE VERSION
# =========================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "de": "Deutsch"
}

TRANSLATIONS = {
    "en": {
        # Navigation
        "dashboard": "Dashboard",
        "project_initialization": "Project Initialization", 
        "results_management": "Results Management",
        "documents": "Documents",
        "milestones": "Milestones",
        "phase_governance": "Phase Governance",
        "iterations_releases": "Iterations & Releases",
        "budget_management": "Budget Management",
        "information": "Information",
        
        # Common UI
        "save": "Save",
        "add": "Add",
        "export": "Export",
        "status": "Status",
        "progress": "Progress",
        "required": "Required",
        "optional": "Optional",
        "name": "Name",
        "description": "Description",
        "date": "Date",
        "amount": "Amount",
        "category": "Category",
        "responsible": "Responsible",
        
        # Status Values
        "not_started": "Not Started",
        "in_progress": "In Progress",
        "completed": "Completed", 
        "approved": "Approved",
        "planned": "Planned",
        "reached": "Reached",
        
        # Project Data
        "project_name": "Project Name",
        "client": "Client",
        "project_manager": "Project Manager",
        "user_representative": "User Representative", 
        "start_date": "Start Date",
        "budget": "Budget",
        "approach": "Approach",
        "project_size": "Project Size",
        "current_phase": "Current Phase",
        
        # Approaches
        "classical": "Classical",
        "agile": "Agile",
        
        # Sizes
        "small": "Small",
        "medium": "Medium",
        "large": "Large",
        
        # Instructions
        "instructions": "Instructions",
        "dashboard_instructions": "The Dashboard provides a high-level overview of your project with budget tracking, progress indicators, and milestone tracking.",
        
        # Success Messages
        "project_initialized": "Project successfully initialized",
        "changes_saved": "Changes saved successfully",
        
        # Budget & Financial
        "planned_budget": "Planned Budget",
        "actual_costs": "Actual Costs", 
        "remaining_budget": "Remaining Budget",
        "budget_usage": "Budget Usage",
        
        # Common
        "please_initialize_project": "Please initialize your project first",
    },
    "de": {
        # Navigation
        "dashboard": "Dashboard",
        "project_initialization": "Projektinitialisierung",
        "results_management": "Ergebnisverwaltung",
        "documents": "Dokumente",
        "milestones": "Meilensteine", 
        "phase_governance": "Phasen-Governance",
        "iterations_releases": "Iterationen & Releases",
        "budget_management": "Budgetverwaltung",
        "information": "Informationen",
        
        # Common UI
        "save": "Speichern",
        "add": "Hinzufügen",
        "export": "Exportieren",
        "status": "Status",
        "progress": "Fortschritt",
        "required": "Erforderlich",
        "optional": "Optional",
        "name": "Name",
        "description": "Beschreibung",
        "date": "Datum",
        "amount": "Betrag",
        "category": "Kategorie",
        "responsible": "Verantwortlich",
        
        # Status Values
        "not_started": "Nicht begonnen",
        "in_progress": "In Bearbeitung",
        "completed": "Abgeschlossen",
        "approved": "Genehmigt",
        "planned": "Geplant",
        "reached": "Erreicht",
        
        # Project Data
        "project_name": "Projektname",
        "client": "Auftraggeber",
        "project_manager": "Projektleiter",
        "user_representative": "Anwendervertreter",
        "start_date": "Startdatum",
        "budget": "Budget",
        "approach": "Vorgehen",
        "project_size": "Projektgröße",
        "current_phase": "Aktuelle Phase",
        
        # Approaches
        "classical": "Klassisch",
        "agile": "Agil",
        
        # Sizes
        "small": "Klein",
        "medium": "Mittel",
        "large": "Groß",
        
        # Instructions
        "instructions": "Anleitungen",
        "dashboard_instructions": "Das Dashboard bietet einen Überblick über Ihr Projekt mit Budgetverfolgung, Fortschrittsanzeigen und Meilenstein-Tracking.",
        
        # Success Messages
        "project_initialized": "Projekt erfolgreich initialisiert",
        "changes_saved": "Änderungen erfolgreich gespeichert",
        
        # Budget & Financial
        "planned_budget": "Geplantes Budget",
        "actual_costs": "Ist-Kosten",
        "remaining_budget": "Verbleibendes Budget",
        "budget_usage": "Budgetauslastung",
        
        # Common
        "please_initialize_project": "Bitte initialisieren Sie zuerst Ihr Projekt",
    }
}

def t(key: str, language: str = "en") -> str:
    """Translation helper function"""
    return TRANSLATIONS.get(language, {}).get(key, key)

# =========================================
# DATACLASSES
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
    language: str = "en"

@dataclass
class PhaseResult:
    name: str
    description: str = ""
    status: str = "not_started"
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
    status: str = "not_started"
    required: bool = True
    linked_result: str = ""
    content: str = ""

@dataclass
class HermesMilestone:
    name: str
    phase: str
    date: str = ""
    status: str = "planned"
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
    type: str = "actual"

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
    roles: Dict[str, str] = field(default_factory=dict)

# =========================================
# KONFIGURATIONEN
# =========================================

HERMES_PHASE_LABELS = {
    "en": {
        "classical": {
            "initialization": "Initialization",
            "concept": "Concept",
            "realization": "Realization", 
            "introduction": "Introduction",
            "completion": "Completion"
        },
        "agile": {
            "initialization": "Initialization",
            "implementation": "Implementation",
            "completion": "Completion"
        }
    },
    "de": {
        "classical": {
            "initialization": "Initialisierung",
            "concept": "Konzept",
            "realization": "Realisierung",
            "introduction": "Einführung",
            "completion": "Abschluss"
        },
        "agile": {
            "initialization": "Initialisierung",
            "implementation": "Umsetzung",
            "completion": "Abschluss"
        }
    }
}

RESULT_TEMPLATES = {
    "en": {
        "Project Charter": {
            "description": "Formal project initiation document",
            "approval_required": True,
            "role": "project_manager"
        },
        "Stakeholder Analysis": {
            "description": "Identification and analysis of stakeholders", 
            "approval_required": False,
            "role": "project_manager"
        }
    },
    "de": {
        "Project Charter": {
            "description": "Formelles Projektinitialisierungsdokument",
            "approval_required": True,
            "role": "project_manager"
        },
        "Stakeholder Analysis": {
            "description": "Identifikation und Analyse der Stakeholder",
            "approval_required": False,
            "role": "project_manager"
        }
    }
}

DEFAULT_HERMES_ROLES = {
    "en": {
        "client": "Client",
        "project_manager": "Project Manager",
        "user_representative": "User Representative"
    },
    "de": {
        "client": "Auftraggeber",
        "project_manager": "Projektleiter",
        "user_representative": "Anwendervertreter"
    }
}

@dataclass
class ProjectSizeConfig:
    required_documents: List[str] = field(default_factory=list)
    optional_documents: List[str] = field(default_factory=list)
    simplified_checklists: bool = False
    mandatory_milestones: List[str] = field(default_factory=list)
    extra_roles: List[str] = field(default_factory=list)

PROJECT_SIZE_CONFIGS = {
    "small": ProjectSizeConfig(
        required_documents=["Project Charter"],
        optional_documents=[],
        simplified_checklists=True,
        mandatory_milestones=["Project Initialization", "Project Completion"],
        extra_roles=[]
    ),
    "medium": ProjectSizeConfig(
        required_documents=["Project Charter", "Stakeholder Analysis"],
        optional_documents=[],
        simplified_checklists=False,
        mandatory_milestones=["Project Initialization", "Project Completion"],
        extra_roles=[]
    ),
    "large": ProjectSizeConfig(
        required_documents=["Project Charter", "Stakeholder Analysis"],
        optional_documents=[],
        simplified_checklists=False,
        mandatory_milestones=["Project Initialization", "Project Completion"],
        extra_roles=[]
    )
}

# =========================================
# HELPER FUNCTIONS
# =========================================

def get_phase_labels(project: HermesProject):
    lang = project.master_data.language
    approach = project.master_data.approach
    return HERMES_PHASE_LABELS.get(lang, HERMES_PHASE_LABELS["en"]).get(approach, {})

def get_result_templates(project: HermesProject):
    lang = project.master_data.language
    return RESULT_TEMPLATES.get(lang, RESULT_TEMPLATES["en"])

def get_default_roles(project: HermesProject):
    lang = project.master_data.language
    return DEFAULT_HERMES_ROLES.get(lang, DEFAULT_HERMES_ROLES["en"])

def init_session_state():
    if "hermes_project" not in st.session_state:
        p = HermesProject()
        p.master_data.current_phase = "initialization"
        p.master_data.language = "en"
        st.session_state.hermes_project = p
    
    proj = st.session_state.hermes_project
    if not proj.phases:
        initialize_standard_phases(proj)
    if not proj.documents:
        init_project_structure(proj)
    if not proj.roles:
        proj.roles = get_default_roles(proj).copy()

def initialize_standard_phases(project: HermesProject):
    labels = get_phase_labels(project)
    project.phases.clear()
    for key, lbl in labels.items():
        project.phases[key] = ProjectPhase(name=lbl)

def init_project_structure(project: HermesProject):
    templates = get_result_templates(project)
    roles = get_default_roles(project)
    lang = project.master_data.language
    
    docs = {}
    for doc_name, doc_config in templates.items():
        docs[doc_name] = HermesDocument(
            name=doc_name,
            responsible=roles.get(doc_config.get("role", "project_manager"), "Project Manager"),
            required=True,
            linked_result=doc_name
        )
    project.documents.update(docs)
    
    for phase_key, phase in project.phases.items():
        if phase_key == "initialization":
            template_names = ["Project Charter", "Stakeholder Analysis"]
        else:
            template_names = []
        
        for name in template_names:
            if name in templates:
                tmpl = templates[name]
                phase.results[name] = PhaseResult(
                    name=name,
                    description=tmpl["description"],
                    status="not_started",
                    approval_required=tmpl.get("approval_required", False),
                    responsible_role=tmpl.get("role", "")
                )

def apply_project_size_tailoring(project: HermesProject):
    config = PROJECT_SIZE_CONFIGS.get(project.master_data.project_size, PROJECT_SIZE_CONFIGS["medium"])
    lang = project.master_data.language
    
    for name, doc in project.documents.items():
        if name in config.required_documents:
            doc.required = True
        elif name in config.optional_documents:
            doc.required = False
    
    roles = get_default_roles(project)
    for r in config.extra_roles:
        if r not in project.roles:
            project.roles[r] = roles.get(r, r.replace("_", " ").title())
    
    project.tailoring = {
        "applied_size": project.master_data.project_size,
        "config": config,
        "language": lang
    }

def validate_minimal_roles(project: HermesProject) -> List[str]:
    missing = []
    if not project.master_data.project_manager:
        missing.append("project_manager")
    if not project.master_data.user_representative:
        missing.append("user_representative") 
    if not project.master_data.client:
        missing.append("client")
    return missing

def calculate_total_progress(project: HermesProject) -> float:
    if not project.phases:
        return 0.0
    vals = [calculate_phase_progress(p) for p in project.phases.values()]
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

def sync_document_to_result(document: HermesDocument, project: HermesProject):
    if document.linked_result and document.status == "completed":
        for phase in project.phases.values():
            if document.linked_result in phase.results:
                res = phase.results[document.linked_result]
                if res.status not in ("completed", "approved"):
                    res.status = "completed"

# =========================================
# REPORT GENERATION (OHNE xlsxwriter)
# =========================================

def generate_project_status_report_pdf(project: HermesProject) -> bytes:
    lang = project.master_data.language
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph(f"HERMES Project Status Report - {project.master_data.project_name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    total_progress = calculate_total_progress(project)
    budget_usage = calculate_budget_usage(project)
    
    summary_text = f"Project Progress: {total_progress:.1f}% | Budget Usage: {budget_usage:.1%}"
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    master_table = [
        ["Project Name", project.master_data.project_name],
        ["Client", project.master_data.client],
        ["Project Manager", project.master_data.project_manager],
        ["Approach", project.master_data.approach],
        ["Project Size", project.master_data.project_size],
        ["Budget (CHF)", f"{project.master_data.budget:,.2f}"]
    ]
    
    master_tbl = Table(master_table, colWidths=[180, 300])
    master_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black)
    ]))
    story.append(master_tbl)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_project_status_report_excel(project: HermesProject) -> bytes:
    """Generate Excel report using simple CSV approach"""
    lang = project.master_data.language
    
    # Create a simple CSV-style data structure
    data = {
        "Project Information": [
            ["Field", "Value"],
            ["Project Name", project.master_data.project_name],
            ["Client", project.master_data.client],
            ["Project Manager", project.master_data.project_manager],
            ["Approach", project.master_data.approach],
            ["Project Size", project.master_data.project_size],
            ["Budget", f"CHF {project.master_data.budget:,.2f}"],
            ["Progress", f"{calculate_total_progress(project):.1f}%"],
            ["Budget Usage", f"{calculate_budget_usage(project):.1%}"]
        ],
        "Phases": [
            ["Phase", "Status", "Progress"]
        ] + [
            [phase.name, phase.status, f"{calculate_phase_progress(phase):.1f}%"]
            for phase in project.phases.values()
        ]
    }
    
    # Convert to JSON for simple export (alternative to Excel)
    report_data = {
        "project": asdict(project.master_data),
        "progress": {
            "total": calculate_total_progress(project),
            "budget_usage": calculate_budget_usage(project)
        },
        "phases": [
            {
                "name": phase.name,
                "status": phase.status,
                "progress": calculate_phase_progress(phase)
            }
            for phase in project.phases.values()
        ]
    }
    
    return json.dumps(report_data, indent=2).encode()

# =========================================
# UI COMPONENTS
# =========================================

def show_instructions(title_key: str, text_key: str, expanded: bool = True):
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    title = t(title_key, lang)
    text = t(text_key, lang)
    
    with st.expander(f"ℹ️ {title} — {t('instructions', lang)}", expanded=expanded):
        st.markdown(text)

def hermes_header():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.image("https://via.placeholder.com/200x60/0055A4/ffffff?text=HERMES", width=200)
    
    with col2:
        st.title("HERMES 2022 — Project Management")
        st.caption("Multilingual project management tool")
    
    with col3:
        current_lang = project.master_data.language
        new_lang = st.selectbox(
            "🌐 Language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            index=list(SUPPORTED_LANGUAGES.keys()).index(current_lang),
            key="language_selector"
        )
        
        if new_lang != current_lang:
            project.master_data.language = new_lang
            st.rerun()

# =========================================
# IMPLEMENTED VIEWS
# =========================================

def project_dashboard():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("dashboard", "dashboard_instructions")
    
    if not project.master_data.project_name:
        st.info(t('please_initialize_project', lang))
        return
    
    # Project overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Project", project.master_data.project_name)
    with col2:
        st.metric("Approach", t(project.master_data.approach, lang))
    with col3:
        st.metric("Project Size", t(project.master_data.project_size, lang))
    with col4:
        st.metric("Current Phase", project.phases[project.master_data.current_phase].name)
    
    # Budget overview
    st.subheader(t('budget', lang))
    budget_usage = calculate_budget_usage(project)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t('planned_budget', lang), f"CHF {project.master_data.budget:,.2f}")
    with col2:
        actual_costs = sum(t.amount for t in project.budget_entries if t.type == "actual")
        st.metric(t('actual_costs', lang), f"CHF {actual_costs:,.2f}")
    with col3:
        st.metric(t('budget_usage', lang), f"{budget_usage:.1%}")
    
    # Progress
    st.subheader(t('progress', lang))
    for key, phase in project.phases.items():
        st.write(f"**{phase.name}** — {t(phase.status, lang)}")
        prog = calculate_phase_progress(phase)
        st.progress(prog / 100)
        completed_results = sum(1 for r in phase.results.values() if r.status in ('completed','approved'))
        st.caption(f"{completed_results}/{len(phase.results)} results completed")
    
    # Simple export (without Excel dependency)
    st.markdown("---")
    st.subheader("Export Reports")
    
    pdf_report = generate_project_status_report_pdf(project)
    st.download_button(
        "Download PDF Report",
        data=pdf_report,
        file_name=f"project_status_{project.master_data.project_name}.pdf",
        mime="application/pdf"
    )
    
    # JSON export instead of Excel
    json_report = generate_project_status_report_excel(project)
    st.download_button(
        "Download JSON Data",
        data=json_report,
        file_name=f"project_data_{project.master_data.project_name}.json",
        mime="application/json"
    )

def enhanced_project_initialization():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("project_initialization", "project_initialization_instructions")
    
    with st.form("init_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project.master_data.project_name = st.text_input(
                f"{t('project_name', lang)}*", 
                project.master_data.project_name
            )
            project.master_data.client = st.text_input(
                f"{t('client', lang)}*", 
                project.master_data.client
            )
            project.master_data.project_manager = st.text_input(
                f"{t('project_manager', lang)}*", 
                project.master_data.project_manager
            )
            project.master_data.user_representative = st.text_input(
                f"{t('user_representative', lang)}*", 
                project.master_data.user_representative
            )
        
        with col2:
            start_val = datetime.now() if not project.master_data.start_date else datetime.strptime(project.master_data.start_date, "%Y-%m-%d")
            project.master_data.start_date = st.date_input(
                f"{t('start_date', lang)}*", 
                start_val
            ).strftime("%Y-%m-%d")
            
            project.master_data.budget = st.number_input(
                f"{t('budget', lang)} (CHF)*", 
                min_value=0.0, 
                value=project.master_data.budget or 100000.0, 
                step=1000.0
            )
            
            approach = st.selectbox(
                f"{t('approach', lang)}*",
                ["classical", "agile"],
                format_func=lambda x: t(x, lang),
                index=0 if project.master_data.approach == "classical" else 1
            )
            project.master_data.approach = approach
            
            size = st.selectbox(
                f"{t('project_size', lang)}*", 
                ["small", "medium", "large"],
                format_func=lambda x: t(x, lang),
                index=["small", "medium", "large"].index(project.master_data.project_size)
            )
            project.master_data.project_size = size
        
        submitted = st.form_submit_button(t("save", lang))
        
        if submitted:
            missing = validate_minimal_roles(project)
            if missing:
                missing_translated = [t(role, lang) for role in missing]
                st.error(f"Missing roles: {', '.join(missing_translated)}")
            elif not project.master_data.project_name:
                st.error("Project name is required")
            else:
                initialize_standard_phases(project)
                init_project_structure(project)
                apply_project_size_tailoring(project)
                
                config = PROJECT_SIZE_CONFIGS.get(project.master_data.project_size)
                project.milestones = []
                for i, ms_name in enumerate(config.mandatory_milestones):
                    phase = "initialization" if "Initialization" in ms_name else project.master_data.current_phase
                    project.milestones.append(HermesMilestone(
                        name=ms_name, 
                        phase=phase, 
                        mandatory=True
                    ))
                
                st.success(t("project_initialized", lang))
                st.rerun()

def results_management():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("results_management", "Results management allows you to track phase results and their approval status.")
    
    for key, phase in project.phases.items():
        with st.expander(f"{phase.name} — {t(phase.status, lang)}", expanded=False):
            templates = get_result_templates(project)
            
            # Show existing results
            for rname, r in phase.results.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{rname}**")
                    st.caption(r.description)
                with col2:
                    status_options = ["not_started", "in_progress", "completed", "approved"]
                    current_index = status_options.index(r.status)
                    new_status = st.selectbox(
                        t("status", lang), 
                        status_options,
                        format_func=lambda x: t(x, lang),
                        index=current_index, 
                        key=f"resstat_{key}_{rname}"
                    )
                    if new_status != r.status:
                        r.status = new_status

def enhanced_documents_center():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("documents", "Manage project documents and their relationships to results.")
    
    if not project.documents:
        st.info(t('please_initialize_project', lang))
        return
    
    for dname, doc in project.documents.items():
        with st.expander(f"{dname} — {t(doc.status, lang)}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{t('responsible', lang)}: {doc.responsible}")
            with col2:
                status_options = ["not_started", "in_progress", "completed"]
                current_index = status_options.index(doc.status)
                new_status = st.selectbox(
                    t("status", lang),
                    status_options,
                    format_func=lambda x: t(x, lang),
                    index=current_index,
                    key=f"docstat_{dname}"
                )
                
                if new_status != doc.status:
                    doc.status = new_status
                    if doc.status == "completed" and doc.linked_result:
                        sync_document_to_result(doc, project)
                        st.success(f"Document completed and linked result updated!")

def enhanced_budget_management():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("budget_management", "Track project finances and expenditures.")
    
    if not project.master_data.project_name:
        st.info(t('please_initialize_project', lang))
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(t("planned_budget", lang), f"CHF {project.master_data.budget:,.2f}")
        actual = sum(t.amount for t in project.budget_entries if t.type == "actual")
        st.metric(t("actual_costs", lang), f"CHF {actual:,.2f}")
        
        usage = calculate_budget_usage(project)
        if usage < 0.7:
            st.success(f"Budget Usage: {usage:.1%}")
        elif usage < 0.9:
            st.warning(f"Budget Usage: {usage:.1%}")
        else:
            st.error(f"Budget Usage: {usage:.1%}")
    
    with col2:
        with st.form("tx_form"):
            tx_date = st.date_input(t("date", lang), datetime.now()).strftime("%Y-%m-%d")
            category = st.selectbox(t("category", lang), ["Personnel", "Hardware", "Software", "Other"])
            amount = st.number_input(f"{t('amount', lang)} (CHF)", min_value=0.0, step=100.0)
            desc = st.text_input(t("description", lang))
            if st.form_submit_button(f"➕ {t('add_transaction', lang)}"):
                project.budget_entries.append(BudgetTransaction(
                    date=tx_date, 
                    category=category, 
                    amount=amount, 
                    description=desc, 
                    type="actual"
                ))
                st.success(f"✅ {t('transaction_added', lang)}!")
                st.rerun()
    
    if project.budget_entries:
        st.subheader("Transaction History")
        df = pd.DataFrame([asdict(t) for t in project.budget_entries])
        st.dataframe(df, use_container_width=True)

# Placeholder functions for other views
def enhanced_milestone_timeline():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    st.info("Milestone timeline - Implementation in progress")

def phase_governance():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    st.info("Phase governance - Implementation in progress")

def enhanced_iteration_management():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    st.info("Iterations & Releases - Implementation in progress")

def show_hermes_info():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    st.info("HERMES Information - Implementation in progress")

# =========================================
# MAIN APPLICATION
# =========================================

def main():
    st.set_page_config(
        page_title="HERMES 2022", 
        layout="wide",
        page_icon="🏛️"
    )
    
    init_session_state()
    hermes_header()
    
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    # Navigation
    menu = st.sidebar.radio(
        "Navigation",
        [
            "dashboard", 
            "project_initialization", 
            "results_management",
            "documents", 
            "milestones", 
            "phase_governance",
            "iterations_releases", 
            "budget_management", 
            "information"
        ],
        format_func=lambda x: t(x, lang)
    )
    
    if menu == "dashboard":
        project_dashboard()
    elif menu == "project_initialization":
        enhanced_project_initialization()
    elif menu == "results_management":
        results_management()
    elif menu == "documents":
        enhanced_documents_center()
    elif menu == "milestones":
        enhanced_milestone_timeline()
    elif menu == "phase_governance":
        phase_governance()
    elif menu == "iterations_releases":
        enhanced_iteration_management()
    elif menu == "budget_management":
        enhanced_budget_management()
    elif menu == "information":
        show_hermes_info()

if __name__ == "__main__":
    main()
