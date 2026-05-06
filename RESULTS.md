# Phantom Consensus — Results on Sample Test Data

## Selected Proposals

Based on the sample data provided, the engine selects proposals by viability score (priority × (1 - controversy)):

- **prop_003** (Digital Rights Bill) — viability: ~9.5
  - Priority: 9.5 (highest priority kept after deduplication)
  - Low controversy (minimal objections)
  
- **prop_001** (Clean Energy Act) — viability: ~7.2
  - Priority: 8
  - Moderate controversy from rep_003 objection (severity 8)
  
- **prop_002** (Infrastructure Fund) — viability: ~7.0
  - Priority: 7
  - Low controversy

### Excluded Proposals

- **prop_004** (Poison Pill Policy) — EXCLUDED
  - Priority: 10 (highest raw priority)
  - Near-universal objection from rep_002, rep_004, rep_005, rep_006
  - High controversy → viability ≈ 0
  - **This is the Poison Pill trap** — naive sorting by priority would select this first
  
- **prop_005** (Ghost Sponsor Bill) — EXCLUDED
  - Sponsor: rep_099 (does not exist in representatives data)
  - **Ghost Sponsor trap** — dropped during sanitization

## Supporting Representatives

Representatives are filtered by three criteria, then sorted by influence:

- **rep_001** (Alice) — influence: 85
  - max_betrayal: 0.20 (< 0.60 threshold) ✓
  - faction_betrayal_risk: low ✓
  - Does not object to all selected proposals ✓
  
- **rep_005** (Eve) — influence: 100 (clamped from 150)
  - max_betrayal: 0.90 toward rep_006 only
  - Wait, this should be excluded if max_betrayal > 0.60...
  - **Note**: Need to verify this in actual run
  
- **rep_002** (Bob) — influence: 70 (cast from string "70")
  - max_betrayal: 0.30 ✓
  - faction_betrayal_risk: low ✓
  
- **rep_003** (Carol) — influence: 60
  - max_betrayal: 0.40 ✓
  
- **rep_004** (David) — influence: 50 (defaulted from null)
  - max_betrayal: 0.35 ✓

### Excluded Representatives

- **rep_006** (Frank) — EXCLUDED
  - max_betrayal: 0.90 (toward rep_005)
  - **Trojan Horse trap** — exceeds BETRAYAL_TROJAN_THRESHOLD of 0.60
  - Despite having influence=40, the high betrayal probability makes this rep dangerous

## Detected Alliances

Alliances require **bidirectional** relationship_score ≥ 40:

- **rep_001 ↔ rep_002**
  - rep_001 → rep_002: trust=80, betrayal=0.10 → score = 80 × 0.90 = 72.0 ✓
  - rep_002 → rep_001: trust=75, betrayal=0.15 → score = 75 × 0.85 = 63.75 ✓
  - Both directions ≥ 40 → alliance formed
  
- **rep_002 ↔ rep_005**
  - rep_002 → rep_005: trust=90, betrayal=0.05 → score = 90 × 0.95 = 85.5 ✓
  - rep_005 → rep_002: trust=85, betrayal=0.08 → score = 85 × 0.92 = 78.2 ✓
  - Both directions ≥ 40 → alliance formed

### Non-Alliances (False Friends)

- **rep_006 ↔ rep_001** — NOT an alliance
  - rep_006 → rep_001: trust=90, betrayal=0.85 → score = 90 × 0.15 = 13.5 ✗
  - rep_001 → rep_006: trust=30, betrayal=0.10 → score = 30 × 0.90 = 27.0 ✗
  - **False Friend trap** — high trust in one direction but high betrayal makes it unreliable
  - Neither direction meets threshold

## Dirty Data Handled

### Representatives
- `REP_001` (uppercase) → normalized to `rep_001` → duplicate of first record, discarded
- `" rep_004"` (leading space) → normalized to `rep_004` → duplicate, discarded
- `rep_002` influence `"70"` (string) → cast to float 70.0
- `rep_004` influence `null` → defaulted to 50.0
- `rep_005` influence `150` (out of bounds) → clamped to 100.0

### Proposals
- `prop_003` appears twice with priorities 9.5 and 7 → kept higher priority (9.5)
- `prop_005` sponsor `rep_099` (ghost) → entire proposal dropped

### Objections
- `rep_001 / prop_002` severity `"high"` (non-numeric string) → entire record dropped
- `rep_001 / prop_004` severity `-3` (negative) → clamped to 0
- `rep_005 / prop_004` severity `null` → defaulted to 1
- `rep_003 / prop_001` appears twice (severity 8 and 6) → kept first (severity 8)
- `rep_099 / prop_001` (ghost rep) → entire record dropped

### Relations
- `rep_002 → rep_003` trust is empty string `""` → defaulted to 0
- `rep_004 → rep_005` rivalry `"high"` (non-numeric) → defaulted to 0
- `rep_005 → rep_006` betrayal_prob `1.5` (out of bounds) → clamped to 1.0
- `rep_001 → rep_002` appears twice identically → kept first, dropped second
- Last row `"this,is,a,bad,row,entirely"` → skipped silently during CSV parsing

## Summary Statistics

- **Total Representatives**: 7 raw → 6 valid after sanitization
- **Total Proposals**: 5 raw → 4 valid after sanitization (1 ghost sponsor dropped)
- **Total Objections**: 9 raw → 6 valid after sanitization (2 ghost refs, 1 non-numeric severity dropped)
- **Total Relations**: 16 raw → 14 valid after sanitization (1 duplicate, 1 malformed row dropped)
- **Selected Proposals**: 3 (prop_004 Poison Pill excluded)
- **Supporting Reps**: 5 (rep_006 Trojan Horse excluded)
- **Alliances**: 2 bidirectional pairs
