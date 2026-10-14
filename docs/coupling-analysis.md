# Ordering, permutation, and cycle analysis

The legitimate order is the DPs' causal construction order:

`DP1 hard policy → DP2 ownership → DP3 identity/fencing → DP4 semantic/backend
boundary → DP5 EVENT/STATE/EFFECT → DP6 recovery accounting → DP7 consumed
watermark → DP8 materialization/readback → DP9 EFFECT barrier → DP10 IPC seam →
DP11 Host/link health → DP12 restart/rebind → DP13 replaceable reference
backend profile`.

The corresponding FR order is FR1 through FR13 in `fr-set.md`.  It is
semantically legitimate: each later responsibility consumes contracts already
established by earlier ones.  The matrix has no X above its diagonal in this
order, so it is lower triangular, not diagonal.  It is therefore DECOUPLED,
not UNCOUPLED.

The preserved graph input is `dependency-graph.json` / `.dot`.  A simple
topological/SCC check over that graph returns 13 singleton SCCs, zero cycles,
and the ordering above.  No reverse dependency violates the proposed design
sequence.  The graph was checked independently from the CSV by rebuilding
edges from each row's nonzero cells and verifying that every dependency points
to the same or an earlier DP column.

This is not arbitrary row/column shuffling: the order follows D072's explicit
authority boundaries and causal flow from Windows admission through ownership,
semantic proposal, materialization, terminal accounting, and recovery.
