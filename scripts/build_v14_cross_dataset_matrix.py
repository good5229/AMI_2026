#!/usr/bin/env python3
"""Build an aggregate mechanism transfer matrix without row-level evidence."""
from v14_common import CLAIM, REPORTS, read_csv, write_csv


def main() -> None:
    specs = [("London", "v14_london_results.csv"), ("CoDEx-VFD", "v14_codex_vfd_results.csv"), ("SustDataED2", "v14_sustdata_results.csv")]
    rows = []
    for dataset, name in specs:
        values = read_csv(REPORTS / name)
        evaluated = [x for x in values if x.get("status", "").startswith("EVALUATED")]
        status = "EVALUATED" if evaluated else values[0]["status"]
        roles = {x.get("role", "") for x in values}
        positive = sum(x.get("actual_label") == "1" for x in evaluated)
        escalated = sum(x.get("pmc_prediction") == "1" for x in evaluated)
        for pmc in range(1, 6):
            transferable = "NOT_EVALUATED"
            mechanism_status = status
            if dataset == "CoDEx-VFD" and evaluated:
                if pmc == 1:
                    mechanism_status = "SURROGATE_ONLY"
                    transferable = "SURROGATE_ONLY_NON_TRANSFERABLE"
                elif pmc == 3:
                    mechanism_status = "NOT_AVAILABLE"
                    transferable = "NOT_AVAILABLE_TWO_MEASURED_CHANNELS"
                else:
                    mechanism_status = "NOT_REPLICATED"
                    transferable = f"NOT_REPLICATED_FROZEN_COMPOSITE_{escalated}_OF_{positive}_POSITIVE_RUNS_ESCALATED"
            elif dataset == "SustDataED2" and evaluated:
                if pmc == 3:
                    mechanism_status = "N/A"
                    transferable = "N/A_SINGLE_PHASE_AGGREGATE"
                else:
                    mechanism_status = "INCONCLUSIVE"
                    transferable = f"INCONCLUSIVE_COMPOSITE_{escalated}_OF_{len(evaluated)}_CLUSTERS_ESCALATED"
            rows.append({"dataset": dataset, "mechanism": f"PMC-{pmc}", "status": mechanism_status,
                         "transfer_conclusion": transferable, "independent_units": len(evaluated),
                         "role": ";".join(sorted(roles)), "claim_boundary": CLAIM})
    write_csv(REPORTS / "v14_cross_dataset_mechanism_matrix.csv",
              ["dataset", "mechanism", "status", "transfer_conclusion", "independent_units", "role", "claim_boundary"], rows)
    print("v0.14 cross-dataset mechanism matrix built")


if __name__ == "__main__":
    main()
