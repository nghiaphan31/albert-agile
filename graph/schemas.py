"""Schémas Pydantic pour sorties structurées des agents (spec III.5)."""

from pydantic import BaseModel, Field


class EpicOutput(BaseModel):
    """Epic produit par R-0 (Business Analyst)."""
    title: str = Field(description="Titre de l'Epic")
    description: str = Field(description="Description, cahier des charges")
    acceptance_criteria: list[str] = Field(default_factory=list, description="Critères d'acceptation")


class ArchitectureOutput(BaseModel):
    """Architecture + DoD produit par R-2 (System Architect)."""
    summary: str = Field(description="Résumé de l'architecture")
    dod_criteria: list[str] = Field(default_factory=list, description="Definition of Done")
    contradiction_detected: bool = Field(default=False, description="True si contradiction L18 entre RAG/Backlog/Architecture")
    contradiction_sources: list[str] = Field(default_factory=list, description="Sources en conflit si contradiction_detected")


class SprintBacklogOutput(BaseModel):
    """Sprint Backlog produit par R-3 (Scrum Master)."""
    tickets: list[dict] = Field(default_factory=list, description="Liste des tickets")
