"""
Core decision engine for Phantom Consensus.
Implements proposal selection, supporter filtering, and alliance detection.
"""

# Module-level constants
BETRAYAL_TROJAN_THRESHOLD = 0.60
REL_SCORE_ALLIANCE_MIN = 40
PROPOSAL_VIABILITY_MIN = 1.0
FACTION_INFILTRATOR_THRESHOLD = 0.65


def select_proposals(clean: dict, features: dict) -> list[str]:
    """Apply viability filter. Sort by viability descending.
    Fallback to highest raw priority if all filtered out.
    Return list of proposal IDs."""
    
    viability = features['viability']
    
    # Filter by viability threshold
    viable_proposals = [
        p for p in clean['proposals']
        if viability.get(p['id'], 0) >= PROPOSAL_VIABILITY_MIN
    ]
    
    # Edge case: if no proposals meet threshold, select highest priority
    if not viable_proposals:
        if clean['proposals']:
            best = max(clean['proposals'], key=lambda p: p['priority'])
            return [best['id']]
        return []
    
    # Sort by viability descending
    viable_proposals.sort(key=lambda p: viability[p['id']], reverse=True)
    
    return [p['id'] for p in viable_proposals]


def select_supporters(clean: dict, features: dict, selected_proposals: list[str]) -> list[str]:
    """Apply Trojan Horse, Infiltrator, Supporter Coherence filters.
    Sort eligible reps by influence descending.
    Fallback to lowest-max_betrayal rep if all excluded.
    Return list of rep IDs."""
    
    max_betrayal = features['max_betrayal']
    faction_risk = features['faction_risk']
    objections_by_rep = clean['objections_by_rep']
    
    eligible_reps = []
    selected_set = set(selected_proposals)
    
    for rep in clean['reps']:
        rep_id = rep['id']
        
        # Filter 1: Trojan Horse - exclude if max betrayal exceeds threshold
        if max_betrayal.get(rep_id, 0) > BETRAYAL_TROJAN_THRESHOLD:
            continue
        
        # Filter 2: Faction Infiltrator - exclude if faction betrayal risk exceeds threshold
        if faction_risk.get(rep_id, 0) > FACTION_INFILTRATOR_THRESHOLD:
            continue
        
        # Filter 3: Supporter Coherence - exclude if objects to ALL selected proposals
        rep_objected = objections_by_rep.get(rep_id, set())
        if selected_set and rep_objected.issuperset(selected_set):
            continue  # Objects to every selected proposal
        
        eligible_reps.append(rep)
    
    # Edge case: if no reps are eligible, select the one with lowest max_betrayal
    if not eligible_reps:
        if clean['reps']:
            best = min(clean['reps'], key=lambda r: max_betrayal.get(r['id'], 1.0))
            return [best['id']]
        return []
    
    # Sort by influence descending
    eligible_reps.sort(key=lambda r: r['influence'], reverse=True)
    
    return [r['id'] for r in eligible_reps]


def detect_alliances(clean: dict, features: dict) -> list[list[str]]:
    """Bidirectional rel_score check. Compare pairs where A < B alphabetically.
    Return list of [rep_a, rep_b] pairs. Return [] if no pairs qualify."""
    
    rel_scores = features['rel_scores']
    rep_ids = sorted([r['id'] for r in clean['reps']])  # Sort for deterministic output
    
    alliances = []
    
    # Check all pairs (A, B) where A < B alphabetically
    for i, rep_a in enumerate(rep_ids):
        for rep_b in rep_ids[i+1:]:
            # Both directions must meet threshold
            score_ab = rel_scores.get((rep_a, rep_b), 0)
            score_ba = rel_scores.get((rep_b, rep_a), 0)
            
            if score_ab >= REL_SCORE_ALLIANCE_MIN and score_ba >= REL_SCORE_ALLIANCE_MIN:
                alliances.append([rep_a, rep_b])
    
    return alliances


def run_engine(clean: dict, features: dict) -> dict:
    """Run all three selection functions. Return result dict with keys:
    'proposals' (list[str]), 'supporting_reps' (list[str]), 'alliances' (list[list[str]])."""
    
    proposals = select_proposals(clean, features)
    supporting_reps = select_supporters(clean, features, proposals)
    alliances = detect_alliances(clean, features)
    
    return {
        'proposals': proposals,
        'supporting_reps': supporting_reps,
        'alliances': alliances
    }
