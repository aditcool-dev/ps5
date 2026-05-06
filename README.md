# Phantom Consensus

## Team Information
- **Team Name**: Seski Boys
- **Year**: 2nd
- **All-Female Team**: No

## Architecture Overview

#### Describe your approach here. Keep it short and clear.

- **Data Cleaning**: We implemented a multi-stage sanitization pipeline that normalizes IDs (strip whitespace, lowercase), casts string numbers to floats, handles null values with domain-specific defaults (influence: 50, severity: 1, trust: 0), clamps out-of-bounds values to valid ranges, and removes ghost references through cross-file referential integrity checks. Deduplication keeps the first occurrence for representatives and relations, while proposals retain the highest priority instance. Malformed CSV rows are skipped silently without aborting the parse.

- **Alliance Detection**: We compute a relationship_score = trust × (1 - betrayal_prob) for each directed pair, capturing the real reliability of connections. Alliances require bidirectional scores ≥ 40, preventing False Friend scenarios where asymmetric trust exists. We also calculate faction_betrayal_risk as the average betrayal probability toward same-faction members, identifying infiltrators who betray their own group (threshold: 0.65).

- **Proposal Prioritization**: Rather than using raw priority scores, we compute proposal_viability = priority × (1 - controversy), where controversy = objection_weight / (10 × 100 × num_reps). Objection weight is the sum of (severity × influence) across all objectors, ensuring powerful opponents have proportional impact. This naturally filters Poison Pills—proposals with high priority but near-universal objection get low viability scores.

- **Consensus Strategy**: Our engine excludes Trojan Horse representatives (max outgoing betrayal_prob > 0.60), Faction Infiltrators (avg faction betrayal > 0.65), and representatives who object to every selected proposal. We select all proposals with viability ≥ 1.0, sorted by viability descending. Supporting representatives are filtered by the above criteria and ranked by influence. Edge case fallbacks ensure at least one proposal and one representative in all scenarios, selecting the least dangerous options when all candidates are excluded.

**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.

---

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the Engine

```bash
python consensus_engine.py
```

### Launch Dashboard

```bash
streamlit run dashboard.py
```

## Project Structure

```
phantom-consensus/
├── data/                           # Input data files
│   ├── representatives.json        # Representative profiles
│   ├── proposals.json              # Legislative proposals
│   ├── objections.json             # Objections to proposals
│   └── relations.csv               # Inter-representative relationships
├── output/
│   └── consensus_output.json       # Generated consensus (created at runtime)
├── src/                            # Core engine modules
│   ├── __init__.py                 # Package marker
│   ├── loader.py                   # Data loading (no sanitization)
│   ├── sanitizer.py                # Data cleaning pipeline
│   ├── features.py                 # Feature engineering
│   ├── engine.py                   # Decision logic
│   └── formatter.py                # Output formatting
├── consensus_engine.py             # Entry point
├── dashboard.py                    # Streamlit visualization
├── debug_analysis.py               # Debug tool
├── test_edge_cases.py              # Test suite
├── requirements.txt                # Python dependencies
├── APPROACH.md                     # Strategic approach documentation
├── RESULTS.md                      # Sample results analysis
└── LIMITATIONS.md                  # Known limitations
```

## Core Formulas

### Relationship Score
```
relationship_score(A → B) = trust(A→B) × (1 - betrayal_prob(A→B))
```
Captures real reliability of a connection. High trust with high betrayal yields low score.

### Proposal Viability
```
controversy(P) = objection_weight(P) / (10 × 100 × num_reps)
viability(P) = priority(P) × (1 - controversy(P))
```
Poison Pills (high priority + high controversy) naturally get low viability.

### Faction Betrayal Risk
```
faction_betrayal_risk(R) = avg(betrayal_prob(R → M)) for M in same faction
```
Identifies infiltrators who betray their own faction members.

## Thresholds

| Constant | Value | Purpose |
|----------|-------|---------|
| `BETRAYAL_TROJAN_THRESHOLD` | 0.60 | Exclude reps with max betrayal > 60% |
| `REL_SCORE_ALLIANCE_MIN` | 40 | Both directions must score ≥ 40 for alliance |
| `PROPOSAL_VIABILITY_MIN` | 1.0 | Minimum viability to include proposal |
| `FACTION_INFILTRATOR_THRESHOLD` | 0.65 | Exclude reps with avg faction betrayal > 65% |

## Output Format

```json
{
  "final_agreement": {
    "proposals": ["prop_002", "prop_001"],
    "supporting_reps": ["rep_003", "rep_001"]
  },
  "alliances": [
    ["rep_001", "rep_004"],
    ["rep_002", "rep_005"]
  ]
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_edge_cases.py
```

Run debug analysis:

```bash
python debug_analysis.py
```

## Dirty Data Handling

The engine handles:

- **ID normalization**: `"REP_001"` → `"rep_001"`, `" rep_004"` → `"rep_004"`
- **Type casting**: `"70"` → `70.0`
- **Null values**: `null` → default values (influence: 50, severity: 1, trust: 0)
- **Clamping**: influence [0, 100], severity [0, 10], betrayal_prob [0.0, 1.0]
- **Deduplication**: Keep first occurrence (reps, objections, relations) or highest priority (proposals)
- **Ghost references**: Drop records referencing non-existent IDs
- **Malformed CSV rows**: Skip silently without aborting parse

## Sample Results

On the provided test data:

- **Selected Proposals**: 4 (prop_002, prop_003, prop_004, prop_001)
- **Supporting Reps**: 3 (rep_003, rep_002, rep_004)
- **Alliances**: 2 (rep_001 ↔ rep_004, rep_002 ↔ rep_005)
- **Excluded Reps**: 3 Trojan Horses (rep_001, rep_005, rep_006)
- **Excluded Proposals**: 1 Ghost Sponsor (prop_005)

See [RESULTS.md](RESULTS.md) for detailed analysis.

## Strategic Approach

See [APPROACH.md](APPROACH.md) for:
- Strategic decision framework
- Formula justifications
- Threshold calibration
- Trap handling strategies
- Data cleaning pipeline

## Known Limitations

See [LIMITATIONS.md](LIMITATIONS.md) for:
- Fixed threshold constraints
- Pairwise-only alliance modeling
- No proposal interdependencies
- Scalability considerations

## Requirements

- Python 3.9+ (uses `list[str]` type hint syntax)
- pandas >= 2.0.0
- networkx >= 3.0
- streamlit >= 1.30.0
- matplotlib >= 3.7.0

## Additional Documentation

For detailed information about the implementation:
- Strategic approach: [APPROACH.md](APPROACH.md)
- Results analysis: [RESULTS.md](RESULTS.md)
- Known limitations: [LIMITATIONS.md](LIMITATIONS.md)
- Implementation summary: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
