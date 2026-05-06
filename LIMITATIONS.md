# Phantom Consensus — Known Limitations

## Threshold Calibration

- **Fixed constants**: All thresholds (BETRAYAL_TROJAN_THRESHOLD=0.60, REL_SCORE_ALLIANCE_MIN=40, etc.) are fixed constants calibrated to the problem description, not learned from data.
- **Dataset sensitivity**: Different datasets with different betrayal distributions may require threshold adjustment. For example, a dataset where typical betrayal_prob values are 0.3-0.4 might need a lower threshold than 0.60.
- **No adaptive thresholds**: The engine does not adjust thresholds based on the distribution of values in the input data.

## Alliance Modeling

- **Pairwise only**: Alliance detection uses pairwise comparison only. Transitive alliances (A-B-C forming a coalition) are not modeled.
- **No multi-party coalitions**: The engine cannot detect or represent alliances involving more than 2 representatives.
- **Static relationships**: Relationships are treated as static. The `last_interaction` field is parsed but not used to model relationship decay or evolution over time.

## Objection Modeling

- **Additive objections**: Objection weight treats all objections as additive without modeling coalition dynamics or strategic objection patterns.
- **No objection clustering**: The engine does not detect coordinated objection campaigns where multiple representatives from the same faction object together.
- **Severity interpretation**: Severity values are treated as linear weights, but in reality, the difference between severity 9 and 10 might not be the same as between 1 and 2.

## Proposal Interdependencies

- **Independent proposals**: The engine does not model proposal interdependencies. Passing proposal P1 might affect the viability of proposal P2 in reality, but this is not captured.
- **No proposal conflicts**: Mutually exclusive proposals (e.g., two different approaches to the same problem) are not detected or handled specially.
- **No proposal synergies**: Proposals that work better together are not identified or prioritized as a bundle.

## Faction Dynamics

- **Simple averaging**: `faction_betrayal_risk` uses a simple average, which may be skewed by small factions (e.g., a 2-person faction where one betrays the other).
- **No faction power modeling**: The engine does not model faction-level power dynamics or faction size effects on consensus.
- **Rivalry field unused**: The `rivalry` field is parsed and stored but not used in any formula in this version. Future versions could incorporate rivalry into alliance detection or supporter selection.

## Scalability

- **O(n²) alliance detection**: Alliance detection compares all pairs of representatives, which is O(n²). For very large datasets (1000+ representatives), this could become slow.
- **In-memory processing**: All data is loaded into memory. For extremely large datasets (millions of records), this could cause memory issues.
- **No incremental updates**: The engine must reprocess all data on every run. It cannot handle incremental updates (e.g., adding one new proposal without reprocessing everything).

## Data Quality

- **Garbage in, garbage out**: While the sanitization pipeline handles many dirty data patterns, it cannot detect or correct fundamentally incorrect data (e.g., a representative's influence value that is technically valid but factually wrong).
- **No anomaly detection**: The engine does not flag suspicious patterns like a representative with influence=100 but no outgoing relations, which might indicate data quality issues.
- **No confidence scores**: The engine does not provide confidence scores or uncertainty estimates for its decisions.

## Edge Cases

- **Minimum viable fallbacks**: When all proposals or all representatives are excluded by filters, the engine falls back to selecting the "least bad" option. This ensures valid output but may not represent a true consensus.
- **Empty alliances**: When no alliances are detected (Complete Rivalry scenario), the output contains an empty alliances array. This is correct behavior but might be unexpected for users who assume alliances always exist.

## Strategic Limitations

- **No game theory**: The engine does not model strategic behavior (e.g., representatives lying about their objections to manipulate outcomes).
- **No temporal dynamics**: The engine treats all data as a snapshot. It cannot model how consensus might evolve over multiple rounds of negotiation.
- **No external factors**: The engine only considers the four input files. External factors like public opinion, resource constraints, or legal requirements are not modeled.

## Future Improvements

Potential enhancements that are out of scope for this version:

1. **Adaptive thresholds**: Learn optimal thresholds from historical consensus outcomes
2. **Coalition detection**: Use graph community detection algorithms to find multi-party coalitions
3. **Proposal bundling**: Identify and recommend proposal packages that work well together
4. **Temporal modeling**: Track relationship evolution over time using `last_interaction` dates
5. **Confidence scoring**: Provide uncertainty estimates for each decision
6. **Interactive mode**: Allow users to adjust thresholds and see how results change
7. **Explanation generation**: Provide natural language explanations for why each proposal/representative was included or excluded
