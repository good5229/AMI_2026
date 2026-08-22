# v0.20 Queue Replay

{
  "policies": {
    "FIFO": {
      "all_cases": {
        "n": 1050,
        "median": 0.0,
        "p75": 0.0,
        "p90": 0.0,
        "p95": 0.0,
        "same_day_share": 0.9971428571428571,
        "over_1d_share": 0.0009523809523809524,
        "over_3d_share": 0.0,
        "over_7d_share": 0.0
      },
      "repeat_30d_cases": {
        "n": 36,
        "median": 0.0,
        "p75": 0.0,
        "p90": 0.0,
        "p95": 0.0,
        "same_day_share": 1.0,
        "over_1d_share": 0.0,
        "over_3d_share": 0.0,
        "over_7d_share": 0.0
      },
      "unstarted_at_horizon": 0
    },
    "FROZEN_COMMON_OPS": {
      "all_cases": {
        "n": 1050,
        "median": 0.0,
        "p75": 0.0,
        "p90": 0.0,
        "p95": 0.0,
        "same_day_share": 0.9971428571428571,
        "over_1d_share": 0.0009523809523809524,
        "over_3d_share": 0.0,
        "over_7d_share": 0.0
      },
      "repeat_30d_cases": {
        "n": 36,
        "median": 0.0,
        "p75": 0.0,
        "p90": 0.0,
        "p95": 0.0,
        "same_day_share": 1.0,
        "over_1d_share": 0.0,
        "over_3d_share": 0.0,
        "over_7d_share": 0.0
      },
      "unstarted_at_horizon": 0
    },
    "FROZEN_SIMPLE_RULE": {
      "all_cases": {
        "n": 1050,
        "median": 0.0,
        "p75": 0.0,
        "p90": 0.0,
        "p95": 0.0,
        "same_day_share": 0.9971428571428571,
        "over_1d_share": 0.0009523809523809524,
        "over_3d_share": 0.0,
        "over_7d_share": 0.0
      },
      "repeat_30d_cases": {
        "n": 36,
        "median": 0.0,
        "p75": 0.0,
        "p90": 0.0,
        "p95": 0.0,
        "same_day_share": 1.0,
        "over_1d_share": 0.0,
        "over_3d_share": 0.0,
        "over_7d_share": 0.0
      },
      "unstarted_at_horizon": 0
    }
  },
  "promotion_gate": {
    "predeclared_all_case_p90_tolerance_days": 1,
    "repeat_case_p90_must_improve": true,
    "passed": false
  },
  "work_start_grade": "WS-B",
  "capacity_interpretation": "NOT_EVALUABLE_AS_STAFFING_CAPACITY",
  "same_day_order": "NOT_SUPPORTED",
  "causal_claim": "NOT_SUPPORTED"
}

Observed daily work starts are replay slots, not staffing or true capacity. This counterfactual replay does not establish actual field-delay reduction or causality.
