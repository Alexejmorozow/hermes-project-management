# app.py - VOLLSTÄNDIG INTERNATIONALISIERTE VERSION
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
# INTERNATIONALISIERUNG - KOMPLETTE ÜBERSETZUNGEN
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
        
        # Error & Validation Messages
        "missing_mandatory_roles": "Missing mandatory roles",
        "is_required": "is required",
        "please_complete_field": "Please complete this field",
        "validation_error": "Validation Error",
        "success_message": "Success",
        "error_message": "Error",
        "warning_message": "Warning",
        "info_message": "Information",
        
        # Success Messages
        "project_initialized": "Project successfully initialized with tailoring applied",
        "changes_saved": "Changes saved successfully",
        "item_created": "Item created successfully",
        "item_updated": "Item updated successfully",
        "item_deleted": "Item deleted successfully",
        
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
        
        # Milestones & Timeline
        "timeline": "Timeline",
        "upcoming_milestones": "Upcoming Milestones",
        "completed_milestones": "Completed Milestones",
        "milestone_name": "Milestone Name",
        "milestone_date": "Milestone Date",
        "mandatory": "Mandatory",
        "optional_milestone": "Optional",
        
        # Phases & Governance
        "phase": "Phase",
        "phases": "Phases",
        "phase_completion": "Phase Completion",
        "governance_checks": "Governance Checks",
        "checklists": "Checklists",
        "completion_criteria": "Completion Criteria",
        "phase_validation": "Phase Validation",
        
        # Documents
        "document_center": "Document Center",
        "document_status": "Document Status",
        "document_management": "Document Management",
        "linked_results": "Linked Results",
        "content_management": "Content Management",
        
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
        
        # Error & Validation Messages
        "missing_mandatory_roles": "Fehlende Pflichtrollen",
        "is_required": "ist erforderlich",
        "please_complete_field": "Bitte füllen Sie dieses Feld aus",
        "validation_error": "Validierungsfehler",
        "success_message": "Erfolg",
        "error_message": "Fehler",
        "warning_message": "Warnung",
        "info_message": "Information",
        
        # Success Messages
        "project_initialized": "Projekt erfolgreich initialisiert mit Tailoring",
        "changes_saved": "Änderungen erfolgreich gespeichert",
        "item_created": "Element erfolgreich erstellt",
        "item_updated": "Element erfolgreich aktualisiert",
        "item_deleted": "Element erfolgreich gelöscht",
        
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
        
        # Milestones & Timeline
        "timeline": "Zeitplan",
        "upcoming_milestones": "Bevorstehende Meilensteine",
        "completed_milestones": "Abgeschlossene Meilensteine",
        "milestone_name": "Meilensteinname",
        "milestone_date": "Meilensteindatum",
        "mandatory": "Verpflichtend",
        "optional_milestone": "Optional",
        
        # Phases & Governance
        "phase": "Phase",
        "phases": "Phasen",
        "phase_completion": "Phasenabschluss",
        "governance_checks": "Governance-Prüfungen",
        "checklists": "Checklisten",
        "completion_criteria": "Abschlusskriterien",
        "phase_validation": "Phasenvalidierung",
        
        # Documents
        "document_center": "Dokumentencenter",
        "document_status": "Dokumentstatus",
        "document_management": "Dokumentenverwaltung",
        "linked_results": "Verknüpfte Ergebnisse",
        "content_management": "Inhaltsverwaltung",
        
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
    }
}

def t(key: str, language: str = "en") -> str:
    """Translation helper function - returns key if translation not found"""
    return TRANSLATIONS.get(language, {}).get(key, key)

# =========================================
# MULTILINGUAL DATACLASSES
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
    language: str = "en"  # Store user language preference

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
# MULTILINGUAL CONFIGURATIONS
# =========================================

# Phase labels with translations
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

# Result templates with translations
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

# Document name mappings between languages
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

# Checklists with translations
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

# Default roles with translations
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
# MULTILINGUAL HELPER FUNCTIONS
# =========================================

def get_phase_labels(project: HermesProject):
    """Get phase labels in current project language"""
    lang = project.master_data.language
    approach = project.master_data.approach
    return HERMES_PHASE_LABELS.get(lang, HERMES_PHASE_LABELS["en"]).get(approach, {})

def get_result_templates(project: HermesProject):
    """Get result templates in current project language"""
    lang = project.master_data.language
    return RESULT_TEMPLATES.get(lang, RESULT_TEMPLATES["en"])

def get_checklists(project: HermesProject):
    """Get checklists in current project language"""
    lang = project.master_data.language
    return HERMES_CHECKLISTS.get(lang, HERMES_CHECKLISTS["en"])

def get_default_roles(project: HermesProject):
    """Get default roles in current project language"""
    lang = project.master_data.language
    return DEFAULT_HERMES_ROLES.get(lang, DEFAULT_HERMES_ROLES["en"])

def get_document_name(original_name: str, language: str):
    """Get translated document name"""
    return DOCUMENT_NAME_MAPPING.get(language, {}).get(original_name, original_name)

def map_document_names(doc_names: List[str], from_lang: str, to_lang: str) -> List[str]:
    """Map document names between languages"""
    mapping = DOCUMENT_NAME_MAPPING.get(from_lang, {})
    reverse_mapping = {v: k for k, v in DOCUMENT_NAME_MAPPING.get(to_lang, {}).items()}
    
    mapped_names = []
    for doc_name in doc_names:
        # First try to find the original English name
        original_name = reverse_mapping.get(doc_name, doc_name)
        # Then map to target language
        mapped_name = mapping.get(original_name, original_name)
        mapped_names.append(mapped_name)
    
    return mapped_names

# =========================================
# INITIALIZATION / SESSION STATE
# =========================================

def init_session_state():
    if "hermes_project" not in st.session_state:
        p = HermesProject()
        p.master_data.current_phase = "initialization"
        p.master_data.language = "en"  # Default language
        st.session_state.hermes_project = p
    
    proj = st.session_state.hermes_project
    if not proj.phases:
        initialize_standard_phases(proj)
    if not proj.documents:
        init_project_structure(proj)
    if not proj.roles:
        proj.roles = get_default_roles(proj).copy()

def initialize_standard_phases(project: HermesProject):
    """Initialize phases in current language"""
    labels = get_phase_labels(project)
    project.phases.clear()
    for key, lbl in labels.items():
        project.phases[key] = ProjectPhase(name=lbl)

def init_project_structure(project: HermesProject):
    """Initialize project structure in current language"""
    templates = get_result_templates(project)
    roles = get_default_roles(project)
    lang = project.master_data.language
    
    # Create documents using translated templates
    docs = {}
    for doc_name, doc_config in templates.items():
        translated_doc_name = get_document_name(doc_name, lang)
        docs[translated_doc_name] = HermesDocument(
            name=translated_doc_name,
            responsible=roles.get(doc_config.get("role", "project_manager"), "Project Manager"),
            required=True,
            linked_result=doc_name  # Keep original name for linking
        )
    project.documents.update(docs)
    
    # Initialize results in phases
    for phase_key, phase in project.phases.items():
        # Map phase to appropriate templates
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

# =========================================
# TAILORING (project size) - MULTILINGUAL
# =========================================

def apply_project_size_tailoring(project: HermesProject):
    """Apply tailoring according to project size with language support"""
    config = PROJECT_SIZE_CONFIGS.get(project.master_data.project_size, PROJECT_SIZE_CONFIGS["medium"])
    lang = project.master_data.language
    
    # Map document names to current language
    required_docs = map_document_names(config.required_documents, "en", lang)
    optional_docs = map_document_names(config.optional_documents, "en", lang)
    
    # mark docs required/optional
    for name, doc in project.documents.items():
        if name in required_docs:
            doc.required = True
        elif name in optional_docs:
            doc.required = False
    
    # set checklist items for phases
    checklists = get_checklists(project)
    for key, phase in project.phases.items():
        if config.simplified_checklists:
            checklist_key = f"{key}_simplified"
            checklist_items = checklists.get(checklist_key, checklists.get(f"{key}_comprehensive", []))
        else:
            checklist_items = checklists.get(f"{key}_comprehensive", [])
        
        # initialize checklist results if not present
        for item in checklist_items:
            if item not in phase.checklist_results:
                phase.checklist_results[item] = False
    
    # apply roles extras
    roles = get_default_roles(project)
    for r in config.extra_roles:
        if r not in project.roles:
            project.roles[r] = roles.get(r, r.replace("_", " ").title())
    
    project.tailoring = {
        "applied_size": project.master_data.project_size,
        "config": config,
        "language": lang
    }

# =========================================
# VALIDATION, GOVERNANCE, HELPERS - MULTILINGUAL
# =========================================

def validate_minimal_roles(project: HermesProject) -> List[str]:
    missing = []
    lang = project.master_data.language
    
    if not project.master_data.project_manager:
        missing.append("project_manager")
    if not project.master_data.user_representative:
        missing.append("user_representative") 
    if not project.master_data.client:
        missing.append("client")
    
    return missing

def validate_phase_completion(phase: ProjectPhase) -> Dict[str, bool]:
    """Check whether a phase can be completed"""
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
# MULTILINGUAL REPORT GENERATION
# =========================================

def generate_project_status_report_pdf(project: HermesProject) -> bytes:
    """Generate PDF report in project language"""
    lang = project.master_data.language
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title in project language
    title = Paragraph(f"{t('project_status_report', lang)} - {project.master_data.project_name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Report metadata
    metadata = Paragraph(f"{t('report_date', lang)}: {datetime.now().strftime('%d.%m.%Y')}", styles['Normal'])
    story.append(metadata)
    story.append(Spacer(1, 12))
    
    # Executive summary
    total_progress = calculate_total_progress(project)
    budget_usage = calculate_budget_usage(project)
    completed_phases = sum(1 for p in project.phases.values() if p.status == "completed")
    
    summary_text = f"""
    {t('executive_summary', lang)}: {t('project_is', lang)} {total_progress:.1f}% {t('complete', lang)}. 
    {t('budget_usage_is', lang)} {budget_usage:.1%}. 
    {completed_phases} {t('out_of', lang)} {len(project.phases)} {t('phases', lang)} {t('completed', lang).lower()}.
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Master data table with translated headers
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
    story.append(Spacer(1, 15))
    
    # Budget overview
    story.append(Paragraph(t('financial_overview', lang), styles['Heading2']))
    actual_costs = sum(t.amount for t in project.budget_entries if t.type == "actual")
    remaining_budget = project.master_data.budget - actual_costs
    
    budget_table = [
        [t('planned_budget', lang), f"CHF {project.master_data.budget:,.2f}"],
        [t('actual_costs', lang), f"CHF {actual_costs:,.2f}"],
        [t('remaining_budget', lang), f"CHF {remaining_budget:,.2f}"],
        [t('budget_usage', lang), f"{budget_usage:.1%}"]
    ]
    
    budget_tbl = Table(budget_table, colWidths=[180, 150])
    budget_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black)
    ]))
    story.append(budget_tbl)
    story.append(Spacer(1, 15))
    
    # Phase progress
    story.append(Paragraph(t('phase_progress', lang), styles['Heading2']))
    phase_data = [[t('phase', lang), t('status', lang), t('progress', lang), t('completed_results', lang)]]
    
    for key, phase in project.phases.items():
        completed_results = sum(1 for r in phase.results.values() if r.status in ("completed", "approved"))
        total_results = len(phase.results)
        phase_data.append([
            phase.name,
            t(phase.status, lang),
            f"{calculate_phase_progress(phase):.1f}%",
            f"{completed_results}/{total_results}"
        ])
    
    phase_tbl = Table(phase_data, colWidths=[150, 80, 80, 120])
    phase_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black)
    ]))
    story.append(phase_tbl)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_project_status_report_excel(project: HermesProject) -> bytes:
    """Generate Excel report in project language"""
    lang = project.master_data.language
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Executive summary
        summary_data = {
            t('metric', lang): [
                t('overall_progress', lang),
                t('budget_usage', lang), 
                t('completed_phases', lang),
                t('reached_milestones', lang),
                t('risk_level', lang),
                t('quality_score', lang)
            ],
            t('value', lang): [
                f"{calculate_total_progress(project):.1f}%",
                f"{calculate_budget_usage(project):.1%}",
                f"{sum(1 for p in project.phases.values() if p.status == 'completed')}/{len(project.phases)}",
                f"{sum(1 for m in project.milestones if m.status == 'reached')}/{len(project.milestones)}",
                t(calculate_risk_level(project), lang),
                f"{calculate_quality_score(project)}%"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name=t('executive_summary', lang), index=False)
        
        # Master data
        master_dict = asdict(project.master_data)
        # Translate approach and size
        master_dict['approach'] = t(master_dict['approach'], lang)
        master_dict['project_size'] = t(master_dict['project_size'], lang)
        master_dict['language'] = t(master_dict['language'], lang) if master_dict['language'] in ['en', 'de'] else master_dict['language']
        
        pd.DataFrame([master_dict]).to_excel(writer, sheet_name=t('master_data', lang), index=False)
        
        # Budget transactions
        if project.budget_entries:
            df_budget = pd.DataFrame([asdict(t) for t in project.budget_entries])
            # Translate column names
            df_budget.columns = [t(col, lang) if col in ['date', 'category', 'amount', 'description', 'type'] else col for col in df_budget.columns]
            df_budget.to_excel(writer, sheet_name=t('transactions', lang), index=False)
        
        # Phases and results
        phase_rows = []
        for key, phase in project.phases.items():
            for r in phase.results.values():
                phase_rows.append({
                    t('phase', lang): phase.name,
                    t('result', lang): r.name,
                    t('status', lang): t(r.status, lang),
                    t('approval_required', lang): t('yes', lang) if r.approval_required else t('no', lang),
                    t('approval_date', lang): r.approval_date,
                    t('responsible_role', lang): r.responsible_role
                })
        pd.DataFrame(phase_rows).to_excel(writer, sheet_name=t('results', lang), index=False)
        
        # Documents
        doc_rows = []
        for doc in project.documents.values():
            doc_rows.append({
                t('document', lang): doc.name,
                t('responsible', lang): doc.responsible,
                t('status', lang): t(doc.status, lang),
                t('required', lang): t('yes', lang) if doc.required else t('no', lang),
                t('linked_result', lang): doc.linked_result
            })
        pd.DataFrame(doc_rows).to_excel(writer, sheet_name=t('documents', lang), index=False)
        
        # Milestones
        milestone_rows = []
        for ms in project.milestones:
            milestone_rows.append({
                t('milestone_name', lang): ms.name,
                t('phase', lang): ms.phase,
                t('status', lang): t(ms.status, lang),
                t('date', lang): ms.date,
                t('mandatory', lang): t('yes', lang) if ms.mandatory else t('no', lang)
            })
        pd.DataFrame(milestone_rows).to_excel(writer, sheet_name=t('milestones', lang), index=False)
    
    buffer.seek(0)
    return buffer.getvalue()

# =========================================
# MULTILINGUAL UI COMPONENTS
# =========================================

def show_instructions(title_key: str, text_key: str, expanded: bool = True):
    """Show instructions in current language"""
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    title = t(title_key, lang)
    text = t(text_key, lang)
    
    with st.expander(f"ℹ️ {title} — {t('instructions', lang)}", expanded=expanded):
        st.markdown(text)

def hermes_header():
    """Header with language selector"""
    project = st.session_state.hermes_project
    lang = project.master_data.language
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.image("https://via.placeholder.com/200x60/0055A4/ffffff?text=HERMES", width=200)
    
    with col2:
        st.title("HERMES 2022 — Project Management Assistant")
        st.caption("Multilingual tool demonstrating HERMES concepts")
    
    with col3:
        # Language selector
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

# =========================================
# MULTILINGUAL UI VIEWS
# =========================================

def project_dashboard():
    """Multilingual Dashboard"""
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
    """Multilingual Project Initialization"""
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
                
                # Create milestones
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

# Weitere UI-Komponenten (results_management, enhanced_documents_center, etc.)
# würden ähnlich internationalisiert werden...

# =========================================
# MULTILINGUAL MAIN NAVIGATION
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
    
    # Navigation mapping - hier würden alle Views eingebunden werden
    if menu == "dashboard":
        project_dashboard()
    elif menu == "project_initialization":
        enhanced_project_initialization()
    elif menu == "results_management":
        # results_management() - würde ähnlich internationalisiert werden
        st.info(f"{t('results_management', lang)} - {t('coming_soon', lang)}")
    elif menu == "documents":
        # enhanced_documents_center() - würde ähnlich internationalisiert werden  
        st.info(f"{t('documents', lang)} - {t('coming_soon', lang)}")
    elif menu == "milestones":
        # enhanced_milestone_timeline() - würde ähnlich internationalisiert werden
        st.info(f"{t('milestones', lang)} - {t('coming_soon', lang)}")
    elif menu == "phase_governance":
        # phase_governance() - würde ähnlich internationalisiert werden
        st.info(f"{t('phase_governance', lang)} - {t('coming_soon', lang)}")
    elif menu == "iterations_releases":
        # enhanced_iteration_management() - würde ähnlich internationalisiert werden
        st.info(f"{t('iterations_releases', lang)} - {t('coming_soon', lang)}")
    elif menu == "budget_management":
        # enhanced_budget_management() - würde ähnlich internationalisiert werden
        st.info(f"{t('budget_management', lang)} - {t('coming_soon', lang)}")
    elif menu == "information":
        # show_hermes_info() - würde ähnlich internationalisiert werden
        st.info(f"{t('information', lang)} - {t('coming_soon', lang)}")

if __name__ == "__main__":
    main()
