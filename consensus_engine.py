#!/usr/bin/env python3
"""
Phantom Consensus Engine
Entry point: python consensus_engine.py

Strategic Consensus Engine for competitive hackathon.
Processes representatives, proposals, objections, and relationships
to output strategic agreements with alliance detection.
"""
from src.loader import load_all
from src.sanitizer import sanitize_all
from src.features import compute_all_features
from src.engine import run_engine
from src.formatter import format_output

DATA_DIR = "data/"
OUTPUT_DIR = "output/"
OUTPUT_PATH = f"{OUTPUT_DIR}consensus_output.json"


def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Phase 1: Load raw data
    raw = load_all(DATA_DIR)
    
    # Phase 2: Sanitize and clean
    clean = sanitize_all(raw)
    
    # Phase 3: Compute features
    features = compute_all_features(clean)
    
    # Phase 4: Run decision engine
    result = run_engine(clean, features)
    
    # Phase 5: Format and write output
    format_output(result, clean, OUTPUT_PATH)


if __name__ == "__main__":
    main()
