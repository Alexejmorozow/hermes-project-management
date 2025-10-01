# app.py - VOLLSTÄNDIGE INTERNATIONALE VERSION MIT ALLEN FUNKTIONEN
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
# INTERNATIONALISIERUNG - ERWEITERTE ÜBERSETZUNGEN
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
        
        # Common UI Elements
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "add": "Add",
        "export": "Export",
        "import": "Import",
        "download": "Download",
        "upload": "Upload",
        "status": "Status",
        "progress": "Progress",
        "required": "Required",
        "optional": "Optional",
        "name": "Name",
        "description": "Description",
        "date": "Date",
        "amount": "Amount",
        "category": "Category",
        "type": "Type",
        "responsible": "Responsible",
        "actions": "Actions",
        "create": "Create",
        "update": "Update",
        "submit": "Submit",
        "reset": "Reset",
        "search": "Search",
        "filter": "Filter",
        "view": "View",
        "details": "Details",
        "summary": "Summary",
        "overview": "Overview",
        "settings": "Settings",
        "help": "Help",
        "language": "Language",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "close": "Close",
        "next": "Next",
        "previous": "Previous",
        "confirm": "Confirm",
        "reject": "Reject",
        "approve": "Approve",
        
        # Status Values
        "not_started": "Not Started",
        "in_progress": "In Progress",
        "completed": "Completed", 
        "approved": "Approved",
        "rejected": "Rejected",
        "planned": "Planned",
        "reached": "Reached",
        "delayed": "Delayed",
        "active": "Active",
        "inactive": "Inactive",
        "draft": "Draft",
        "final": "Final",
        
        # Project Data
        "project_name": "Project Name",
        "client": "Client",
        "project_manager": "Project Manager",
        "user_representative": "User Representative", 
        "start_date": "Start Date",
        "end_date": "End Date",
        "budget": "Budget",
        "approach": "Approach",
        "project_size": "Project Size",
        "current_phase": "Current Phase",
        "project_id": "Project ID",
        "project_description": "Project Description",
        
        # Approaches
        "classical": "Classical",
        "agile": "Agile",
        
        # Sizes
        "small": "Small",
        "medium": "Medium",
        "large": "Large",
        
        # Instructions
        "instructions": "Instructions",
        "dashboard_instructions": """
        The **Dashboard** provides a high-level overview of your project:
        
        📊 **Budget & Timeline**
        - Current budget utilization and remaining funds
        - Project timeline and phase progress
        - Financial health indicators
        
        🎯 **Milestones & Progress**  
        - Upcoming critical milestones
        - Overall project completion percentage
        - Current phase status
        
        ⚠️ **Risk & Quality**
        - Current risk level assessment
        - Quality score based on deliverables
        - Project health status
        
        💡 **Tip**: Use the export functions to generate stakeholder reports.
        """,
        
        "project_initialization_instructions": """
        **Initialize your HERMES project with these essential steps:**
        
        1. **Basic Project Data** - Enter project name, client, and key roles
        2. **Project Approach** - Choose between classical (phased) or agile (iterative) methodology  
        3. **Project Size** - Select the appropriate size for automatic tailoring
        4. **Budget & Timeline** - Set the initial budget and start date
        
        🔧 **Automatic Tailoring**: Based on your project size, HERMES will automatically configure:
        - Required vs. optional documents
        - Appropriate checklists and governance level
        - Mandatory milestones
        - Role assignments
        
        💡 **Tip**: Complete all mandatory fields (*) to ensure proper project setup.
        """,
        
        "results_management_instructions": """
        **Manage project results and deliverables:**
        
        📋 **Result Tracking**
        - Track completion status of all phase results
        - Request and manage approvals for critical deliverables
        - Assign responsible roles and track progress
        
        ✅ **Approval Workflow**
        - Results requiring approval must be formally accepted
        - Automatic status updates when approvals are granted
        - Audit trail of approval dates and responsibles
        
        🔄 **Phase Coordination** 
        - Results are organized by project phases
        - Progress indicators for each phase
        - Dependency tracking between results
        
        💡 **Tip**: Use the template library to quickly add standard HERMES results.
        """,

        "documents_instructions": """
        **Manage project documents and their relationships:**
        
        📄 **Document Management**
        - Track document status and completion
        - Assign responsible team members
        - Link documents to specific results
        
        🔗 **Automatic Synchronization**
        - When a document is completed, linked results are automatically updated
        - Maintain consistency between documents and deliverables
        - Track document versions and content
        
        📊 **Document Analytics**
        - Overview of document completion rates
        - Status distribution across all documents
        - Export capabilities for document registers
        """,

        "milestones_instructions": """
        **Track and manage project milestones:**
        
        🗓️ **Timeline Visualization**
        - Interactive timeline of all project milestones
        - Color-coded status indicators (planned, reached, delayed)
        - Mouse-over details for each milestone
        
        ✅ **Milestone Governance**
        - Automatic validation of completion criteria
        - Phase result and document completion checks
        - Checklist validation for milestone approval
        
        🎯 **Milestone Operations**
        - Reach milestones when all criteria are met
        - Track milestone dates and status changes
        - Monitor mandatory vs. optional milestones
        """,

        "phase_governance_instructions": """
        **Govern project phases with structured checklists:**
        
        📋 **Phase Checklists**
        - Comprehensive checklists for each project phase
        - Automatic validation of completion criteria
        - Progress tracking for phase activities
        
        ✅ **Completion Validation**
        - Validate results completion and approvals
        - Check required document availability
        - Ensure checklist items are completed
        
        🔄 **Phase Transitions**
        - Automatic phase advancement when criteria are met
        - Milestone validation for phase completion
        - Audit trail of phase start and end dates
        """,

        "iterations_instructions": """
        **Manage agile iterations and releases:**
        
        🔄 **Iteration Planning**
        - Create and manage development iterations
        - Set iteration goals and user story targets
        - Track velocity and completion rates
        
        🚀 **Release Management**
        - Designate release candidates
        - Comprehensive release approval checks
        - Automatic milestone creation for releases
        
        ✅ **Release Governance**
        - Validate release documentation
        - Check budget and milestone readiness
        - Formal release approval workflow
        """,

        "budget_instructions": """
        **Track project finances and expenditures:**
        
        💰 **Budget Monitoring**
        - Real-time budget vs. actual comparison
        - Traffic light indicators for budget health
        - Remaining budget calculations
        
        📊 **Transaction Management**
        - Record actual and planned expenditures
        - Categorize costs by type and purpose
        - Maintain complete financial audit trail
        
        📈 **Financial Analytics**
        - Spending breakdown by category
        - Cumulative cost tracking over time
        - Export capabilities for financial reporting
        """,
        
        # Error & Validation Messages
        "missing_mandatory_roles": "Missing mandatory roles",
        "is_required": "is required",
        "please_complete_field": "Please complete this field",
        "validation_error": "Validation Error",
        "success_message": "Success",
        "error_message": "Error",
        "warning_message": "Warning",
        "info_message": "Information",
        "please_initialize_project": "Please initialize your project in 'Project Initialization'.",
        "coming_soon": "Implementation in progress",
        
        # Success Messages
        "project_initialized": "Project successfully initialized with tailoring applied",
        "changes_saved": "Changes saved successfully",
        "item_created": "Item created successfully",
        "item_updated": "Item updated successfully",
        "item_deleted": "Item deleted successfully",
        "phase_completed": "Phase completed successfully",
        "milestone_reached": "Milestone reached successfully",
        "release_approved": "Release approved successfully",
        "transaction_added": "Transaction added successfully",
        
        # Report Titles
        "project_status_report": "Project Status Report",
        "executive_summary": "Executive Summary",
        "budget_report": "Budget Report",
        "milestone_report": "Milestone Report",
        "phase_progress_report": "Phase Progress Report",
        
        # Budget & Financial
        "planned_budget": "Planned Budget",
        "actual_costs": "Actual Costs", 
        "remaining_budget": "Remaining Budget",
        "budget_usage": "Budget Usage",
        "cost_breakdown": "Cost Breakdown",
        "financial_overview": "Financial Overview",
        "transactions": "Transactions",
        "transaction_history": "Transaction History",
        "spending_by_category": "Spending by Category",
        "cumulative_spending": "Cumulative Spending",
        
        # Milestones & Timeline
        "timeline": "Timeline",
        "upcoming_milestones": "Upcoming Milestones",
        "completed_milestones": "Completed Milestones",
        "milestone_name": "Milestone Name",
        "milestone_date": "Milestone Date",
        "mandatory": "Mandatory",
        "optional_milestone": "Optional",
        "milestone_management": "Milestone Management",
        "completion_checks": "Completion Checks",
        
        # Phases & Governance
        "phase": "Phase",
        "phases": "Phases",
        "phase_completion": "Phase Completion",
        "governance_checks": "Governance Checks",
        "checklists": "Checklists",
        "completion_criteria": "Completion Criteria",
        "phase_validation": "Phase Validation",
        "checklist_items": "Checklist Items",
        "phase_results": "Phase Results",
        "required_documents": "Required Documents",
        
        # Documents
        "document_center": "Document Center",
        "document_status": "Document Status",
        "document_management": "Document Management",
        "linked_results": "Linked Results",
        "content_management": "Content Management",
        "total_documents": "Total Documents",
        "document_analytics": "Document Analytics",
        "export_document": "Export Document",
        
        # Iterations & Releases
        "iteration": "Iteration",
        "iterations": "Iterations",
        "release": "Release",
        "releases": "Releases",
        "release_candidate": "Release Candidate",
        "release_approval": "Release Approval",
        "sprint": "Sprint",
        "user_stories": "User Stories",
        "velocity": "Velocity",
        "iteration_planning": "Iteration Planning",
        "release_checks": "Release Checks",
        "iteration_goals": "Iteration Goals",
        "completed_stories": "Completed Stories",
        "total_stories": "Total Stories",
        
        # Roles & Responsibilities
        "roles": "Roles",
        "responsibilities": "Responsibilities",
        "role_assignment": "Role Assignment",
        "team_members": "Team Members",
        
        # Export & Reports
        "generate_report": "Generate Report",
        "export_data": "Export Data",
        "download_pdf": "Download PDF",
        "download_excel": "Download Excel",
        "report_date": "Report Date",
        "export_reports": "Export Reports",
        "export_budget": "Export Budget Data",
        
        # System Messages
        "loading": "Loading...",
        "processing": "Processing...",
        "saving": "Saving...",
        "please_wait": "Please wait...",
        
        # Quality & Risk
        "quality_score": "Quality Score",
        "risk_level": "Risk Level",
        "risk_assessment": "Risk Assessment",
        "quality_assurance": "Quality Assurance",
        
        # Time Periods
        "today": "Today",
        "yesterday": "Yesterday",
        "this_week": "This Week",
        "this_month": "This Month",
        "this_quarter": "This Quarter",
        "this_year": "This Year",

        # Additional UI Texts
        "project": "Project",
        "results": "Results",
        "metric": "Metric",
        "value": "Value",
        "overall_progress": "Overall Progress",
        "completed_phases": "Completed Phases",
        "reached_milestones": "Reached Milestones",
        "out_of": "out of",
        "project_is": "Project is",
        "complete": "complete",
        "budget_usage_is": "Budget usage is",
        "master_data": "Master Data",
        "phase_progress": "Phase Progress",
        "completed_results": "Completed Results",
        "cannot_reach_yet": "Cannot reach milestone yet - complete requirements first",
        "reach_milestone": "Reach Milestone",
        "add_transaction": "Add Transaction",
        "add_iteration": "Add Iteration",
        "iteration_number": "Iteration Number",
        "iteration_name": "Iteration Name",
        "start_date": "Start Date",
        "end_date": "End Date",
        "goals": "Goals",
        "release_checks": "Release Checks",
        "release_document_complete": "Release document completed",
        "release_result_approved": "Release result approved",
        "budget_healthy": "Budget status healthy",
        "milestones_on_track": "Milestones on track",
        "approve_release": "Approve Release",
        "add_from_templates": "Add from templates",
        "choose_template": "Choose template",
        "approval_required": "Approval Required",
        "approval_date": "Approval Date",
        "responsible_role": "Responsible Role",
        "completion_requirements": "Completion Requirements",
        "phase_results_complete": "Phase results completed",
        "documents_ready": "Required documents completed",
        "checklists_completed": "Checklists completed",
        "complete_phase": "Complete Phase",
        "period": "Period",
        "export_budget_excel": "Export Budget to Excel",
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
        
        # Common UI Elements
        "save": "Speichern",
        "cancel": "Abbrechen",
        "edit": "Bearbeiten",
        "delete": "Löschen",
        "add": "Hinzufügen",
        "export": "Exportieren",
        "import": "Importieren",
        "download": "Herunterladen",
        "upload": "Hochladen",
        "status": "Status",
        "progress": "Fortschritt",
        "required": "Erforderlich",
        "optional": "Optional",
        "name": "Name",
        "description": "Beschreibung",
        "date": "Datum",
        "amount": "Betrag",
        "category": "Kategorie",
        "type": "Typ",
        "responsible": "Verantwortlich",
        "actions": "Aktionen",
        "create": "Erstellen",
        "update": "Aktualisieren",
        "submit": "Absenden",
        "reset": "Zurücksetzen",
        "search": "Suchen",
        "filter": "Filtern",
        "view": "Ansicht",
        "details": "Details",
        "summary": "Zusammenfassung",
        "overview": "Übersicht",
        "settings": "Einstellungen",
        "help": "Hilfe",
        "language": "Sprache",
        "yes": "Ja",
        "no": "Nein",
        "ok": "OK",
        "close": "Schließen",
        "next": "Weiter",
        "previous": "Zurück",
        "confirm": "Bestätigen",
        "reject": "Ablehnen",
        "approve": "Genehmigen",
        
        # Status Values
        "not_started": "Nicht begonnen",
        "in_progress": "In Bearbeitung",
        "completed": "Abgeschlossen",
        "approved": "Genehmigt",
        "rejected": "Abgelehnt",
        "planned": "Geplant",
        "reached": "Erreicht",
        "delayed": "Verzögert",
        "active": "Aktiv",
        "inactive": "Inaktiv",
        "draft": "Entwurf",
        "final": "Final",
        
        # Project Data
        "project_name": "Projektname",
        "client": "Auftraggeber",
        "project_manager": "Projektleiter",
        "user_representative": "Anwendervertreter",
        "start_date": "Startdatum",
        "end_date": "Enddatum",
        "budget": "Budget",
        "approach": "Vorgehen",
        "project_size": "Projektgröße",
        "current_phase": "Aktuelle Phase",
        "project_id": "Projekt-ID",
        "project_description": "Projektbeschreibung",
        
        # Approaches
        "classical": "Klassisch",
        "agile": "Agil",
        
        # Sizes
        "small": "Klein",
        "medium": "Mittel",
        "large": "Groß",
        
        # Instructions
        "instructions": "Anleitungen",
        "dashboard_instructions": """
        Das **Dashboard** bietet einen Überblick über Ihr Projekt:
        
        📊 **Budget & Zeitplan**
        - Aktuelle Budgetauslastung und verbleibende Mittel
        - Projektzeitplan und Phasenfortschritt
        - Finanzielle Gesundheitsindikatoren
        
        🎯 **Meilensteine & Fortschritt**
        - Bevorstehende kritische Meilensteine
        - Gesamtprojekt-Fertigstellungsgrad
        - Status der aktuellen Phase
        
        ⚠️ **Risiko & Qualität**
        - Aktuelle Risikobewertung
        - Qualitäts-Score basierend auf Lieferobjekten
        - Projekt-Health-Status
        
        💡 **Tipp**: Nutzen Sie die Export-Funktionen für Stakeholder-Berichte.
        """,
        
        "project_initialization_instructions": """
        **Initialisieren Sie Ihr HERMES-Projekt in diesen Schritten:**
        
        1. **Projektstammdaten** - Projektname, Auftraggeber und Schlüsselrollen
        2. **Projektvorgehen** - Wählen Sie zwischen klassischem (phasenbasiert) oder agilem (iterativ) Vorgehen
        3. **Projektgröße** - Wählen Sie die passende Größe für automatisches Tailoring
        4. **Budget & Zeitplan** - Legen Sie Startbudget und -datum fest
        
        🔧 **Automatisches Tailoring**: Basierend auf der Projektgröße konfiguriert HERMES automatisch:
        - Erforderliche vs. optionale Dokumente
        - Passende Checklisten und Governance-Level
        - Verpflichtende Meilensteine
        - Rollenzuordnungen
        
        💡 **Tipp**: Füllen Sie alle Pflichtfelder (*) aus für eine korrekte Projekteinrichtung.
        """,
        
        "results_management_instructions": """
        **Verwalten Sie Projektergebnisse und Lieferobjekte:**
        
        📋 **Ergebnisverfolgung**
        - Verfolgen Sie den Fertigstellungsstatus aller Phasenergebnisse
        - Beantragen und verwalten Sie Freigaben für kritische Lieferobjekte
        - Weisen Sie verantwortliche Rollen zu und verfolgen Sie Fortschritte
        
        ✅ **Freigabe-Workflow**
        - Ergebnisse mit Freigabepflicht müssen formal akzeptiert werden
        - Automatische Statusupdates bei erteilten Freigaben
        - Prüfpfad der Freigabedaten und Verantwortlichen
        
        🔄 **Phasenkoordination**
        - Ergebnisse sind nach Projektphasen organisiert
        - Fortschrittsindikatoren für jede Phase
        - Abhängigkeitstracking zwischen Ergebnissen
        
        💡 **Tipp**: Nutzen Sie die Vorlagen-Bibliothek für standard HERMES-Ergebnisse.
        """,

        "documents_instructions": """
        **Verwalten Sie Projektdokumente und ihre Beziehungen:**
        
        📄 **Dokumentenmanagement**
        - Verfolgen Sie Dokumentstatus und Fertigstellung
        - Weisen Sie verantwortliche Teammitglieder zu
        - Verknüpfen Sie Dokumente mit spezifischen Ergebnissen
        
        🔗 **Automatische Synchronisation**
        - Wenn ein Dokument abgeschlossen ist, werden verknüpfte Ergebnisse automatisch aktualisiert
        - Wahrung der Konsistenz zwischen Dokumenten und Lieferobjekten
        - Verfolgen Sie Dokumentversionen und Inhalte
        
        📊 **Dokumentenanalyse**
        - Überblick über Dokumenten-Fertigstellungsraten
        - Statusverteilung über alle Dokumente
        - Exportfunktionen für Dokumentenregister
        """,

        "milestones_instructions": """
        **Verfolgen und verwalten Sie Projektmeilensteine:**
        
        🗓️ **Zeitplanvisualisierung**
        - Interaktiver Zeitplan aller Projektmeilensteine
        - Farbcodierte Statusindikatoren (geplant, erreicht, verzögert)
        - Mouse-over Details für jeden Meilenstein
        
        ✅ **Meilenstein-Governance**
        - Automatische Validierung der Abschlusskriterien
        - Prüfung der Phasenergebnisse und Dokumentenfertigstellung
        - Checklistenvalidierung für Meilensteinfreigabe
        
        🎯 **Meilensteinoperationen**
        - Erreichen Sie Meilensteine, wenn alle Kriterien erfüllt sind
        - Verfolgen Sie Meilensteindaten und Statusänderungen
        - Überwachen Sie verpflichtende vs. optionale Meilensteine
        """,

        "phase_governance_instructions": """
        **Steuern Sie Projektphasen mit strukturierten Checklisten:**
        
        📋 **Phasen-Checklisten**
        - Umfassende Checklisten für jede Projektphase
        - Automatische Validierung der Abschlusskriterien
        - Fortschrittsverfolgung für Phasenaktivitäten
        
        ✅ **Abschlussvalidierung**
        - Validieren Sie den Abschluss und die Freigaben von Ergebnissen
        - Prüfen Sie die Verfügbarkeit erforderlicher Dokumente
        - Stellen Sie sicher, dass Checklistenpunkte abgeschlossen sind
        
        🔄 **Phasenübergänge**
        - Automatischer Phasenfortschritt bei erfüllten Kriterien
        - Meilensteinvalidierung für Phasenabschluss
        - Prüfpfad der Phasenstart- und -enddaten
        """,

        "iterations_instructions": """
        **Verwalten Sie agile Iterationen und Releases:**
        
        🔄 **Iterationsplanung**
        - Erstellen und verwalten Sie Entwicklungsiterationen
        - Setzen Sie Iterationsziele und User-Story-Ziele
        - Verfolgen Sie Velocity und Fertigstellungsraten
        
        🚀 **Release-Management**
        - Bestimmen Sie Release-Kandidaten
        - Umfassende Release-Freigabeprüfungen
        - Automatische Meilensteinerstellung für Releases
        
        ✅ **Release-Governance**
        - Validieren Sie Release-Dokumentation
        - Prüfen Sie Budget- und Meilensteinbereitschaft
        - Formeller Release-Freigabe-Workflow
        """,

        "budget_instructions": """
        **Verfolgen Sie Projektfinanzen und Ausgaben:**
        
        💰 **Budgetüberwachung**
        - Echtzeit-Vergleich von Budget vs. Ist
        - Ampelsystem für Budgetgesundheit
        - Berechnung des verbleibenden Budgets
        
        📊 **Transaktionsmanagement**
        - Erfassen Sie Ist- und Planausgaben
        - Kategorisieren Sie Kosten nach Art und Zweck
        - Führen Sie einen vollständigen Finanzprüfpfad
        
        📈 **Finanzanalyse**
        - Ausgabenaufschlüsselung nach Kategorien
        - Kumulative Kostenverfolgung über die Zeit
        - Exportfunktionen für Finanzberichterstattung
        """,
        
        # Error & Validation Messages
        "missing_mandatory_roles": "Fehlende Pflichtrollen",
        "is_required": "ist erforderlich",
        "please_complete_field": "Bitte füllen Sie dieses Feld aus",
        "validation_error": "Validierungsfehler",
        "success_message": "Erfolg",
        "error_message": "Fehler",
        "warning_message": "Warnung",
        "info_message": "Information",
        "please_initialize_project": "Bitte initialisieren Sie Ihr Projekt unter 'Projektinitialisierung'.",
        "coming_soon": "Implementierung in Arbeit",
        
        # Success Messages
        "project_initialized": "Projekt erfolgreich initialisiert mit Tailoring",
        "changes_saved": "Änderungen erfolgreich gespeichert",
        "item_created": "Element erfolgreich erstellt",
        "item_updated": "Element erfolgreich aktualisiert",
        "item_deleted": "Element erfolgreich gelöscht",
        "phase_completed": "Phase erfolgreich abgeschlossen",
        "milestone_reached": "Meilenstein erfolgreich erreicht",
        "release_approved": "Release erfolgreich genehmigt",
        "transaction_added": "Transaktion erfolgreich hinzugefügt",
        
        # Report Titles
        "project_status_report": "Projektstatusbericht",
        "executive_summary": "Zusammenfassung",
        "budget_report": "Budgetbericht",
        "milestone_report": "Meilensteinbericht",
        "phase_progress_report": "Phasenfortschrittsbericht",
        
        # Budget & Financial
        "planned_budget": "Geplantes Budget",
        "actual_costs": "Ist-Kosten",
        "remaining_budget": "Verbleibendes Budget",
        "budget_usage": "Budgetauslastung",
        "cost_breakdown": "Kostenaufschlüsselung",
        "financial_overview": "Finanzübersicht",
        "transactions": "Transaktionen",
        "transaction_history": "Transaktionshistorie",
        "spending_by_category": "Ausgaben nach Kategorie",
        "cumulative_spending": "Kumulative Ausgaben",
        
        # Milestones & Timeline
        "timeline": "Zeitplan",
        "upcoming_milestones": "Bevorstehende Meilensteine",
        "completed_milestones": "Abgeschlossene Meilensteine",
        "milestone_name": "Meilensteinname",
        "milestone_date": "Meilensteindatum",
        "mandatory": "Verpflichtend",
        "optional_milestone": "Optional",
        "milestone_management": "Meilensteinverwaltung",
        "completion_checks": "Abschlussprüfungen",
        
        # Phases & Governance
        "phase": "Phase",
        "phases": "Phasen",
        "phase_completion": "Phasenabschluss",
        "governance_checks": "Governance-Prüfungen",
        "checklists": "Checklisten",
        "completion_criteria": "Abschlusskriterien",
        "phase_validation": "Phasenvalidierung",
        "checklist_items": "Checklistenpunkte",
        "phase_results": "Phasenergebnisse",
        "required_documents": "Erforderliche Dokumente",
        
        # Documents
        "document_center": "Dokumentencenter",
        "document_status": "Dokumentstatus",
        "document_management": "Dokumentenverwaltung",
        "linked_results": "Verknüpfte Ergebnisse",
        "content_management": "Inhaltsverwaltung",
        "total_documents": "Gesamtdokumente",
        "document_analytics": "Dokumentenanalyse",
        "export_document": "Dokument exportieren",
        
        # Iterations & Releases
        "iteration": "Iteration",
        "iterations": "Iterationen",
        "release": "Release",
        "releases": "Releases",
        "release_candidate": "Release-Kandidat",
        "release_approval": "Release-Freigabe",
        "sprint": "Sprint",
        "user_stories": "User Stories",
        "velocity": "Velocity",
        "iteration_planning": "Iterationsplanung",
        "release_checks": "Release-Prüfungen",
        "iteration_goals": "Iterationsziele",
        "completed_stories": "Abgeschlossene Stories",
        "total_stories": "Gesamt-Stories",
        
        # Roles & Responsibilities
        "roles": "Rollen",
        "responsibilities": "Verantwortlichkeiten",
        "role_assignment": "Rollenzuordnung",
        "team_members": "Teammitglieder",
        
        # Export & Reports
        "generate_report": "Bericht erstellen",
        "export_data": "Daten exportieren",
        "download_pdf": "PDF herunterladen",
        "download_excel": "Excel herunterladen",
        "report_date": "Berichtsdatum",
        "export_reports": "Berichte exportieren",
        "export_budget": "Budgetdaten exportieren",
        
        # System Messages
        "loading": "Lädt...",
        "processing": "Verarbeitet...",
        "saving": "Speichert...",
        "please_wait": "Bitte warten...",
        
        # Quality & Risk
        "quality_score": "Qualitäts-Score",
        "risk_level": "Risikolevel",
        "risk_assessment": "Risikobewertung",
        "quality_assurance": "Qualitätssicherung",
        
        # Time Periods
        "today": "Heute",
        "yesterday": "Gestern",
        "this_week": "Diese Woche",
        "this_month": "Diesen Monat",
        "this_quarter": "Dieses Quartal",
        "this_year": "Dieses Jahr",

        # Additional UI Texts
        "project": "Projekt",
        "results": "Ergebnisse",
        "metric": "Metrik",
        "value": "Wert",
        "overall_progress": "Gesamtfortschritt",
        "completed_phases": "Abgeschlossene Phasen",
        "reached_milestones": "Erreichte Meilensteine",
        "out_of": "von",
        "project_is": "Projekt ist",
        "complete": "abgeschlossen",
        "budget_usage_is": "Budgetauslastung ist",
        "master_data": "Stammdaten",
        "phase_progress": "Phasenfortschritt",
        "completed_results": "Abgeschlossene Ergebnisse",
        "cannot_reach_yet": "Meilenstein kann noch nicht erreicht werden - erfüllen Sie zuerst die Anforderungen",
        "reach_milestone": "Meilenstein erreichen",
        "add_transaction": "Transaktion hinzufügen",
        "add_iteration": "Iteration hinzufügen",
        "iteration_number": "Iterationsnummer",
        "iteration_name": "Iterationsname",
        "start_date": "Startdatum",
        "end_date": "Enddatum",
        "goals": "Ziele",
        "release_checks": "Release-Prüfungen",
        "release_document_complete": "Release-Dokument abgeschlossen",
        "release_result_approved": "Release-Ergebnis genehmigt",
        "budget_healthy": "Budgetstatus gesund",
        "milestones_on_track": "Meilensteine im Plan",
        "approve_release": "Release genehmigen",
        "add_from_templates": "Aus Vorlagen hinzufügen",
        "choose_template": "Vorlage auswählen",
        "approval_required": "Freigabe erforderlich",
        "approval_date": "Freigabedatum",
        "responsible_role": "Verantwortliche Rolle",
        "completion_requirements": "Abschlussanforderungen",
        "phase_results_complete": "Phasenergebnisse abgeschlossen",
        "documents_ready": "Erforderliche Dokumente abgeschlossen",
        "checklists_completed": "Checklisten abgeschlossen",
        "complete_phase": "Phase abschließen",
        "period": "Zeitraum",
        "export_budget_excel": "Budget nach Excel exportieren",
    }
}

def t(key: str, language: str = "en") -> str:
    """Translation helper function - returns key if translation not found"""
    return TRANSLATIONS.get(language, {}).get(key, key)

# =========================================
# DATACLASSES (UNVERÄNDERT VORHER)
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
# KONFIGURATIONEN (UNVERÄNDERT VORHER)
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
        },
        "Requirements Specification": {
            "description": "Detailed requirements specification",
            "approval_required": True,
            "role": "user_representative"
        },
        "Solution Concept": {
            "description": "Technical solution architecture",
            "approval_required": True, 
            "role": "project_manager"
        },
        "Test Concept": {
            "description": "Testing strategy and approach",
            "approval_required": False,
            "role": "project_manager"
        },
        "Acceptance Protocol": {
            "description": "Formal user acceptance documentation",
            "approval_required": True,
            "role": "client"
        },
        "Project Completion Report": {
            "description": "Final project completion documentation",
            "approval_required": True,
            "role": "project_manager"
        },
        "Release 1": {
            "description": "First product release",
            "approval_required": True,
            "role": "project_manager"
        },
        "Release 2": {
            "description": "Second product release", 
            "approval_required": True,
            "role": "project_manager"
        }
    },
    "de": {
        "Projektauftrag": {
            "description": "Formelles Projektinitialisierungsdokument",
            "approval_required": True,
            "role": "project_manager"
        },
        "Stakeholder-Analyse": {
            "description": "Identifikation und Analyse der Stakeholder",
            "approval_required": False,
            "role": "project_manager"
        },
        "Anforderungsspezifikation": {
            "description": "Detaillierte Anforderungsspezifikation",
            "approval_required": True,
            "role": "user_representative"
        },
        "Lösungskonzept": {
            "description": "Technische Lösungsarchitektur",
            "approval_required": True,
            "role": "project_manager"
        },
        "Testkonzept": {
            "description": "Teststrategie und -vorgehen",
            "approval_required": False,
            "role": "project_manager"
        },
        "Abnahmeprotokoll": {
            "description": "Formelle Benutzerabnahmedokumentation",
            "approval_required": True,
            "role": "client"
        },
        "Projektabschlussbericht": {
            "description": "Finale Projektabschlussdokumentation",
            "approval_required": True,
            "role": "project_manager"
        },
        "Release 1": {
            "description": "Erstes Produkt-Release",
            "approval_required": True,
            "role": "project_manager"
        },
        "Release 2": {
            "description": "Zweites Produkt-Release",
            "approval_required": True, 
            "role": "project_manager"
        }
    }
}

DOCUMENT_NAME_MAPPING = {
    "en": {
        "Project Charter": "Project Charter",
        "Stakeholder Analysis": "Stakeholder Analysis", 
        "Requirements Specification": "Requirements Specification",
        "Solution Concept": "Solution Concept",
        "Test Concept": "Test Concept",
        "Acceptance Protocol": "Acceptance Protocol",
        "Project Completion Report": "Project Completion Report",
        "Release Report": "Release Report"
    },
    "de": {
        "Project Charter": "Projektauftrag",
        "Stakeholder Analysis": "Stakeholder-Analyse",
        "Requirements Specification": "Anforderungsspezifikation", 
        "Solution Concept": "Lösungskonzept",
        "Test Concept": "Testkonzept",
        "Acceptance Protocol": "Abnahmeprotokoll",
        "Project Completion Report": "Projektabschlussbericht",
        "Release Report": "Release-Bericht"
    }
}

HERMES_CHECKLISTS = {
    "en": {
        "initialization_comprehensive": [
            "Project mandate verified and documented",
            "Stakeholder analysis performed and approved",
            "Budget and resources confirmed as sufficient",
            "High-level risks identified and assessed",
            "Project approach and methodology decided"
        ],
        "initialization_simplified": [
            "Project mandate exists",
            "Key responsible persons assigned"
        ],
        "concept_comprehensive": [
            "Requirements validated with all user groups",
            "Solution alternatives assessed and selected",
            "Economic efficiency proven with business case",
            "Security and protection requirements considered"
        ],
        "concept_simplified": [
            "Requirements discussed and agreed",
            "Solution direction confirmed"
        ],
        "implementation_comprehensive": [
            "Test strategy defined and resources allocated",
            "Migration concept finalized and approved",
            "Operational readiness plan established"
        ],
        "completion_comprehensive": [
            "Operational handover completed successfully",
            "Final acceptance signed by client",
            "Lessons learned documented and shared",
            "Financial closure procedures completed"
        ],
        "completion_simplified": [
            "Handover to operations completed",
            "Final acceptance obtained"
        ]
    },
    "de": {
        "initialization_comprehensive": [
            "Projektmandat geprüft und dokumentiert",
            "Stakeholder-Analyse durchgeführt und genehmigt",
            "Budget und Ressourcen als ausreichend bestätigt",
            "Risiken auf hoher Ebene identifiziert und bewertet",
            "Projektvorgehen und Methodik entschieden"
        ],
        "initialization_simplified": [
            "Projektmandat vorhanden",
            "Wesentliche Verantwortliche zugeordnet"
        ],
        "concept_comprehensive": [
            "Anforderungen mit allen Anwendergruppen validiert",
            "Lösungsalternativen bewertet und ausgewählt",
            "Wirtschaftlichkeit mit Business Case nachgewiesen",
            "Sicherheits- und Schutzanforderungen berücksichtigt"
        ],
        "concept_simplified": [
            "Anforderungen besprochen und vereinbart",
            "Lösungsrichtung bestätigt"
        ],
        "implementation_comprehensive": [
            "Teststrategie definiert und Ressourcen zugeordnet",
            "Migrationskonzept finalisiert und genehmigt",
            "Plan für Betriebsbereitschaft erstellt"
        ],
        "completion_comprehensive": [
            "Operative Übergabe erfolgreich abgeschlossen",
            "Endabnahme durch Auftraggeber unterzeichnet",
            "Lessons Learned dokumentiert und geteilt",
            "Finanzielle Abschlussverfahren abgeschlossen"
        ],
        "completion_simplified": [
            "Übergabe an den Betrieb abgeschlossen",
            "Endabnahme eingeholt"
        ]
    }
}

DEFAULT_HERMES_ROLES = {
    "en": {
        "client": "Client",
        "project_manager": "Project Manager",
        "user_representative": "User Representative",
        "project_controller": "Project Controller",
        "quality_manager": "Quality Manager"
    },
    "de": {
        "client": "Auftraggeber",
        "project_manager": "Projektleiter",
        "user_representative": "Anwendervertreter",
        "project_controller": "Projektcontroller",
        "quality_manager": "Qualitätsmanager"
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
        required_documents=["Project Charter", "Acceptance Protocol"],
        optional_documents=["Stakeholder Analysis", "Test Concept"],
        simplified_checklists=True,
        mandatory_milestones=["Project Initialization", "Project Completion"],
        extra_roles=[]
    ),
    "medium": ProjectSizeConfig(
        required_documents=["Project Charter", "Stakeholder Analysis", "Requirements Specification", "Solution Concept", "Acceptance Protocol"],
        optional_documents=["Test Concept"],
        simplified_checklists=False,
        mandatory_milestones=["Project Initialization", "Implementation Decision", "Project Completion"],
        extra_roles=["project_controller"]
    ),
    "large": ProjectSizeConfig(
        required_documents=["Project Charter", "Stakeholder Analysis", "Requirements Specification", "Solution Concept", "Test Concept", "Acceptance Protocol", "Project Completion Report"],
        optional_documents=[],
        simplified_checklists=False,
        mandatory_milestones=["Project Initialization", "Implementation Decision", "Phase Release Concept", "Phase Release Realization", "Project Completion"],
        extra_roles=["project_controller", "quality_manager"]
    )
}

# =========================================
# HELPER FUNCTIONS (UNVERÄNDERT VORHER)
# =========================================
def get_phase_labels(project: HermesProject):
    lang = project.master_data.language
    approach = project.master_data.approach
    return HERMES_PHASE_LABELS.get(lang, HERMES_PHASE_LABELS["en"]).get(approach, {})

def get_result_templates(project: HermesProject):
    lang = project.master_data.language
    return RESULT_TEMPLATES.get(lang, RESULT_TEMPLATES["en"])

def get_checklists(project: HermesProject):
    lang = project.master_data.language
    return HERMES_CHECKLISTS.get(lang, HERMES_CHECKLISTS["en"])

def get_default_roles(project: HermesProject):
    lang = project.master_data.language
    return DEFAULT_HERMES_ROLES.get(lang, DEFAULT_HERMES_ROLES["en"])

def get_document_name(original_name: str, language: str):
    return DOCUMENT_NAME_MAPPING.get(language, {}).get(original_name, original_name)

def map_document_names(doc_names: List[str], from_lang: str, to_lang: str) -> List[str]:
    mapping = DOCUMENT_NAME_MAPPING.get(from_lang, {})
    reverse_mapping = {v: k for k, v in DOCUMENT_NAME_MAPPING.get(to_lang, {}).items()}
    
    mapped_names = []
    for doc_name in doc_names:
        original_name = reverse_mapping.get(doc_name, doc_name)
        mapped_name = mapping.get(original_name, original_name)
        mapped_names.append(mapped_name)
    
    return mapped_names

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
        translated_doc_name = get_document_name(doc_name, lang)
        docs[translated_doc_name] = HermesDocument(
            name=translated_doc_name,
            responsible=roles.get(doc_config.get("role", "project_manager"), "Project Manager"),
            required=True,
            linked_result=doc_name
        )
    project.documents.update(docs)
    
    for phase_key, phase in project.phases.items():
        if phase_key == "initialization":
            template_names = ["Project Charter", "Stakeholder Analysis"]
        elif phase_key == "concept":
            template_names = ["Requirements Specification", "Solution Concept"]
        elif phase_key in ["realization", "implementation"]:
            template_names = ["Test Concept"]
        elif phase_key == "introduction":
            template_names = ["Acceptance Protocol"]
        elif phase_key == "completion":
            template_names = ["Project Completion Report"]
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
    
    required_docs = map_document_names(config.required_documents, "en", lang)
    optional_docs = map_document_names(config.optional_documents, "en", lang)
    
    for name, doc in project.documents.items():
        if name in required_docs:
            doc.required = True
        elif name in optional_docs:
            doc.required = False
    
    checklists = get_checklists(project)
    for key, phase in project.phases.items():
        if config.simplified_checklists:
            checklist_key = f"{key}_simplified"
            checklist_items = checklists.get(checklist_key, checklists.get(f"{key}_comprehensive", []))
        else:
            checklist_items = checklists.get(f"{key}_comprehensive", [])
        
        for item in checklist_items:
            if item not in phase.checklist_results:
                phase.checklist_results[item] = False
    
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

def validate_phase_completion(phase: ProjectPhase) -> Dict[str, bool]:
    result_ok = True
    for r in phase.results.values():
        if r.approval_required and r.status != "approved":
            result_ok = False
            break
    
    docs_ok = True
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
    
    for r in phase.results.values():
        if r.approval_required and r.status != "approved":
            validation["phase_results_complete"] = False
            break
    
    for doc_name in phase.required_documents:
        doc = project.documents.get(doc_name)
        if doc and doc.required and doc.status != "completed":
            validation["required_documents_complete"] = False
            break
    
    if phase.checklist_results:
        if not all(phase.checklist_results.values()):
            validation["checklists_complete"] = False
    
    validation["can_reach"] = (
        validation["phase_results_complete"] and 
        validation["required_documents_complete"] and 
        validation["checklists_complete"]
    )
    
    return validation

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

def calculate_risk_level(project: HermesProject) -> str:
    prog = calculate_total_progress(project)
    if prog > 80:
        return "low"
    elif prog > 50:
        return "medium"
    else:
        return "high"

def calculate_quality_score(project: HermesProject) -> int:
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
    if document.linked_result and document.status == "completed":
        for phase in project.phases.values():
            if document.linked_result in phase.results:
                res = phase.results[document.linked_result]
                if res.status not in ("completed", "approved"):
                    res.status = "completed"

def auto_advance_phase(project: HermesProject):
    current = project.master_data.current_phase
    phase_keys = list(project.phases.keys())
    
    if current not in phase_keys:
        return
    
    idx = phase_keys.index(current)
    phase = project.phases[current]
    validation = validate_phase_completion(phase)
    
    milestone_ready = any(ms.phase == current and ms.status == "reached" for ms in project.milestones)
    
    if validation["can_complete"] and milestone_ready:
        phase.status = "completed"
        phase.end_date = datetime.now().strftime("%Y-%m-%d")
        
        if idx + 1 < len(phase_keys):
            next_key = phase_keys[idx + 1]
            project.master_data.current_phase = next_key
            project.phases[next_key].status = "active"
            project.phases[next_key].start_date = datetime.now().strftime("%Y-%m-%d")

# =========================================
# KOMPLETTE IMPLEMENTIERTE VIEWS
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
        st.title("HERMES 2022 — Project Management Assistant")
        st.caption("Multilingual tool demonstrating HERMES concepts")
    
    with col3:
        current_lang = project.master_data.language
        new_lang = st.selectbox(
            "🌐 " + t('language', lang),
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            index=list(SUPPORTED_LANGUAGES.keys()).index(current_lang),
            key="language_selector"
        )
        
        if new_lang != current_lang:
            project.master_data.language = new_lang
            st.rerun()

def project_dashboard():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("dashboard", "dashboard_instructions")
    
    if not project.master_data.project_name:
        st.info(t('please_initialize_project', lang))
        return
    
    # Project overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t('project', lang), project.master_data.project_name)
    with col2:
        st.metric(t('approach', lang), t(project.master_data.approach, lang))
    with col3:
        st.metric(t('project_size', lang), t(project.master_data.project_size, lang))
    with col4:
        st.metric(t('current_phase', lang), project.phases[project.master_data.current_phase].name)
    
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
    
    # Progress indicators
    st.subheader(t('progress', lang))
    for key, phase in project.phases.items():
        st.write(f"**{phase.name}** — {t(phase.status, lang)}")
        prog = calculate_phase_progress(phase)
        st.progress(prog / 100)
        completed_results = sum(1 for r in phase.results.values() if r.status in ('completed','approved'))
        st.caption(f"{completed_results}/{len(phase.results)} {t('results', lang)} {t('completed', lang).lower()}")
    
    # Report exports
    st.markdown("---")
    st.subheader(t('export_reports', lang))
    col1, col2 = st.columns(2)
    
    with col1:
        pdf_report = generate_project_status_report_pdf(project)
        st.download_button(
            t('download_pdf', lang),
            data=pdf_report,
            file_name=f"status_{project.master_data.project_name}_{lang}.pdf",
            mime="application/pdf"
        )
    
    with col2:
        excel_report = generate_project_status_report_excel(project)
        st.download_button(
            t('download_excel', lang),
            data=excel_report, 
            file_name=f"status_{project.master_data.project_name}_{lang}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
                st.error(f"{t('missing_mandatory_roles', lang)}: {', '.join(missing_translated)}")
            elif not project.master_data.project_name:
                st.error(f"{t('project_name', lang)} {t('is_required', lang)}")
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
    
    show_instructions("results_management", "results_management_instructions")
    
    for key, phase in project.phases.items():
        with st.expander(f"{phase.name} — {t(phase.status, lang)}", expanded=False):
            # Add result from templates
            st.write(t("add_from_templates", lang) + ":")
            templates = get_result_templates(project)
            template_names = list(templates.keys())
            tmpl = st.selectbox(f"{t('choose_template', lang)} ({phase.name})", [""] + template_names, key=f"tmpl_{key}")
            if tmpl:
                if st.button(f"{t('add', lang)} '{tmpl}' {t('to', lang)} {phase.name}", key=f"addres_{key}_{tmpl}"):
                    t_config = templates[tmpl]
                    phase.results[tmpl] = PhaseResult(
                        name=tmpl,
                        description=t_config.get("description",""),
                        approval_required=t_config.get("approval_required", False),
                        responsible_role=t_config.get("role","")
                    )
                    st.success(f"{t('result', lang)} '{tmpl}' {t('added_to', lang)} {phase.name}")
            
            # Show existing results
            for rname, r in phase.results.items():
                col1, col2, col3 = st.columns([3,2,2])
                with col1:
                    st.write(f"**{rname}**")
                    st.caption(r.description)
                    st.write(f"{t('responsible_role', lang)}: {r.responsible_role or '—'}")
                with col2:
                    status_options = ["not_started", "in_progress", "completed", "approved"]
                    status_labels = [t(s, lang) for s in status_options]
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
                        if new_status == "approved":
                            r.approval_date = datetime.now().strftime("%Y-%m-%d")
                with col3:
                    if r.approval_required:
                        st.write(f"✅ {t('approval_required', lang)}")
                        if r.approval_date:
                            st.write(f"{t('approval_date', lang)}: {r.approval_date}")
                    else:
                        st.write(f"➖ {t('approval_required', lang)}")

def enhanced_documents_center():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("documents", "documents_instructions")
    
    if not project.documents:
        st.info(f"{t('no_documents_available', lang)} {t('please_initialize_project', lang)}")
        return
    
    # Document statistics
    status_counts = {}
    for d in project.documents.values():
        status_counts[d.status] = status_counts.get(d.status, 0) + 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("total_documents", lang), len(project.documents))
    with col2:
        st.metric(t("completed", lang), status_counts.get("completed", 0))
    with col3:
        st.metric(t("in_progress", lang), status_counts.get("in_progress", 0))
    
    # Document list with editing
    for dname, doc in project.documents.items():
        with st.expander(f"{dname} — {t(doc.status, lang)}", expanded=False):
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"{t('responsible', lang)}: {doc.responsible}")
                if doc.linked_result:
                    st.write(f"{t('linked_results', lang)}: {doc.linked_result}")
                doc.content = st.text_area(t("content_management", lang), value=doc.content, key=f"doccont_{dname}")
            with col2:
                status_options = ["not_started", "in_progress", "completed"]
                status_labels = [t(s, lang) for s in status_options]
                current_index = status_options.index(doc.status)
                new_status = st.selectbox(
                    t("status", lang),
                    status_options,
                    format_func=lambda x: t(x, lang),
                    index=current_index,
                    key=f"docstat_{dname}"
                )
                
                role_options = list(project.roles.values())
                current_resp_index = role_options.index(doc.responsible) if doc.responsible in role_options else 0
                doc.responsible = st.selectbox(
                    t("responsible", lang),
                    role_options,
                    index=current_resp_index,
                    key=f"docresp_{dname}"
                )
                
                if new_status != doc.status:
                    doc.status = new_status
                    if doc.status == "completed" and doc.linked_result:
                        sync_document_to_result(doc, project)
                        st.success(f"✅ {t('document', lang)} {t('completed', lang).lower()} {t('and', lang)} {t('linked_result', lang).lower()} '{doc.linked_result}' {t('updated', lang).lower()}")
            
            # Export document
            if st.button(f"{t('export_document', lang)} (txt)", key=f"export_{dname}"):
                st.download_button(
                    label=f"{t('download', lang)} {dname}.txt",
                    data=doc.content or f"{dname}\n\n({t('no_content', lang)})",
                    file_name=f"{dname.replace(' ', '_')}.txt",
                    mime="text/plain"
                )

def enhanced_milestone_timeline():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("milestones", "milestones_instructions")
    
    if not project.milestones:
        st.info(f"{t('no_milestones_configured', lang)} {t('please_initialize_project', lang)}")
        return
    
    # Timeline visualization
    fig = go.Figure()
    for i, ms in enumerate(project.milestones):
        x = datetime.now() if not ms.date else datetime.strptime(ms.date, "%Y-%m-%d")
        color = "green" if ms.status == "reached" else "orange" if validate_milestone_completion(ms, project)["can_reach"] else "blue"
        fig.add_trace(go.Scatter(
            x=[x], 
            y=[i], 
            mode='markers+text', 
            text=[ms.name], 
            textposition="middle right", 
            marker=dict(size=15, color=color),
            hovertemplate=f"<b>{ms.name}</b><br>{t('phase', lang)}: {ms.phase}<br>{t('status', lang)}: {t(ms.status, lang)}<br>{t('date', lang)}: {ms.date or t('not_set', lang)}<extra></extra>"
        ))
    
    fig.update_layout(
        title=t("timeline", lang),
        xaxis_title=t("date", lang),
        yaxis=dict(showticklabels=False),
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Milestone details
    st.subheader(t("milestone_management", lang))
    for ms in project.milestones:
        with st.expander(f"{ms.name} ({ms.phase}) — {t(ms.status, lang)}", expanded=False):
            val = validate_milestone_completion(ms, project)
            st.write(f"**{t('completion_checks', lang)}:**")
            st.write(f"- {t('phase_results_complete', lang)}: {'✅' if val['phase_results_complete'] else '❌'}")
            st.write(f"- {t('required_documents_complete', lang)}: {'✅' if val['required_documents_complete'] else '❌'}")
            st.write(f"- {t('checklists_completed', lang)}: {'✅' if val['checklists_complete'] else '❌'}")
            
            if ms.status != "reached":
                if val["can_reach"]:
                    if st.button(f"{t('reach_milestone', lang)}: {ms.name}", key=f"reach_{ms.name}"):
                        ms.status = "reached"
                        ms.date = datetime.now().strftime("%Y-%m-%d")
                        st.success(f"🎉 {t('milestone', lang)} '{ms.name}' {t('reached', lang).lower()}!")
                        st.rerun()
                else:
                    st.info(f"⏳ {t('cannot_reach_yet', lang)}")

def phase_governance():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("phase_governance", "phase_governance_instructions")
    
    for key, phase in project.phases.items():
        with st.expander(f"{phase.name} — {t(phase.status, lang)}"):
            # Checklist items
            st.write(f"**{t('checklists', lang)}:**")
            if phase.checklist_results:
                for item, val in list(phase.checklist_results.items()):
                    new_val = st.checkbox(item, value=val, key=f"chk_{key}_{item}")
                    if new_val != val:
                        phase.checklist_results[item] = new_val
            else:
                st.write(f"➖ {t('no_checklist_items', lang)}")
            
            # Required documents
            st.write(f"**{t('required_documents', lang)}:**")
            for doc_name in phase.required_documents:
                doc = project.documents.get(doc_name)
                status = t(doc.status, lang) if doc else t('not_defined', lang)
                st.write(f"- {doc_name}: {status}")
            
            # Results summary
            st.write(f"**{t('phase_results', lang)}:**")
            for r in phase.results.values():
                approval_text = f" ({t('approval_required', lang)})" if r.approval_required else ""
                st.write(f"- {r.name}: {t(r.status, lang)}{approval_text}")
            
            # Phase completion action
            val = validate_phase_completion(phase)
            st.write(f"**{t('can_complete', lang)}?** {'✅' if val['can_complete'] else '❌'}")
            
            if val["can_complete"] and st.button(f"{t('complete_phase', lang)} {phase.name}", key=f"complete_{key}"):
                phase.status = "completed"
                phase.end_date = datetime.now().strftime("%Y-%m-%d")
                auto_advance_phase(project)
                st.success(f"🎉 {t('phase', lang)} '{phase.name}' {t('completed', lang).lower()}!")
                st.rerun()

def enhanced_iteration_management():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("iterations_releases", "iterations_instructions")
    
    if project.master_data.approach != "agile":
        st.info(f"🔁 {t('switch_to_agile', lang)}")
        return
    
    # Add new iteration
    with st.expander(f"➕ {t('add_iteration', lang)}", expanded=False):
        with st.form("iter_form"):
            col1, col2 = st.columns(2)
            with col1:
                num = st.number_input(t("iteration_number", lang), min_value=1, value=1)
                name = st.text_input(t("iteration_name", lang), f"Sprint {num}")
                start = st.date_input(t("start_date", lang), datetime.now())
                end = st.date_input(t("end_date", lang), datetime.now() + timedelta(days=14))
            with col2:
                total = st.number_input(t("total_stories", lang), min_value=0, value=10)
                release_candidate = st.checkbox(t("release_candidate", lang))
                goals = st.text_area(t("goals", lang) + " (one per line)").split("\n")
            
            if st.form_submit_button(f"🚀 {t('create', lang)} {t('iteration', lang)}"):
                it = Iteration(
                    number=int(num), 
                    name=name, 
                    start_date=start.strftime("%Y-%m-%d"), 
                    end_date=end.strftime("%Y-%m-%d"), 
                    total_user_stories=int(total), 
                    release_candidate=release_candidate, 
                    goals=[g.strip() for g in goals if g.strip()]
                )
                project.iterations.append(it)
                
                # Ensure release result exists
                release_res_name = f"Release {it.number}"
                impl_phase_key = "implementation" if "implementation" in project.phases else "realization"
                if impl_phase_key in project.phases and release_res_name not in project.phases[impl_phase_key].results:
                    project.phases[impl_phase_key].results[release_res_name] = PhaseResult(
                        name=release_res_name,
                        description=f"{t('release', lang)} {t('result', lang)} {t('for', lang)} {it.name}",
                        approval_required=True,
                        responsible_role="project_manager"
                    )
                
                # Create release document
                docname = f"Release Report {it.number}"
                if docname not in project.documents:
                    project.documents[docname] = HermesDocument(
                        name=docname,
                        responsible=t("project_manager", lang),
                        status="not_started",
                        linked_result=release_res_name,
                        required=True
                    )
                
                st.success(f"✅ {t('iteration', lang)} '{it.name}' {t('created', lang).lower()}!")
                st.rerun()
    
    # List iterations
    for it in sorted(project.iterations, key=lambda x: x.number):
        with st.expander(f"{t('iteration', lang)} {it.number}: {it.name} ({t(it.status, lang)})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{t('period', lang)}:** {it.start_date} — {it.end_date}")
                st.write(f"**{t('progress', lang)}:** {it.progress():.1f}%")
                st.progress(it.progress() / 100)
                
                comp = st.number_input(
                    t("completed_stories", lang),
                    min_value=0,
                    max_value=it.total_user_stories,
                    value=it.completed_user_stories,
                    key=f"comp_{it.number}"
                )
                it.completed_user_stories = comp
                
                it.status = st.selectbox(
                    t("status", lang),
                    ["planned", "active", "completed"],
                    format_func=lambda x: t(x, lang),
                    index=["planned", "active", "completed"].index(it.status),
                    key=f"stat_{it.number}"
                )
            
            with col2:
                if it.release_candidate:
                    st.info(f"🚀 {t('release_candidate', lang)}")
                    
                    # Release validation
                    val = validate_release_approval(it, project)
                    st.write(f"**{t('release_checks', lang)}:**")
                    st.write(f"- {t('release_document_complete', lang)}: {'✅' if val['release_document_complete'] else '❌'}")
                    st.write(f"- {t('release_result_approved', lang)}: {'✅' if val['release_result_approved'] else '❌'}")
                    st.write(f"- {t('budget_healthy', lang)}: {'✅' if val['budget_healthy'] else '❌'}")
                    st.write(f"- {t('milestones_on_track', lang)}: {'✅' if val['milestones_on_track'] else '❌'}")
                    
                    if not it.release_approved and val["can_approve"]:
                        if st.button(f"✅ {t('approve_release', lang)} {it.number}", key=f"approve_{it.number}"):
                            it.release_approved = True
                            it.status = "completed"
                            
                            # Mark release result approved
                            release_result_name = f"Release {it.number}"
                            impl_key = "implementation" if "implementation" in project.phases else "realization"
                            if impl_key in project.phases and release_result_name in project.phases[impl_key].results:
                                project.phases[impl_key].results[release_result_name].status = "approved"
                                project.phases[impl_key].results[release_result_name].approval_date = datetime.now().strftime("%Y-%m-%d")
                            
                            # Create milestone
                            project.milestones.append(HermesMilestone(
                                name=f"Release {it.number} - {it.name}",
                                phase=impl_key,
                                date=datetime.now().strftime("%Y-%m-%d"),
                                status="reached",
                                mandatory=False
                            ))
                            st.success(f"🎉 {t('release', lang)} {it.number} {t('approved', lang).lower()}!")
                    elif it.release_approved:
                        st.success(f"✅ {t('release', lang)} {t('already_approved', lang).lower()}")

def enhanced_budget_management():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    show_instructions("budget_management", "budget_instructions")
    
    if not project.master_data.project_name:
        st.info(t('please_initialize_project', lang))
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(t("planned_budget", lang), f"CHF {project.master_data.budget:,.2f}")
        actual = sum(t.amount for t in project.budget_entries if t.type == "actual")
        st.metric(t("actual_costs", lang), f"CHF {actual:,.2f}")
        st.metric(t("remaining_budget", lang), f"CHF {project.master_data.budget - actual:,.2f}")
        
        # Budget health indicator
        usage = calculate_budget_usage(project)
        if usage < 0.7:
            st.success(f"💰 {t('budget_usage', lang)}: {usage:.1%}")
        elif usage < 0.9:
            st.warning(f"💰 {t('budget_usage', lang)}: {usage:.1%}")
        else:
            st.error(f"💰 {t('budget_usage', lang)}: {usage:.1%}")
    
    with col2:
        with st.form("tx_form"):
            tx_date = st.date_input(t("date", lang), datetime.now()).strftime("%Y-%m-%d")
            category = st.selectbox(t("category", lang), ["Personnel", "Hardware", "Software", "External Services", "Training", "Travel", "Other"])
            amount = st.number_input(f"{t('amount', lang)} (CHF)", min_value=0.0, step=100.0)
            desc = st.text_input(t("description", lang))
            tx_type = st.selectbox(t("type", lang), ["actual", "planned"])
            if st.form_submit_button(f"➕ {t('add_transaction', lang)}"):
                project.budget_entries.append(BudgetTransaction(
                    date=tx_date, 
                    category=category, 
                    amount=amount, 
                    description=desc, 
                    type=tx_type
                ))
                st.success(f"✅ {t('transaction_added', lang)}!")
                st.rerun()
    
    # Transaction history and analytics
    if project.budget_entries:
        st.subheader(t("transaction_history", lang))
        df = pd.DataFrame([asdict(t) for t in project.budget_entries])
        st.dataframe(df, use_container_width=True)
        
        # Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            # Spending by category
            actual_df = df[df["type"] == "actual"]
            if not actual_df.empty:
                cat = actual_df.groupby("category")["amount"].sum()
                fig = px.pie(
                    values=cat.values, 
                    names=cat.index, 
                    title=t("spending_by_category", lang)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cumulative spending
            if not actual_df.empty:
                actual_df['date'] = pd.to_datetime(actual_df['date'])
                time_series = actual_df.groupby('date')['amount'].sum().cumsum()
                if not time_series.empty:
                    fig = px.line(
                        x=time_series.index,
                        y=time_series.values,
                        title=t("cumulative_spending", lang),
                        labels={'x': t('date', lang), 'y': f"{t('amount', lang)} (CHF)"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Export functionality
        st.subheader(t("export_data", lang))
        if st.button(f"📊 {t('export_budget_excel', lang)}"):
            out = BytesIO()
            with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name=t("transactions", lang))
                summary = pd.DataFrame([
                    {t("metric", lang): t("planned_budget", lang), t("value", lang): project.master_data.budget},
                    {t("metric", lang): t("actual_costs", lang), t("value", lang): sum(actual_df['amount'])},
                    {t("metric", lang): t("budget_usage", lang), t("value", lang): f"{usage:.1%}"}
                ])
                summary.to_excel(writer, index=False, sheet_name=t("summary", lang))
            out.seek(0)
            st.download_button(
                f"💾 {t('download_excel', lang)}",
                data=out.getvalue(),
                file_name=f"budget_{project.master_data.project_name}_{lang}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def show_hermes_info():
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    st.header("ℹ️ HERMES 2022 Project Management")
    st.write("""
    This multilingual application demonstrates the core concepts of HERMES 2022:
    
    **🎯 Key Features:**
    - **Tailoring**: Automatic configuration based on project size (small, medium, large)
    - **Governance**: Phase-based checklists and milestone validation
    - **Document-Result Synchronization**: Automated status updates
    - **Agile & Classical**: Support for both project approaches
    - **Multilingual**: Full support for English and German
    
    **📊 Core Components:**
    - Project initialization with automatic tailoring
    - Result and document management
    - Milestone tracking with governance checks
    - Budget management and financial tracking
    - Iteration and release management for agile projects
    
    **🌍 Internationalization:**
    - Real-time language switching
    - Translated user interface and content
    - Localized reports and exports
    """)
    
    st.info("💡 Use the language selector in the header to switch between English and German.")

# Helper function for release validation
def validate_release_approval(iteration: Iteration, project: HermesProject) -> Dict[str, bool]:
    res = {
        "release_document_complete": True, 
        "release_result_approved": True, 
        "budget_healthy": True, 
        "milestones_on_track": True, 
        "can_approve": True
    }
    
    # Release document check
    docname = f"Release Report {iteration.number}"
    doc = project.documents.get(docname)
    if not doc or doc.status != "completed":
        res["release_document_complete"] = False
    
    # Release result check
    release_name = f"Release {iteration.number}"
    impl_key = "implementation" if "implementation" in project.phases else "realization"
    if impl_key in project.phases and release_name in project.phases[impl_key].results:
        r = project.phases[impl_key].results[release_name]
        if r.status != "completed":
            res["release_result_approved"] = False
    else:
        res["release_result_approved"] = False
    
    # Budget health check
    usage = calculate_budget_usage(project)
    if usage > 0.9:
        res["budget_healthy"] = False
    
    # Milestones check
    for ms in project.milestones:
        if ms.mandatory and ms.phase == impl_key and ms.status != "reached":
            res["milestones_on_track"] = False
    
    res["can_approve"] = all(res.values())
    return res

# Report generation functions (from previous implementation)
def generate_project_status_report_pdf(project: HermesProject) -> bytes:
    lang = project.master_data.language
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph(f"{t('project_status_report', lang)} - {project.master_data.project_name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    total_progress = calculate_total_progress(project)
    budget_usage = calculate_budget_usage(project)
    completed_phases = sum(1 for p in project.phases.values() if p.status == "completed")
    
    summary_text = f"{t('executive_summary', lang)}: {t('project_is', lang)} {total_progress:.1f}% {t('complete', lang)}. {t('budget_usage_is', lang)} {budget_usage:.1%}. {completed_phases} {t('out_of', lang)} {len(project.phases)} {t('phases', lang)} {t('completed', lang).lower()}."
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Master data table
    master_table = [
        [t('project_name', lang), project.master_data.project_name],
        [t('client', lang), project.master_data.client],
        [t('project_manager', lang), project.master_data.project_manager],
        [t('user_representative', lang), project.master_data.user_representative],
        [t('approach', lang), t(project.master_data.approach, lang)],
        [t('project_size', lang), t(project.master_data.project_size, lang)],
        [t('start_date', lang), project.master_data.start_date],
        [t('budget', lang) + " (CHF)", f"{project.master_data.budget:,.2f}"]
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
    lang = project.master_data.language
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Executive summary
        summary_data = {
            t('metric', lang): [
                t('overall_progress', lang),
                t('budget_usage', lang), 
                t('completed_phases', lang),
                t('reached_milestones', lang)
            ],
            t('value', lang): [
                f"{calculate_total_progress(project):.1f}%",
                f"{calculate_budget_usage(project):.1%}",
                f"{sum(1 for p in project.phases.values() if p.status == 'completed')}/{len(project.phases)}",
                f"{sum(1 for m in project.milestones if m.status == 'reached')}/{len(project.milestones)}"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name=t('executive_summary', lang), index=False)
        
        # Master data
        master_dict = asdict(project.master_data)
        master_dict['approach'] = t(master_dict['approach'], lang)
        master_dict['project_size'] = t(master_dict['project_size'], lang)
        pd.DataFrame([master_dict]).to_excel(writer, sheet_name=t('master_data', lang), index=False)
    
    buffer.seek(0)
    return buffer.getvalue()

# =========================================
# MAIN APPLICATION
# =========================================

def main():
    st.set_page_config(
        page_title="HERMES 2022 Assistant", 
        layout="wide",
        page_icon="🏛️"
    )
    
    init_session_state()
    hermes_header()
    
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    # Multilingual navigation
    menu = st.sidebar.radio(
        t("navigation", lang),
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
    
    # Navigation routing
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
