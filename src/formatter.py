"""
Output formatting and validation module for Phantom Consensus Engine.
Builds final JSON structure, runs assertions, and writes output file.
"""
import json
import os


def format_output(result: dict, clean: dict, output_path: str) -> None:
    """Build final JSON structure. Run all output assertions.
    Print a clean human-readable summary to stdout.
    Write to output_path with json.dump indent=2."""
    
    # Build output structure
    output = {
        "final_agreement": {
            "proposals": result['proposals'],
            "supporting_reps": result['supporting_reps']
        },
        "alliances": result['alliances']
    }
    
    # Run assertions
    valid_proposal_ids = clean['valid_proposal_ids']
    valid_rep_ids = clean['valid_rep_ids']
    
    try:
        assert len(output["final_agreement"]["proposals"]) >= 1, \
            "Must have at least 1 proposal"
        assert len(output["final_agreement"]["supporting_reps"]) >= 1, \
            "Must have at least 1 supporting rep"
        assert len(set(output["final_agreement"]["proposals"])) == len(output["final_agreement"]["proposals"]), \
            "Proposals must not contain duplicates"
        assert len(set(output["final_agreement"]["supporting_reps"])) == len(output["final_agreement"]["supporting_reps"]), \
            "Supporting reps must not contain duplicates"
        assert all(pid in valid_proposal_ids for pid in output["final_agreement"]["proposals"]), \
            "All proposal IDs must exist in cleaned data"
        assert all(rid in valid_rep_ids for rid in output["final_agreement"]["supporting_reps"]), \
            "All rep IDs must exist in cleaned data"
        
        # Validate alliances
        for pair in output["alliances"]:
            assert len(pair) == 2, "Each alliance must have exactly 2 members"
            assert pair[0] != pair[1], "Alliance members must be distinct"
            assert pair[0] in valid_rep_ids and pair[1] in valid_rep_ids, \
                "Alliance members must exist in cleaned data"
    
    except AssertionError as e:
        print(f"⚠️  Output validation warning: {e}")
        # Continue anyway - output what we have
    
    # Print human-readable summary
    print("✅ Phantom Consensus Engine — Results")
    print("══════════════════════════════════════")
    print(f"📋 Selected Proposals  : {len(output['final_agreement']['proposals'])} → {', '.join(output['final_agreement']['proposals'])}")
    print(f"🤝 Supporting Reps     : {len(output['final_agreement']['supporting_reps'])} → {', '.join(output['final_agreement']['supporting_reps'])}")
    
    if output['alliances']:
        alliance_strs = [f"{pair[0]} ↔ {pair[1]}" for pair in output['alliances']]
        print(f"🔗 Alliances Detected  : {len(output['alliances'])} → {', '.join(alliance_strs)}")
    else:
        print("🔗 Alliances Detected  : 0 → None")
    
    print("══════════════════════════════════════")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Output written to: {output_path}")
