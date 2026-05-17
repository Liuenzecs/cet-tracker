"""Schemas for data import / export."""

from typing import Any, Dict, List

from pydantic import BaseModel


class ExportData(BaseModel):
    sessions: List[Dict[str, Any]] = []
    listening_results: List[Dict[str, Any]] = []
    reading_results: List[Dict[str, Any]] = []
    vocabulary_notes: List[Dict[str, Any]] = []
    vocabulary_entries: List[Dict[str, Any]] = []


class ImportResult(BaseModel):
    sessions_imported: int = 0
    listening_results_imported: int = 0
    reading_results_imported: int = 0
    vocabulary_notes_imported: int = 0
    vocabulary_entries_imported: int = 0
