"""
Data sanitization module for Phantom Consensus Engine.
Handles dirty data patterns: ID normalization, null values, clamping, deduplication, ghost references.
"""
from typing import Any, Optional
from collections import defaultdict

# Module-level constants
INFLUENCE_NULL_DEFAULT = 50
SEVERITY_NULL_DEFAULT = 1
TRUST_NULL_DEFAULT = 0


def normalize_id(raw: Any) -> Optional[str]:
    """Strip whitespace, lowercase. Return None if raw is None or empty after strip."""
    if raw is None:
        return None
    s = str(raw).strip().lower()
    return s if s else None  # Return None for empty string, not ""


def sanitize_influence(raw: Any) -> float:
    """Cast to float, clamp [0,100], default to INFLUENCE_NULL_DEFAULT on null or parse failure."""
    if raw is None:
        return INFLUENCE_NULL_DEFAULT
    try:
        val = float(raw)
        return max(0.0, min(100.0, val))
    except (ValueError, TypeError):
        return INFLUENCE_NULL_DEFAULT


def sanitize_severity(raw: Any) -> Optional[float]:
    """Return None if raw is a non-numeric string (caller drops the entire record).
    Return SEVERITY_NULL_DEFAULT (1) if raw is null.
    Clamp to [0,10] otherwise."""
    if raw is None:
        return SEVERITY_NULL_DEFAULT
    
    # Check if it's a string that's non-numeric
    if isinstance(raw, str):
        try:
            val = float(raw)
        except ValueError:
            # Non-numeric string like "high" - return None to signal drop
            return None
    else:
        try:
            val = float(raw)
        except (ValueError, TypeError):
            return None
    
    # Clamp to [0, 10]
    return max(0.0, min(10.0, val))


def sanitize_numeric(raw: Any, default: float, lo: float, hi: float) -> float:
    """Generic: cast to float, clamp [lo,hi], return default on failure or null."""
    if raw is None:
        return default
    
    # Handle empty string explicitly
    if isinstance(raw, str) and raw.strip() == "":
        return default
    
    try:
        val = float(raw)
        return max(lo, min(hi, val))
    except (ValueError, TypeError):
        return default


def sanitize_all(raw: dict) -> dict:
    """Run full sanitization pipeline. Return dict with keys:
    'reps' (list), 'proposals' (list), 'objections' (list), 'relations' (list),
    'valid_rep_ids' (set), 'valid_proposal_ids' (set),
    'rep_influence_map' (dict), 'rel_map' (dict),
    'objections_by_proposal' (dict), 'objections_by_rep' (dict)."""
    
    # Step 1: Sanitize representatives (keep first occurrence)
    seen_rep_ids = set()
    clean_reps = []
    for r in raw['representatives']:
        rep_id = normalize_id(r.get('id'))
        if rep_id is None or rep_id in seen_rep_ids:
            continue
        seen_rep_ids.add(rep_id)
        
        clean_reps.append({
            'id': rep_id,
            'name': str(r.get('name', '')),
            'faction': str(r.get('faction', '')).strip(),
            'influence': sanitize_influence(r.get('influence'))
        })
    
    valid_rep_ids = {r['id'] for r in clean_reps}
    rep_influence_map = {r['id']: r['influence'] for r in clean_reps}
    
    # Step 2: Sanitize proposals (drop ghost sponsors, deduplicate by keeping highest priority)
    proposal_dict = {}  # Use dict to track by ID, preserving insertion order
    for p in raw['proposals']:
        prop_id = normalize_id(p.get('id'))
        sponsor_id = normalize_id(p.get('sponsor'))
        
        if prop_id is None or sponsor_id is None:
            continue
        if sponsor_id not in valid_rep_ids:
            continue  # Ghost sponsor - drop proposal
        
        priority = p.get('priority', 1)
        try:
            priority = float(priority)
        except (ValueError, TypeError):
            priority = 1.0
        
        # Deduplication: keep higher priority, or first on tie
        if prop_id in proposal_dict:
            existing_priority = proposal_dict[prop_id]['priority']
            if priority > existing_priority:
                proposal_dict[prop_id] = {
                    'id': prop_id,
                    'title': str(p.get('title', '')),
                    'sponsor': sponsor_id,
                    'priority': priority
                }
            # If priority is equal or lower, keep the first (do nothing)
        else:
            proposal_dict[prop_id] = {
                'id': prop_id,
                'title': str(p.get('title', '')),
                'sponsor': sponsor_id,
                'priority': priority
            }
    
    clean_proposals = list(proposal_dict.values())
    valid_proposal_ids = {p['id'] for p in clean_proposals}
    
    # Step 3: Sanitize objections (drop ghost references, handle dirty severity, deduplicate)
    seen_objection_pairs = set()
    clean_objections = []
    objections_by_proposal = defaultdict(list)
    objections_by_rep = defaultdict(set)
    
    for o in raw['objections']:
        rep_id = normalize_id(o.get('rep_id'))
        proposal_id = normalize_id(o.get('proposal_id'))
        
        if rep_id is None or proposal_id is None:
            continue
        if rep_id not in valid_rep_ids or proposal_id not in valid_proposal_ids:
            continue  # Ghost reference
        
        # Check for duplicate (rep_id, proposal_id) pair
        pair = (rep_id, proposal_id)
        if pair in seen_objection_pairs:
            continue  # Keep first, drop duplicate
        
        severity = sanitize_severity(o.get('severity'))
        if severity is None:
            continue  # Non-numeric string severity - drop entire record
        
        seen_objection_pairs.add(pair)
        clean_obj = {
            'rep_id': rep_id,
            'proposal_id': proposal_id,
            'severity': severity
        }
        clean_objections.append(clean_obj)
        objections_by_proposal[proposal_id].append(clean_obj)
        objections_by_rep[rep_id].add(proposal_id)
    
    # Step 4: Sanitize relations (drop ghost references, handle dirty values, deduplicate)
    seen_relation_pairs = set()
    clean_relations = []
    rel_map = {}
    
    for row in raw['relations']:
        try:
            from_id = normalize_id(row.get('from'))
            to_id = normalize_id(row.get('to'))
            
            if from_id is None or to_id is None:
                continue
            if from_id not in valid_rep_ids or to_id not in valid_rep_ids:
                continue  # Ghost reference
            
            # Check for duplicate (from, to) pair
            pair = (from_id, to_id)
            if pair in seen_relation_pairs:
                continue  # Keep first, drop duplicate
            seen_relation_pairs.add(pair)
            
            # Sanitize numeric fields with explicit empty string handling
            trust = sanitize_numeric(row.get('trust'), TRUST_NULL_DEFAULT, 0, 100)
            rivalry = sanitize_numeric(row.get('rivalry'), 0, 0, 100)
            betrayal_prob = sanitize_numeric(row.get('betrayal_prob'), 0, 0.0, 1.0)
            
            clean_rel = {
                'from': from_id,
                'to': to_id,
                'trust': trust,
                'rivalry': rivalry,
                'betrayal_prob': betrayal_prob,
                'last_interaction': row.get('last_interaction', '')
            }
            clean_relations.append(clean_rel)
            rel_map[(from_id, to_id)] = clean_rel
            
        except Exception:
            # Skip malformed row silently
            continue
    
    return {
        'reps': clean_reps,
        'proposals': clean_proposals,
        'objections': clean_objections,
        'relations': clean_relations,
        'valid_rep_ids': valid_rep_ids,
        'valid_proposal_ids': valid_proposal_ids,
        'rep_influence_map': rep_influence_map,
        'rel_map': rel_map,
        'objections_by_proposal': objections_by_proposal,
        'objections_by_rep': objections_by_rep
    }
