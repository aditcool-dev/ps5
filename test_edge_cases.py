#!/usr/bin/env python3
"""
Test script to verify edge case handling
"""
import json
import os

def test_output_format():
    """Verify output JSON format matches specification"""
    with open("output/consensus_output.json") as f:
        output = json.load(f)
    
    print("Testing output format...")
    
    # Check structure
    assert "final_agreement" in output, "Missing final_agreement"
    assert "proposals" in output["final_agreement"], "Missing proposals"
    assert "supporting_reps" in output["final_agreement"], "Missing supporting_reps"
    assert "alliances" in output, "Missing alliances"
    
    # Check types
    assert isinstance(output["final_agreement"]["proposals"], list), "proposals must be list"
    assert isinstance(output["final_agreement"]["supporting_reps"], list), "supporting_reps must be list"
    assert isinstance(output["alliances"], list), "alliances must be list"
    
    # Check minimum requirements
    assert len(output["final_agreement"]["proposals"]) >= 1, "Must have at least 1 proposal"
    assert len(output["final_agreement"]["supporting_reps"]) >= 1, "Must have at least 1 supporting rep"
    
    # Check no duplicates
    proposals = output["final_agreement"]["proposals"]
    assert len(proposals) == len(set(proposals)), "Proposals must not have duplicates"
    
    reps = output["final_agreement"]["supporting_reps"]
    assert len(reps) == len(set(reps)), "Supporting reps must not have duplicates"
    
    # Check alliance format
    for alliance in output["alliances"]:
        assert isinstance(alliance, list), "Each alliance must be a list"
        assert len(alliance) == 2, "Each alliance must have exactly 2 members"
        assert alliance[0] != alliance[1], "Alliance members must be distinct"
    
    print("✅ Output format is valid")
    return True

def test_dirty_data_handling():
    """Verify dirty data patterns were handled correctly"""
    from src.loader import load_all
    from src.sanitizer import sanitize_all
    
    print("\nTesting dirty data handling...")
    
    raw = load_all("data/")
    clean = sanitize_all(raw)
    
    # Check ID normalization
    rep_ids = [r['id'] for r in clean['reps']]
    assert 'rep_001' in rep_ids, "rep_001 should exist"
    assert 'REP_001' not in rep_ids, "REP_001 should be normalized to rep_001"
    assert ' rep_004' not in rep_ids, "Leading space should be stripped"
    
    # Check deduplication (only 6 unique reps after normalization)
    assert len(rep_ids) == 6, f"Should have 6 reps after deduplication, got {len(rep_ids)}"
    
    # Check influence sanitization
    rep_map = {r['id']: r for r in clean['reps']}
    assert rep_map['rep_002']['influence'] == 70.0, "String '70' should be cast to float"
    assert rep_map['rep_004']['influence'] == 50.0, "Null influence should default to 50"
    assert rep_map['rep_005']['influence'] == 100.0, "Influence 150 should be clamped to 100"
    
    # Check ghost sponsor removal
    prop_ids = [p['id'] for p in clean['proposals']]
    assert 'prop_005' not in prop_ids, "Ghost sponsor proposal should be dropped"
    
    # Check proposal deduplication (prop_003 appears twice, keep higher priority)
    prop_map = {p['id']: p for p in clean['proposals']}
    assert prop_map['prop_003']['priority'] == 9.5, "Should keep higher priority (9.5 not 7)"
    
    # Check objection severity handling
    # "high" severity should be dropped, so rep_001 should not object to prop_002
    assert 'prop_002' not in clean['objections_by_rep'].get('rep_001', set()), \
        "Non-numeric severity 'high' should drop entire objection"
    
    # Check severity clamping
    objections = {(o['rep_id'], o['proposal_id']): o for o in clean['objections']}
    if ('rep_001', 'prop_004') in objections:
        assert objections[('rep_001', 'prop_004')]['severity'] == 0, \
            "Negative severity should be clamped to 0"
    
    # Check relations sanitization
    rel_map = clean['rel_map']
    # Empty trust should default to 0
    if ('rep_002', 'rep_003') in rel_map:
        assert rel_map[('rep_002', 'rep_003')]['trust'] == 0, \
            "Empty string trust should default to 0"
    
    # Betrayal prob > 1.0 should be clamped
    if ('rep_005', 'rep_006') in rel_map:
        assert rel_map[('rep_005', 'rep_006')]['betrayal_prob'] == 1.0, \
            "Betrayal prob 1.5 should be clamped to 1.0"
    
    print("✅ Dirty data handling is correct")
    return True

def test_trojan_horse_detection():
    """Verify Trojan Horse representatives are excluded"""
    from src.loader import load_all
    from src.sanitizer import sanitize_all
    from src.features import compute_all_features
    from src.engine import run_engine
    
    print("\nTesting Trojan Horse detection...")
    
    raw = load_all("data/")
    clean = sanitize_all(raw)
    features = compute_all_features(clean)
    result = run_engine(clean, features)
    
    # rep_001 has max_betrayal=0.65 > 0.60 threshold
    assert 'rep_001' not in result['supporting_reps'], \
        "rep_001 should be excluded (Trojan Horse: max_betrayal=0.65)"
    
    # rep_005 has max_betrayal=1.00 > 0.60 threshold
    assert 'rep_005' not in result['supporting_reps'], \
        "rep_005 should be excluded (Trojan Horse: max_betrayal=1.00)"
    
    # rep_006 has max_betrayal=0.80 > 0.60 threshold
    assert 'rep_006' not in result['supporting_reps'], \
        "rep_006 should be excluded (Trojan Horse: max_betrayal=0.80)"
    
    print("✅ Trojan Horse detection working correctly")
    return True

def test_alliance_detection():
    """Verify bidirectional alliance detection"""
    from src.loader import load_all
    from src.sanitizer import sanitize_all
    from src.features import compute_all_features
    from src.engine import run_engine
    
    print("\nTesting alliance detection...")
    
    raw = load_all("data/")
    clean = sanitize_all(raw)
    features = compute_all_features(clean)
    result = run_engine(clean, features)
    
    # rep_001 ↔ rep_004: both directions ≥ 40
    assert ['rep_001', 'rep_004'] in result['alliances'], \
        "rep_001 ↔ rep_004 should be an alliance (scores: 80.8, 88.2)"
    
    # rep_002 ↔ rep_005: both directions ≥ 40
    assert ['rep_002', 'rep_005'] in result['alliances'], \
        "rep_002 ↔ rep_005 should be an alliance (scores: 56.2, 68.0)"
    
    # rep_001 ↔ rep_006: one direction < 40 (False Friend)
    assert ['rep_001', 'rep_006'] not in result['alliances'], \
        "rep_001 ↔ rep_006 should NOT be an alliance (False Friend: 63.0, 22.5)"
    
    print("✅ Alliance detection working correctly")
    return True

def test_proposal_viability():
    """Verify proposal viability calculation"""
    from src.loader import load_all
    from src.sanitizer import sanitize_all
    from src.features import compute_all_features
    
    print("\nTesting proposal viability...")
    
    raw = load_all("data/")
    clean = sanitize_all(raw)
    features = compute_all_features(clean)
    
    viability = features['viability']
    
    # prop_002 has no objections, should have viability = priority
    assert abs(viability['prop_002'] - 10.0) < 0.01, \
        f"prop_002 should have viability ≈ 10.0, got {viability['prop_002']}"
    
    # All proposals should have viability > 0
    for prop_id, v in viability.items():
        assert v > 0, f"{prop_id} has viability {v} <= 0"
    
    print("✅ Proposal viability calculation correct")
    return True

def main():
    print("=" * 70)
    print("EDGE CASE TESTING")
    print("=" * 70)
    
    try:
        test_output_format()
        test_dirty_data_handling()
        test_trojan_horse_detection()
        test_alliance_detection()
        test_proposal_viability()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
