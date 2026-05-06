"""
Data loading module for Phantom Consensus Engine.
Loads all four input files without any value casting or sanitization.
"""
import json
import csv
from typing import List, Dict


def load_representatives(data_dir: str) -> list[dict]:
    """Read representatives.json. Return raw list of dicts. No value casting."""
    with open(f"{data_dir}representatives.json", 'r') as f:
        return json.load(f)


def load_proposals(data_dir: str) -> list[dict]:
    """Read proposals.json. Return raw list of dicts. No value casting."""
    with open(f"{data_dir}proposals.json", 'r') as f:
        return json.load(f)


def load_objections(data_dir: str) -> list[dict]:
    """Read objections.json. Return raw list of dicts. No value casting."""
    with open(f"{data_dir}objections.json", 'r') as f:
        return json.load(f)


def load_relations(data_dir: str) -> list[dict]:
    """Read relations.csv row by row using csv.DictReader.
    Each row individually wrapped in try/except.
    Return list of dicts using header row as keys. No value casting."""
    relations = []
    with open(f"{data_dir}relations.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Just store the raw row - no casting yet
                relations.append(dict(row))
            except Exception:
                # Skip malformed rows silently
                continue
    return relations


def load_all(data_dir: str) -> dict:
    """Call all four loaders. Return dict with keys:
    'representatives', 'proposals', 'objections', 'relations'."""
    return {
        'representatives': load_representatives(data_dir),
        'proposals': load_proposals(data_dir),
        'objections': load_objections(data_dir),
        'relations': load_relations(data_dir)
    }
