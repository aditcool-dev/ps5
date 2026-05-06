# Phantom Consensus — Strategic Approach

## Strategic Decision Framework

We model Phantom Consensus as a **risk-weighted optimization problem**, not a simple ranking problem. The core insight is that raw scores lie: a representative with influence=98 and betrayal_prob=0.95 is worth less than a representative with influence=60 and betrayal_prob=0.05.

Our approach uses three defensive layers:

1. **Data Sanitization** — Normalize IDs, clamp values, remove ghost references, handle duplicates
2. **Feature Engineering** — Compute risk-adjusted scores that capture hidden threats
3. **Strategic Filtering** — Apply threshold-based filters to exclude Trojan Horses, Poison Pills, False Friends, and Faction Infiltrators

## Key Formulas

### Relationship Score
```
relationship_score(A → B) = trust(A→B) × (1 - betrayal_prob(A→B))
```
This captures the **real reliability** of a connection. High trust with high betrayal probability yields a low score, exposing False Friends.

### Objection Weight
```
objection_weight(proposal) = Σ (severity_i × influence_i) for each objector i
```
Weights objections by the objector's influence, making powerful opponents more significant.

### Controversy Score
```
controversy(proposal) = objection_weight(proposal) / (10 × 100 × num_valid_reps)
```
Normalizes objection weight to [0, 1] range for comparison across different-sized datasets.

### Proposal Viability
```
proposal_viability(proposal) = priority × (1 - controversy)
```
A Poison Pill (high priority + near-total objection) will have controversy ≈ 1, making viability ≈ 0.

### Faction Betrayal Risk
```
faction_betrayal_risk(R) = average(betrayal_prob(R → M)) for M in same faction, M ≠ R
```
Identifies Faction Infiltrators who betray their own faction members. Missing relation pairs default to 0.

## Threshold Justification

### BETRAYAL_TROJAN_THRESHOLD = 0.60
Catches representatives with max outgoing betrayal > 60%. This threshold is calibrated to exclude test patterns with betrayal_prob of 0.85, 0.90, and 0.95 while not being overly conservative (0.40 would catch too many legitimate cases).

### REL_SCORE_ALLIANCE_MIN = 40
Both directions must have relationship_score ≥ 40 for an alliance. This ensures meaningful bidirectional trust. Example: trust=90 × (1-0.85) = 13.5 → NOT allied (False Friend). But trust=80 × (1-0.1) = 72 → allied.

### PROPOSAL_VIABILITY_MIN = 1.0
Minimum viability score to include a proposal. Stops Poison Pills where priority=10 but controversy=1.0 yields viability=0.

### FACTION_INFILTRATOR_THRESHOLD = 0.65
Average betrayal toward own faction members > 65% flags an infiltrator. This catches representatives who appear loyal but systematically betray their faction.

## Trap Handling

### Trojan Horse
**Pattern**: Representative with high influence but betrayal_prob > 0.60 toward key allies.  
**Defense**: `max_betrayal` filter in supporter selection excludes any rep with max outgoing betrayal > threshold.

### Poison Pill
**Pattern**: Proposal with high priority but near-universal objection.  
**Defense**: `proposal_viability` formula multiplies priority by (1 - controversy), naturally filtering out poisoned proposals.

### False Friend
**Pattern**: Asymmetric trust — A trusts B (trust=90, betrayal=0.1) but B betrays A (trust=30, betrayal=0.85).  
**Defense**: Alliance detection requires **bidirectional** relationship_score ≥ 40. The B→A score will be low, preventing alliance formation.

### Faction Infiltrator
**Pattern**: Representative who appears to be a faction member but has high average betrayal toward own faction.  
**Defense**: `faction_betrayal_risk` computation identifies these patterns and excludes them from supporters.

### Ghost Sponsor
**Pattern**: Proposal references a sponsor ID that doesn't exist in representatives data.  
**Defense**: During proposal sanitization, we check `sponsor_id in valid_rep_ids` and drop proposals with ghost sponsors.

### Complete Rivalry
**Pattern**: No pair of representatives meets the bidirectional alliance threshold.  
**Defense**: Alliance detection naturally returns `[]` without crashing or fabricating pairs.

### Minimum Viable
**Pattern**: Only 1 valid representative and 1 valid proposal after sanitization.  
**Defense**: Edge case fallbacks ensure we always output at least 1 proposal and 1 supporter, selecting the best available option.

### Cascading Betrayal
**Pattern**: Chain of betrayals where A betrays B, B betrays C, creating instability.  
**Defense**: Using `relationship_score = trust × (1 - betrayal_prob)` naturally breaks betrayal chains by lowering scores for high-betrayal connections.

## Data Cleaning Strategy

### ID Normalization
All IDs are normalized using `.strip().lower()` to handle mixed casing ("REP_001" → "rep_001") and whitespace (" rep_004" → "rep_004").

### Clamping
- `influence`: clamp to [0, 100], default to 50 on null
- `trust`: clamp to [0, 100], default to 0 on null or empty string
- `severity`: clamp to [0, 10], default to 1 on null, **drop entire record** on non-numeric string
- `betrayal_prob`: clamp to [0.0, 1.0]

### Ghost Removal
Cross-file referential integrity checks:
- Proposals: drop if sponsor not in valid_rep_ids
- Objections: drop if rep_id or proposal_id not in valid sets
- Relations: drop if from or to not in valid_rep_ids

### Deduplication Rules
- **Representatives**: Keep first occurrence of each normalized ID
- **Proposals**: On duplicate ID, keep the one with higher priority; if tied, keep first
- **Objections**: Keep first `(rep_id, proposal_id)` pair; drop subsequent duplicates
- **Relations**: Keep first `(from_id, to_id)` pair; drop subsequent duplicates

### Dirty CSV Handling
Each row in relations.csv is wrapped in try/except. Malformed rows are skipped silently without aborting the entire file parse.
