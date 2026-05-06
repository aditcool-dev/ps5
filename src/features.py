"""
Feature engineering module for Phantom Consensus Engine.
Computes relationship scores, betrayal metrics, objection weights, and proposal viability.
"""
from collections import defaultdict


def compute_relationship_scores(clean: dict) -> dict:
    """Returns dict: (from_id, to_id) -> float relationship_score."""
    rel_scores = {}
    for rel in clean['relations']:
        from_id = rel['from']
        to_id = rel['to']
        trust = rel['trust']
        betrayal_prob = rel['betrayal_prob']
        
        # Formula: relationship_score = trust × (1 - betrayal_prob)
        score = trust * (1 - betrayal_prob)
        rel_scores[(from_id, to_id)] = score
    
    return rel_scores


def compute_max_betrayal(clean: dict) -> dict:
    """Returns dict: rep_id -> float max outgoing betrayal_prob.
    Default 0 for reps with no outgoing relations."""
    max_betrayal = defaultdict(float)
    
    for rel in clean['relations']:
        from_id = rel['from']
        betrayal_prob = rel['betrayal_prob']
        max_betrayal[from_id] = max(max_betrayal[from_id], betrayal_prob)
    
    # Ensure all reps have an entry (default 0 for those with no outgoing relations)
    for rep in clean['reps']:
        if rep['id'] not in max_betrayal:
            max_betrayal[rep['id']] = 0.0
    
    return dict(max_betrayal)


def compute_faction_betrayal_risk(clean: dict) -> dict:
    """Returns dict: rep_id -> float avg betrayal toward own faction members.
    Use 0 for missing relation pairs. Default 0 if sole faction member."""
    
    # Build faction membership map
    faction_members = defaultdict(set)
    for rep in clean['reps']:
        faction_members[rep['faction']].add(rep['id'])
    
    # Build relation lookup
    rel_map = clean['rel_map']
    
    faction_risk = {}
    for rep in clean['reps']:
        rep_id = rep['id']
        faction = rep['faction']
        
        # Get other members of same faction
        same_faction = faction_members[faction] - {rep_id}
        
        if not same_faction:
            # Sole member of faction
            faction_risk[rep_id] = 0.0
            continue
        
        # Compute average betrayal toward faction members
        betrayal_probs = []
        for member_id in same_faction:
            pair = (rep_id, member_id)
            if pair in rel_map:
                betrayal_probs.append(rel_map[pair]['betrayal_prob'])
            else:
                betrayal_probs.append(0.0)  # Missing relation defaults to 0
        
        faction_risk[rep_id] = sum(betrayal_probs) / len(betrayal_probs)
    
    return faction_risk


def compute_objection_weights(clean: dict) -> dict:
    """Returns dict: proposal_id -> float total weighted objection."""
    objection_weights = defaultdict(float)
    
    for obj in clean['objections']:
        proposal_id = obj['proposal_id']
        rep_id = obj['rep_id']
        severity = obj['severity']
        influence = clean['rep_influence_map'].get(rep_id, 50)
        
        # Formula: objection_weight = sum(severity × influence)
        objection_weights[proposal_id] += severity * influence
    
    return dict(objection_weights)


def compute_proposal_viability(clean: dict, objection_weights: dict) -> dict:
    """Returns dict: proposal_id -> float viability score."""
    num_valid_reps = len(clean['reps'])
    max_possible_weight = 10 * 100 * max(num_valid_reps, 1)
    
    viability = {}
    for proposal in clean['proposals']:
        prop_id = proposal['id']
        priority = proposal['priority']
        obj_weight = objection_weights.get(prop_id, 0)
        
        # Formula: controversy = objection_weight / (10 × 100 × num_reps)
        controversy = obj_weight / max_possible_weight
        
        # Formula: viability = priority × (1 - controversy)
        viability[prop_id] = priority * (1 - controversy)
    
    return viability


def compute_all_features(clean: dict) -> dict:
    """Calls all feature functions. Returns dict with keys:
    'rel_scores', 'max_betrayal', 'faction_risk', 'objection_weights', 'viability'."""
    
    objection_weights = compute_objection_weights(clean)
    
    return {
        'rel_scores': compute_relationship_scores(clean),
        'max_betrayal': compute_max_betrayal(clean),
        'faction_risk': compute_faction_betrayal_risk(clean),
        'objection_weights': objection_weights,
        'viability': compute_proposal_viability(clean, objection_weights)
    }
