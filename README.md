Current state of affairs: 

nin: uses less memory, but takes 24s to run on n=8.

old_nin: uses more memory, but takes 10s to run on n=8.

The underlying algorithm is the same, supposedly this discrepancy is because is_general_position gets called twice as many times in nin compared to old_nin, but this should not be the case, and I can't figure out why this happens.
