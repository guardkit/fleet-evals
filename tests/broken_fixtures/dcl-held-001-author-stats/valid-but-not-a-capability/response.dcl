language dcl 1.0

// Valid DCL, but NOT a capability: it compiles ok:true yet carries no
// `capability` block, so it must FAIL the structural floor (never the compile
// gate). Proves the floor catches an empty-but-valid technicality.
actor Operator is human

shape Query {
}
