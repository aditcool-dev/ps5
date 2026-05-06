#!/usr/bin/env python3
"""
Debug analysis script to understand the consensus engine decisions
"""
from src.loader import load_all
from src.sanitizer import sanitize_all
from src.features import compute_all_features
from src.engine import run_engine, BETRAYAL_TROJAN_THRESHOLD, FACTION_INFILTRATOR_THRESHOLD

DATA_DIR = "data/"

def main():
    # Load and sanitize
    raw = load_all(DATA_DIR)
    clean = sanitize_all(raw)
    features = compute_all_features(clean)
    
    print("=" * 70)
    print("SANITIZED REPRESENTATIVES")
    print("=" * 70)
    for rep in clean['reps']:
        print(f"{rep['id']:12} | faction: {rep['faction']:15} | influence: {rep['influence']:6.1f}")
    
    print("\n" + "=" * 70)
    print("SANITIZED PROPOSALS")
    print("=" * 70)
    for prop in clean['proposals']:
        print(f"{prop['id']:12} | sponsor: {prop['sponsor']:12} | priority: {prop['priority']:5.1f}")
    
    print("\n" + "=" * 70)
    print("PROPOSAL VIABILITY SCORES")
    print("=" * 70)
    for prop in clean['proposals']:
        prop_id = prop['id']
        viability = features['viability'].get(prop_id, 0)
        obj_weight = features['objection_weights'].get(prop_id, 0)
        print(f"{prop_id:12} | priority: {prop['priority']:5.1f} | obj_weight: {obj_weight:8.1f} | viability: {viability:6.2f}")
    
    print("\n" + "=" * 70)
    print("REPRESENTATIVE RISK SCORES")
    print("=" * 70)
    for rep in clean['reps']:
        rep_id = rep['id']
        max_betrayal = features['max_betrayal'].get(rep_id, 0)
        faction_risk = features['faction_risk'].get(rep_id, 0)
        trojan = "🚨 TROJAN" if max_betrayal > BETRAYAL_TROJAN_THRESHOLD else "✓"
        infiltrator = "🚨 INFILTRATOR" if faction_risk > FACTION_INFILTRATOR_THRESHOLD else "✓"
        print(f"{rep_id:12} | max_betrayal: {max_betrayal:4.2f} {trojan:15} | faction_risk: {faction_risk:4.2f} {infiltrator}")
    
    print("\n" + "=" * 70)
    print("OBJECTIONS BY REP")
    print("=" * 70)
    for rep_id, prop_ids in clean['objections_by_rep'].items():
        print(f"{rep_id:12} | objects to: {', '.join(sorted(prop_ids))}")
    
    print("\n" + "=" * 70)
    print("RELATIONSHIP SCORES (for alliances)")
    print("=" * 70)
    rel_scores = features['rel_scores']
    rep_ids = sorted([r['id'] for r in clean['reps']])
    for i, rep_a in enumerate(rep_ids):
        for rep_b in rep_ids[i+1:]:
            score_ab = rel_scores.get((rep_a, rep_b), 0)
            score_ba = rel_scores.get((rep_b, rep_a), 0)
            alliance = "✓ ALLIANCE" if (score_ab >= 40 and score_ba >= 40) else ""
            if score_ab > 0 or score_ba > 0:
                print(f"{rep_a} ↔ {rep_b:12} | {rep_a}→{rep_b}: {score_ab:5.1f} | {rep_b}→{rep_a}: {score_ba:5.1f} {alliance}")
    
    print("\n" + "=" * 70)
    print("FINAL DECISION")
    print("=" * 70)
    result = run_engine(clean, features)
    print(f"Selected Proposals: {result['proposals']}")
    print(f"Supporting Reps: {result['supporting_reps']}")
    print(f"Alliances: {result['alliances']}")

if __name__ == "__main__":
    main()
