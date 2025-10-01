# hermes_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from enum import Enum

app = FastAPI(
    title="HERMES 2022 Project API",
    description="Backend API für die HERMES Projektmanagement App",
    version="1.0.0"
)

# Temporäre In-Memory "Datenbank" - später ersetzen wir durch PostgreSQL
projects_db = {}

# Enums für bessere Type-Safety
class ProjectApproach(str, Enum):
    CLASSICAL = "classical"
    AGILE = "agile"

class ProjectSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class ProjectLanguage(str, Enum):
    EN = "en"
    DE = "de"

class ResultStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"

class DocumentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Pydantic Models - kompatibel mit deinen Dataclasses!
class ProjectMasterData(BaseModel):
    project_name: str = ""
    client: str = ""
    project_manager: str = ""
    user_representative: str = ""
    start_date: str = ""
    budget: float = 0.0
    approach: ProjectApproach = ProjectApproach.CLASSICAL
    project_size: ProjectSize = ProjectSize.MEDIUM
    language: ProjectLanguage = ProjectLanguage.EN

class PhaseResult(BaseModel):
    name: str
    description: str = ""
    status: ResultStatus = ResultStatus.NOT_STARTED
    approval_required: bool = False
    approval_date: str = ""
    responsible_role: str = ""

class ProjectPhase(BaseModel):
    name: str
    results: Dict[str, PhaseResult] = {}
    required_documents: List[str] = []
    checklist_results: Dict[str, bool] = {}
    status: str = "not_started"
    start_date: str = ""
    end_date: str = ""

class HermesDocument(BaseModel):
    name: str
    responsible: str = ""
    status: DocumentStatus = DocumentStatus.NOT_STARTED
    required: bool = True
    linked_result: str = ""
    content: str = ""

class HermesMilestone(BaseModel):
    name: str
    phase: str
    date: str = ""
    status: str = "planned"
    mandatory: bool = True

class Iteration(BaseModel):
    number: int
    name: str
    start_date: str
    end_date: str
    total_user_stories: int = 0
    completed_user_stories: int = 0
    release_candidate: bool = False
    release_approved: bool = False
    status: str = "planned"
    goals: List[str] = []

class BudgetTransaction(BaseModel):
    date: str = ""
    category: str = ""
    amount: float = 0.0
    description: str = ""
    type: str = "actual"

class HermesProject(BaseModel):
    id: Optional[str] = None
    master_data: ProjectMasterData = ProjectMasterData()
    phases: Dict[str, ProjectPhase] = {}
    documents: Dict[str, HermesDocument] = {}
    milestones: List[HermesMilestone] = []
    iterations: List[Iteration] = []
    budget_entries: List[BudgetTransaction] = []
    actual_costs: float = 0.0
    tailoring: Dict[str, Any] = {}
    current_phase: str = "initialization"
    risks: List[Dict[str, Any]] = []
    created_at: str = ""
    updated_at: str = ""

# Helper Functions
def create_default_phases() -> Dict[str, ProjectPhase]:
    """Erstellt Standard-Phasen für ein neues Projekt"""
    return {
        "initialization": ProjectPhase(name="Initialization"),
        "concept": ProjectPhase(name="Concept"),
        "implementation": ProjectPhase(name="Implementation"),
        "introduction": ProjectPhase(name="Introduction"),
        "completion": ProjectPhase(name="Completion")
    }

def create_default_documents() -> Dict[str, HermesDocument]:
    """Erstellt Standard-Dokumente"""
    default_docs = ["Project Charter", "Project Management Plan", "Solution Requirements", "Acceptance Protocol"]
    return {doc: HermesDocument(name=doc, responsible="Project Manager", required=True) for doc in default_docs}

def create_default_milestones() -> List[HermesMilestone]:
    """Erstellt Standard-Meilensteine"""
    return [
        HermesMilestone(name="Project Start", phase="initialization", mandatory=True),
        HermesMilestone(name="Implementation Decision", phase="concept", mandatory=True),
        HermesMilestone(name="Project Completed", phase="completion", mandatory=True)
    ]

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "HERMES 2022 API läuft! 🚀", 
        "version": "1.0.0",
        "endpoints": {
            "projects": "/projects",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/projects", response_model=List[HermesProject])
async def get_all_projects():
    """Gibt alle gespeicherten Projekte zurück"""
    return list(projects_db.values())

@app.post("/projects", response_model=dict)
async def create_project(project: HermesProject):
    """Erstellt ein neues HERMES Projekt"""
    project_id = str(uuid.uuid4())
    project.id = project_id
    project.created_at = datetime.now().isoformat()
    project.updated_at = datetime.now().isoformat()
    
    # Standardwerte setzen falls nicht vorhanden
    if not project.phases:
        project.phases = create_default_phases()
    if not project.documents:
        project.documents = create_default_documents()
    if not project.milestones:
        project.milestones = create_default_milestones()
    
    projects_db[project_id] = project.dict()
    return {
        "project_id": project_id, 
        "message": "Projekt erfolgreich erstellt",
        "project_name": project.master_data.project_name
    }

@app.get("/projects/{project_id}", response_model=HermesProject)
async def get_project(project_id: str):
    """Holt ein bestimmtes Projekt anhand der ID"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return projects_db[project_id]

@app.put("/projects/{project_id}", response_model=dict)
async def update_project(project_id: str, project: HermesProject):
    """Aktualisiert ein bestehendes Projekt"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    project.updated_at = datetime.now().isoformat()
    projects_db[project_id] = project.dict()
    return {
        "message": "Projekt erfolgreich aktualisiert",
        "project_name": project.master_data.project_name,
        "updated_at": project.updated_at
    }

@app.delete("/projects/{project_id}", response_model=dict)
async def delete_project(project_id: str):
    """Löscht ein Projekt"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    project_name = projects_db[project_id].get('master_data', {}).get('project_name', 'Unbekannt')
    del projects_db[project_id]
    return {"message": f"Projekt '{project_name}' erfolgreich gelöscht"}

@app.get("/projects/{project_id}/health")
async def get_project_health(project_id: str):
    """Gibt Gesundheitsstatus eines Projekts zurück"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    project = projects_db[project_id]
    
    # Einfache Health-Check Logik
    total_results = 0
    completed_results = 0
    
    for phase in project.get('phases', {}).values():
        for result in phase.get('results', {}).values():
            total_results += 1
            if result.get('status') in ['completed', 'approved']:
                completed_results += 1
    
    progress = (completed_results / total_results * 100) if total_results > 0 else 0
    
    return {
        "project_id": project_id,
        "project_name": project.get('master_data', {}).get('project_name'),
        "progress": f"{progress:.1f}%",
        "phase": project.get('current_phase', 'unknown'),
        "last_updated": project.get('updated_at')
    }

# Utility Endpoints
@app.get("/health")
async def health_check():
    """Health Check für die API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "project_count": len(projects_db),
        "version": "1.0.0"
    }

@app.get("/statistics")
async def get_statistics():
    """Gibt Statistiken über alle Projekte zurück"""
    total_projects = len(projects_db)
    classical_count = sum(1 for p in projects_db.values() 
                         if p.get('master_data', {}).get('approach') == 'classical')
    agile_count = total_projects - classical_count
    
    return {
        "total_projects": total_projects,
        "classical_projects": classical_count,
        "agile_projects": agile_count,
        "projects_by_size": {
            "small": sum(1 for p in projects_db.values() 
                        if p.get('master_data', {}).get('project_size') == 'small'),
            "medium": sum(1 for p in projects_db.values() 
                         if p.get('master_data', {}).get('project_size') == 'medium'),
            "large": sum(1 for p in projects_db.values() 
                        if p.get('master_data', {}).get('project_size') == 'large')
        }
    }

# CORS Middleware (wichtig für Streamlit)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Für Entwicklung - später einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HERMES API Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
