# v0.18 Queue Protocol

Daily batches are replayed with no intake time. Capacity uses development all-calendar-day valid closure counts: C25=0, C50=62, C75=80. C25 is `NONREVIEWING_SCENARIO` and is not used for a positive utility claim.

Q0 is date-resolution FIFO; Q1 prioritizes prior 90-day history; Q2 uses the frozen selected score. Outcome-free SHA-256 tie tokens provide reproducibility but are not actual arrival order. Outputs are simulated time-to-review, never repair completion or staffing effects.
