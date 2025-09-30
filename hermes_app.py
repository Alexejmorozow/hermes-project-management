import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# =========================================
# DATENKLASSEN
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

@dataclass
class PhaseResult:
    name: str
    description: str = ""
    status: str = "not_started"
    approval_required: bool = False
    approval_date: str = ""

@dataclass
class ProjectPhase:
    name: str
    results: Dict[str, PhaseResult] = field(default_factory=dict)
    required_documents: List[str] = field(default_factory=list)
    checklist_results: Dict[str, Dict[str, bool]] = field(default_factory=dict)

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

@dataclass
class HermesProject:
    master_data: ProjectMasterData = field(default_factory=ProjectMasterData)
    phases: Dict[str, ProjectPhase] = field(default_factory=dict)
    documents: Dict[str, HermesDocument] = field(default_factory=dict)
    milestones: List[HermesMilestone] = field(default_factory=list)
    iterations: List[Iteration] = field(default_factory=list)
    actual_costs: float = 0.0
    risks: List[Dict] = field(default_factory=list)

# =========================================
# INITIALISIERUNGSFUNKTIONEN
# =========================================

def init_session_state():
    """Initialisiert die Session State Variablen"""
    if 'hermes_project' not in st.session_state:
        st.session_state.hermes_project = HermesProject()
    
    # Standard-Phasen initialisieren
    if not st.session_state.hermes_project.phases:
        initialize_standard_phases()

def initialize_standard_phases():
    """Initialisiert die standard HERMES Phasen"""
    project = st.session_state.hermes_project
    
    phases = {
        "initialization": ProjectPhase("Initialization"),
        "concept": ProjectPhase("Concept"), 
        "implementation": ProjectPhase("Implementation"),
        "introduction": ProjectPhase("Introduction"),
        "completion": ProjectPhase("Completion")
    }
    
    # Standard-Ergebnisse für jede Phase
    phases["initialization"].results = {
        "Project Charter": PhaseResult("Project Charter", approval_required=True),
        "Stakeholder Analysis": PhaseResult("Stakeholder Analysis")
    }
    
    phases["concept"].results = {
        "Requirements Specification": PhaseResult("Requirements Specification", approval_required=True),
        "Solution Concept": PhaseResult("Solution Concept", approval_required=True)
    }
    
    project.phases = phases

def initialize_mandatory_milestones(project: HermesProject):
    """Initialisiert die obligatorischen Meilensteine"""
    mandatory_milestones = [
        HermesMilestone("Project Start", "initialization", mandatory=True),
        HermesMilestone("Concept Approved", "concept", mandatory=True),
        HermesMilestone("Implementation Start", "implementation", mandatory=True),
        HermesMilestone("Ready for Operation", "introduction", mandatory=True),
        HermesMilestone("Project Completed", "completion", mandatory=True)
    ]
    
    project.milestones = mandatory_milestones

def init_project_structure(project: HermesProject):
    """Initialisiert die Projektstruktur basierend auf HERMES"""
    # Standard-Dokumente
    standard_docs = {
        "Project Charter": HermesDocument("Project Charter", "Project Manager", required=True, linked_result="Project Charter"),
        "Stakeholder Analysis": HermesDocument("Stakeholder Analysis", "Project Manager", linked_result="Stakeholder Analysis"),
        "Requirements Specification": HermesDocument("Requirements Specification", "Requirements Engineer", required=True, linked_result="Requirements Specification"),
        "Solution Concept": HermesDocument("Solution Concept", "Solution Architect", required=True, linked_result="Solution Concept")
    }
    
    project.documents.update(standard_docs)

def validate_minimal_roles(project: HermesProject) -> List[str]:
    """Validiert ob alle minimalen Rollen besetzt sind"""
    missing_roles = []
    master = project.master_data
    
    if not master.project_manager:
        missing_roles.append("Project Manager")
    if not master.user_representative:
        missing_roles.append("User Representative")
    
    return missing_roles

# =========================================
# ERWEITERTE FUNKTIONEN FÜR GOVERNANCE
# =========================================

def validate_milestone_completion(milestone: HermesMilestone, project: HermesProject) -> Dict[str, bool]:
    """Validiert ob ein Meilenstein erreicht werden kann"""
    validation = {
        "phase_results_complete": True,
        "required_documents_complete": True,
        "checklists_complete": True,
        "can_reach": True
    }

    # Prüfe Phase-Ergebnisse
    phase = project.phases.get(milestone.phase)
    if phase:
        for result in phase.results.values():
            if result.approval_required and result.status != "approved":
                validation["phase_results_complete"] = False
                break

    # Prüfe Pflichtdokumente der Phase
    if phase:
        for doc_name in phase.required_documents:
            doc = project.documents.get(doc_name)
            if doc and doc.required and doc.status != "completed":
                validation["required_documents_complete"] = False
                break

    # Prüfe Checklisten der Phase
    if phase and phase.checklist_results:
        for checklist_name, checklist_items in phase.checklist_results.items():
            if not all(checklist_items.values()):
                validation["checklists_complete"] = False
                break

    validation["can_reach"] = all([
        validation["phase_results_complete"],
        validation["required_documents_complete"], 
        validation["checklists_complete"]
    ])
    return validation

def sync_document_to_result(document: HermesDocument, project: HermesProject):
    """Synchronisiert Dokument-Status auf verknüpftes Ergebnis"""
    if document.linked_result and document.status == "completed":
        # Finde das verknüpfte Ergebnis in allen Phasen
        for phase in project.phases.values():
            if document.linked_result in phase.results:
                phase.results[document.linked_result].status = "completed"
                break

def generate_comprehensive_release_report(iteration: Iteration, project: HermesProject) -> BytesIO:
    """Generiert einen vollständigen Release-Report als PDF"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"HERMES Release Report - {project.master_data.project_name}")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Release: {iteration.number} - {iteration.name}")
    c.drawString(50, height - 100, f"Report Date: {datetime.now().strftime('%d.%m.%Y')}")

    # Release Information
    c.drawString(50, height - 130, "Release Information:")
    c.drawString(70, height - 150, f"• Period: {iteration.start_date} to {iteration.end_date}")
    c.drawString(70, height - 170, f"• Progress: {iteration.progress():.1f}%")
    c.drawString(70, height - 190, f"• User Stories: {iteration.completed_user_stories}/{iteration.total_user_stories}")
    c.drawString(70, height - 210, f"• Release Candidate: {'Yes' if iteration.release_candidate else 'No'}")
    c.drawString(70, height - 230, f"• Approved: {'Yes' if iteration.release_approved else 'No'}")

    # Project Context
    c.drawString(50, height - 270, "Project Context:")
    c.drawString(70, height - 290, f"• Client: {project.master_data.client}")
    c.drawString(70, height - 310, f"• Project Manager: {project.master_data.project_manager}")
    budget_usage = (project.actual_costs / project.master_data.budget * 100) if project.master_data.budget > 0 else 0
    c.drawString(70, height - 330, f"• Budget Usage: {budget_usage:.1f}%")

    # Approval Section
    c.drawString(50, height - 380, "Approval:")
    c.drawString(70, height - 400, "___________________________________")
    c.drawString(70, height - 420, "Project Manager Signature")

    c.drawString(300, height - 400, "___________________________________")
    c.drawString(300, height - 420, "Client Signature")

    c.save()
    buffer.seek(0)
    return buffer

def generate_excel_release_report(iteration: Iteration, project: HermesProject) -> BytesIO:
    """Generiert einen Excel-Release-Report"""
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Release Summary
        summary_data = {
            'Field': ['Release Number', 'Release Name', 'Start Date', 'End Date', 
                     'Progress', 'Completed Stories', 'Total Stories', 'Release Candidate'],
            'Value': [iteration.number, iteration.name, iteration.start_date, iteration.end_date,
                     f"{iteration.progress():.1f}%", iteration.completed_user_stories,
                     iteration.total_user_stories, 'Yes' if iteration.release_candidate else 'No']
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Release Summary', index=False)

        # Project Context
        context_data = {
            'Field': ['Project Name', 'Client', 'Project Manager', 'Budget', 'Actual Costs'],
            'Value': [project.master_data.project_name, project.master_data.client,
                     project.master_data.project_manager, project.master_data.budget,
                     project.actual_costs]
        }
        pd.DataFrame(context_data).to_excel(writer, sheet_name='Project Context', index=False)

        # Iteration Goals (wenn vorhanden)
        if hasattr(iteration, 'goals') and iteration.goals:
            goals_data = {'Goals': iteration.goals}
            pd.DataFrame(goals_data).to_excel(writer, sheet_name='Iteration Goals', index=False)

    buffer.seek(0)
    return buffer

# =========================================
# DASHBOARD & VISUALISIERUNG
# =========================================

def hermes_header():
    """Zeigt den HERMES Header"""
    st.title("🎯 HERMES 2022 Project Management")
    st.markdown("---")

def project_dashboard():
    """Haupt-Dashboard mit Projektübersicht"""
    st.header("📊 Project Dashboard")
    project = st.session_state.hermes_project
    
    if not project.master_data.project_name:
        st.info("ℹ️ Please initialize your project first in 'Project Initialization'")
        return
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Project", project.master_data.project_name)
    
    with col2:
        st.metric("Approach", project.master_data.approach.title())
    
    with col3:
        completed_milestones = sum(1 for m in project.milestones if m.status == "reached")
        st.metric("Milestones", f"{completed_milestones}/{len(project.milestones)}")
    
    with col4:
        budget_usage = (project.actual_costs / project.master_data.budget * 100) if project.master_data.budget > 0 else 0
        st.metric("Budget Usage", f"{budget_usage:.1f}%")
    
    # Phasen-Fortschritt
    st.subheader("Phase Progress")
    for phase_name, phase in project.phases.items():
        total_results = len(phase.results)
        completed_results = sum(1 for r in phase.results.values() if r.status == "completed")
        progress = (completed_results / total_results * 100) if total_results > 0 else 0
        
        st.write(f"**{phase_name.title()}**: {completed_results}/{total_results} results completed")
        st.progress(progress / 100)
    
    # Aktuelle Meilensteine
    st.subheader("Upcoming Milestones")
    upcoming_milestones = [m for m in project.milestones if m.status in ["planned", "delayed"]]
    
    if upcoming_milestones:
        for milestone in upcoming_milestones[:3]:  # Zeige nur die nächsten 3
            validation = validate_milestone_completion(milestone, project)
            status_icon = "✅" if validation["can_reach"] else "⏳"
            st.write(f"{status_icon} {milestone.name} ({milestone.phase})")
    else:
        st.info("No upcoming milestones")

# =========================================
# RESULTS MANAGEMENT
# =========================================

def results_management():
    """Verwaltung der Phasenergebnisse"""
    st.header("📋 Results Management")
    project = st.session_state.hermes_project
    
    for phase_name, phase in project.phases.items():
        with st.expander(f"{phase_name.title()} Phase", expanded=False):
            for result_name, result in phase.results.items():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{result_name}**")
                    if result.description:
                        st.write(f"*{result.description}*")
                
                with col2:
                    new_status = st.selectbox(
                        "Status",
                        ["not_started", "in_progress", "completed", "approved"],
                        index=["not_started", "in_progress", "completed", "approved"].index(result.status),
                        key=f"result_{phase_name}_{result_name}"
                    )
                    if new_status != result.status:
                        result.status = new_status
                        if new_status == "approved":
                            result.approval_date = datetime.now().strftime("%Y-%m-%d")

# =========================================
# BUDGET MANAGEMENT
# =========================================

def budget_management():
    """Budgetverwaltung"""
    st.header("💰 Budget Management")
    project = st.session_state.hermes_project
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Budget Overview")
        st.metric("Total Budget", f"CHF {project.master_data.budget:,.2f}")
        st.metric("Actual Costs", f"CHF {project.actual_costs:,.2f}")
        
        remaining = project.master_data.budget - project.actual_costs
        st.metric("Remaining Budget", f"CHF {remaining:,.2f}")
        
        usage_percentage = (project.actual_costs / project.master_data.budget * 100) if project.master_data.budget > 0 else 0
        st.metric("Usage", f"{usage_percentage:.1f}%")
    
    with col2:
        st.subheader("Update Costs")
        new_costs = st.number_input("Actual Costs (CHF)", min_value=0.0, value=float(project.actual_costs))
        
        if st.button("Update Costs"):
            project.actual_costs = new_costs
            st.success("Costs updated successfully!")
            st.rerun()
        
        # Budget Chart
        if project.master_data.budget > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Budget'],
                y=[project.master_data.budget],
                name='Total Budget',
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                x=['Budget'],
                y=[project.actual_costs],
                name='Actual Costs',
                marker_color='coral'
            ))
            fig.update_layout(title="Budget vs Actual Costs", barmode='overlay')
            st.plotly_chart(fig, use_container_width=True)

# =========================================
# PHASE GOVERNANCE
# =========================================

def phase_governance():
    """Phase Governance und Checklisten"""
    st.header("⚙️ Phase Governance")
    project = st.session_state.hermes_project
    
    for phase_name, phase in project.phases.items():
        with st.expander(f"{phase_name.title()} - Governance", expanded=False):
            
            # Required Documents
            st.write("**Required Documents:**")
            for doc_name in phase.required_documents:
                doc = project.documents.get(doc_name)
                status_icon = "✅" if doc and doc.status == "completed" else "❌"
                st.write(f"{status_icon} {doc_name}")
            
            # Checklist Management
            st.write("**Checklists:**")
            if phase_name not in phase.checklist_results:
                phase.checklist_results[phase_name] = {}
            
            checklist_item = st.text_input(f"Add checklist item for {phase_name}", key=f"check_{phase_name}")
            if st.button(f"Add to {phase_name} checklist", key=f"add_{phase_name}"):
                if checklist_item:
                    phase.checklist_results[phase_name][checklist_item] = False
                    st.rerun()
            
            # Checklist Items anzeigen und bearbeiten
            for item, completed in phase.checklist_results.get(phase_name, {}).items():
                new_completed = st.checkbox(item, value=completed, key=f"chk_{phase_name}_{item}")
                if new_completed != completed:
                    phase.checklist_results[phase_name][item] = new_completed

# =========================================
# VOLLSTÄNDIG INTEGRIERTE ITERATION & RELEASE GOVERNANCE
# =========================================

def enhanced_iteration_management():
    """Erweiterte Iteration-Verwaltung mit Governance"""
    st.header("🔄 Iterations & Releases")
    project = st.session_state.hermes_project

    if project.master_data.approach != "agile":
        st.info("🔄 Switch to agile approach in Project Initialization to use iterations")
        return

    # Neue Iteration anlegen
    with st.expander("➕ Add New Iteration", expanded=False):
        with st.form("iteration_form"):
            col1, col2 = st.columns(2)
            with col1:
                iteration_number = st.number_input("Iteration Number", min_value=1, value=1)
                iteration_name = st.text_input("Iteration Name", f"Sprint {iteration_number}")
                start_date = st.date_input("Start Date", datetime.now())
                end_date = st.date_input("End Date", datetime.now() + timedelta(days=14))
            with col2:
                total_stories = st.number_input("Total User Stories", min_value=0, value=10)
                release_candidate = st.checkbox("Release Candidate")
                goals = st.text_area("Iteration Goals (one per line)").split('\n')

            if st.form_submit_button("Create Iteration"):
                iteration = Iteration(
                    number=iteration_number,
                    name=iteration_name,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    total_user_stories=total_stories,
                    release_candidate=release_candidate
                )
                # Goals als Attribut hinzufügen
                iteration.goals = [g.strip() for g in goals if g.strip()]

                project.iterations.append(iteration)

                # Automatisch Release-Dokument erstellen
                release_doc_name = f"Release Report {iteration.number}"
                if release_doc_name not in project.documents:
                    project.documents[release_doc_name] = HermesDocument(
                        name=release_doc_name,
                        responsible="Project Manager",
                        linked_result=f"Release {iteration.number}"
                    )

                st.success("Iteration created with release document!")
                st.rerun()

    # Bestehende Iterationen anzeigen
    for iteration in project.iterations:
        with st.expander(f"Iteration {iteration.number}: {iteration.name} ({iteration.status})", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Period:** {iteration.start_date} to {iteration.end_date}")
                st.write(f"**Progress:** {iteration.progress():.1f}%")
                st.progress(iteration.progress() / 100)

                # Story-Fortschritt aktualisieren
                completed = st.number_input(
                    "Completed Stories",
                    min_value=0,
                    max_value=iteration.total_user_stories,
                    value=iteration.completed_user_stories,
                    key=f"completed_{iteration.number}"
                )
                iteration.completed_user_stories = completed

                # Iteration Status
                iteration.status = st.selectbox(
                    "Iteration Status",
                    ["planned", "active", "completed"],
                    index=["planned", "active", "completed"].index(iteration.status),
                    key=f"iter_status_{iteration.number}"
                )

                # Goals anzeigen
                if hasattr(iteration, 'goals') and iteration.goals:
                    st.write("**Goals:**")
                    for goal in iteration.goals:
                        st.write(f"• {goal}")

            with col2:
                if iteration.release_candidate:
                    st.info("🎯 Release Candidate")

                    # Release-Governance Prüfung
                    release_doc_name = f"Release Report {iteration.number}"
                    release_doc = project.documents.get(release_doc_name)
                    release_result_name = f"Release {iteration.number}"

                    can_approve = True

                    # Prüfe Release-Dokument
                    if release_doc and release_doc.status != "completed":
                        st.warning("📄 Release Report not completed")
                        can_approve = False

                    # Prüfe Release-Ergebnis
                    release_phase = project.phases.get("implementation")
                    if release_phase and release_result_name in release_phase.results:
                        release_result = release_phase.results[release_result_name]
                        if release_result.status != "completed":
                            st.warning("🎯 Release result not completed")
                            can_approve = False

                    if not iteration.release_approved:
                        if st.button(f"Approve Release {iteration.number}",
                                    key=f"approve_{iteration.number}",
                                    disabled=not can_approve):

                            iteration.release_approved = True
                            iteration.status = "completed"

                            # Release-Ergebnis als approved markieren
                            if release_phase and release_result_name in release_phase.results:
                                release_phase.results[release_result_name].status = "approved"
                                release_phase.results[release_result_name].approval_date = datetime.now().strftime("%Y-%m-%d")

                            # Release-Meilenstein erstellen
                            release_milestone = HermesMilestone(
                                name=f"Release {iteration.number} - {iteration.name}",
                                phase="implementation",
                                date=datetime.now().strftime("%Y-%m-%d"),
                                status="reached",
                                mandatory=False
                            )
                            project.milestones.append(release_milestone)
                            st.success("✅ Release approved! Milestone created.")
                    else:
                        st.success("✅ Release Approved")
                        st.write(f"Approved on: {datetime.now().strftime('%d.%m.%Y')}")

            # Report Generation
            st.subheader("Reports")
            col_pdf, col_excel = st.columns(2)

            with col_pdf:
                pdf_buffer = generate_comprehensive_release_report(iteration, project)
                st.download_button(
                    "📊 PDF Report",
                    data=pdf_buffer,
                    file_name=f"release_{iteration.number}_report.pdf",
                    mime="application/pdf"
                )

            with col_excel:
                excel_buffer = generate_excel_release_report(iteration, project)
                st.download_button(
                    "📈 Excel Report",
                    data=excel_buffer,
                    file_name=f"release_{iteration.number}_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# =========================================
# GOVERNANCE-GESTEUERTE MEILENSTEINE
# =========================================

def enhanced_milestone_timeline():
    """Erweiterte Meilenstein-Ansicht mit Governance"""
    st.header("🎯 Milestones")
    project = st.session_state.hermes_project

    # Timeline Visualisierung
    if project.milestones:
        dates = []
        names = []
        status_colors = []
        status_text = []

        for ms in project.milestones:
            # Datum für Visualisierung (aktuelles Datum falls nicht gesetzt)
            display_date = datetime.now() if not ms.date else datetime.strptime(ms.date, "%Y-%m-%d")
            dates.append(display_date)
            names.append(ms.name)

            # Farbe basierend auf Status und Validierung
            if ms.status == "reached":
                status_colors.append("green")
                status_text.append("Reached")
            else:
                validation = validate_milestone_completion(ms, project)
                if validation["can_reach"]:
                    status_colors.append("orange")
                    status_text.append("Ready to reach")
                else:
                    status_colors.append("blue")
                    status_text.append("Planned")

        # Timeline Chart
        fig = go.Figure()

        for i, (date, name, color, status) in enumerate(zip(dates, names, status_colors, status_text)):
            fig.add_trace(go.Scatter(
                x=[date],
                y=[i],
                mode='markers+text',
                marker=dict(size=15, color=color),
                text=[name],
                textposition="middle right",
                name=name,
                hovertemplate=f"<b>{name}</b><br>Status: {status}<br>Date: {date.strftime('%d.%m.%Y')}<extra></extra>"
            ))

        fig.update_layout(
            title="Project Milestones Timeline",
            xaxis_title="Date",
            yaxis=dict(showticklabels=False),
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # Meilenstein-Details und Governance
    st.subheader("Milestone Management")

    for ms in project.milestones:
        with st.expander(f"{ms.name} ({ms.phase}) - {ms.status}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Phase:** {ms.phase}")
                st.write(f"**Mandatory:** {'Yes' if ms.mandatory else 'No'}")
                if ms.date:
                    st.write(f"**Date:** {ms.date}")

                # Governance-Validierung anzeigen
                validation = validate_milestone_completion(ms, project)

                st.write("**Completion Requirements:**")
                if validation["phase_results_complete"]:
                    st.success("✅ Phase results completed")
                else:
                    st.error("❌ Phase results incomplete")

                if validation["required_documents_complete"]:
                    st.success("✅ Required documents completed")
                else:
                    st.error("❌ Required documents incomplete")

                if validation["checklists_complete"]:
                    st.success("✅ Checklists completed")
                else:
                    st.error("❌ Checklists incomplete")

            with col2:
                if ms.status != "reached":
                    if validation["can_reach"]:
                        if st.button(f"Reach Milestone", key=f"reach_{ms.name}"):
                            ms.status = "reached"
                            ms.date = datetime.now().strftime("%Y-%m-%d")
                            st.success(f"Milestone '{ms.name}' reached!")
                            st.rerun()
                    else:
                        st.warning("Cannot reach milestone yet")
                        st.info("Complete all requirements above")

                # Status bearbeiten (nur für Admin/fallback)
                new_status = st.selectbox(
                    "Status",
                    ["planned", "reached", "delayed"],
                    index=["planned", "reached", "delayed"].index(ms.status),
                    key=f"ms_status_{ms.name}"
                )
                if new_status != ms.status:
                    ms.status = new_status
                    if new_status == "reached" and not ms.date:
                        ms.date = datetime.now().strftime("%Y-%m-%d")

# =========================================
# AUTOMATISCHE DOKUMENT-ERGEBNIS-SYNCHRONISATION
# =========================================

def enhanced_documents_center():
    """Erweitertes Document Center mit automatischer Synchronisation"""
    st.header("📄 Documents Center")
    project = st.session_state.hermes_project
    
    if not project.documents:
        st.info("No documents defined yet. Initialize project first.")
        return

    # Dokument-Statistiken
    doc_status = {}
    for doc in project.documents.values():
        doc_status[doc.status] = doc_status.get(doc.status, 0) + 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Documents", len(project.documents))
    with col2:
        st.metric("Completed", doc_status.get("completed", 0))
    with col3:
        st.metric("In Progress", doc_status.get("in_progress", 0))
    with col4:
        st.metric("Not Started", doc_status.get("not_started", 0))

    # Dokumentliste mit Synchronisation
    for doc_name, doc in project.documents.items():
        with st.expander(f"{doc_name} - {doc.status}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Responsible:** {doc.responsible}")
                if doc.linked_result:
                    st.write(f"**Linked to:** {doc.linked_result}")
                    # Zeige Status des verknüpften Ergebnisses
                    for phase in project.phases.values():
                        if doc.linked_result in phase.results:
                            result = phase.results[doc.linked_result]
                            st.write(f"**Result Status:** {result.status}")
                            break
            
            with col2:
                old_status = doc.status
                new_status = st.selectbox(
                    "Status",
                    ["not_started", "in_progress", "completed"],
                    index=["not_started", "in_progress", "completed"].index(doc.status),
                    key=f"doc_status_{doc_name}"
                )
                if new_status != old_status:
                    doc.status = new_status
                    # Automatische Synchronisation auf Ergebnis
                    if new_status == "completed" and doc.linked_result:
                        sync_document_to_result(doc, project)
                        st.success(f"✅ Document completed and result '{doc.linked_result}' updated!")
                    st.rerun()

# =========================================
# INTEGRIERTE PROJEKTINITIALISIERUNG
# =========================================

def enhanced_project_initialization():
    """Projektinitialisierung mit automatischen Meilensteinen"""
    st.header("🚀 Project Initialization")
    project = st.session_state.hermes_project
    
    with st.form("init_form"):
        project.master_data.project_name = st.text_input("Project Name", project.master_data.project_name)
        project.master_data.client = st.text_input("Client", project.master_data.client)
        project.master_data.project_manager = st.text_input("Project Manager", project.master_data.project_manager)
        project.master_data.user_representative = st.text_input("User Representative", project.master_data.user_representative)
        
        start_date_value = datetime.now() if not project.master_data.start_date else datetime.strptime(project.master_data.start_date, "%Y-%m-%d")
        project.master_data.start_date = st.date_input("Start Date", start_date_value).strftime("%Y-%m-%d")
        
        project.master_data.budget = st.number_input("Budget (CHF)", min_value=0, value=project.master_data.budget or 100000)
        
        approach = st.selectbox(
            "Approach", 
            ["classical", "agile"], 
            index=0 if project.master_data.approach == "classical" else 1
        )
        project.master_data.approach = approach
        
        project.master_data.project_size = st.selectbox(
            "Project Size", 
            ["small", "medium", "large"], 
            index=["small", "medium", "large"].index(project.master_data.project_size)
        )

        if st.form_submit_button("Initialize Project"):
            missing_roles = validate_minimal_roles(project)
            if missing_roles:
                st.error(f"Missing mandatory roles: {', '.join(missing_roles)}")
            elif not project.master_data.project_name:
                st.error("Project name is required")
            else:
                init_project_structure(project)
                initialize_mandatory_milestones(project)  # Meilensteine sofort erstellen
                st.success("✅ Project initialized with standard milestones!")
                st.rerun()

# =========================================
# INFORMATION SECTION
# =========================================

def show_hermes_info():
    """Zeigt HERMES Informationen"""
    st.header("ℹ️ HERMES 2022 Information")
    
    st.subheader("About HERMES")
    st.write("""
    HERMES is a project management method developed by the Swiss Federal Administration. 
    It provides a flexible framework for managing projects of all sizes and complexities.
    """)
    
    st.subheader("Key Features")
    st.write("""
    • **Standardized Phases**: Initialization, Concept, Implementation, Introduction, Completion
    • **Governance Framework**: Clear decision points and approvals
    • **Document Management**: Structured document handling
    • **Milestone Tracking**: Visual progress monitoring
    • **Agile & Classical**: Supports both approaches
    """)
    
    st.subheader("Project Sizes")
    st.write("""
    • **Small**: Simple projects with limited scope
    • **Medium**: Standard projects with moderate complexity  
    • **Large**: Complex projects with multiple stakeholders
    """)

# =========================================
# ANGEPASSTE MAIN APP
# =========================================

def main():
    st.set_page_config(
        page_title="HERMES 2022", 
        layout="wide",
        page_icon="🎯"
    )
    
    init_session_state()
    hermes_header()
    
    menu = st.sidebar.radio("Navigation", [
        "Dashboard",
        "Project Initialization", 
        "Results Management",
        "Budget Management",
        "Phase Governance",
        "Milestones",
        "Iterations & Releases",
        "Documents",
        "Information"
    ])

    if menu == "Dashboard":
        project_dashboard()
    elif menu == "Project Initialization":
        enhanced_project_initialization()
    elif menu == "Results Management":
        results_management()
    elif menu == "Budget Management":
        budget_management()
    elif menu == "Phase Governance":
        phase_governance()
    elif menu == "Milestones":
        enhanced_milestone_timeline()
    elif menu == "Iterations & Releases":
        enhanced_iteration_management()
    elif menu == "Documents":
        enhanced_documents_center()
    elif menu == "Information":
        show_hermes_info()

# Hilfsmethode für Iteration Progress
def progress(self):
    """Berechnet den Fortschritt der Iteration"""
    if self.total_user_stories > 0:
        return (self.completed_user_stories / self.total_user_stories) * 100
    return 0

# Progress-Methode zur Iteration-Klasse hinzufügen
Iteration.progress = progress

if __name__ == "__main__":
    main()
