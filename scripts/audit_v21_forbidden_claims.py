#!/usr/bin/env python3
import re
from pathlib import Path

from v21_submission_lib import REPORT, ROOT, SUBMISSION

PATTERNS = [
    r"AMI만으로.*고장을 정확히 진단", r"실제 고장 정확도", r"고장 확률", r"확정 고장",
    r"민원 감소율", r"비용 절감액", r"인력 절감", r"처리시간 단축 실증",
    r"fault accuracy", r"fault probability", r"confirmed fault", r"cost savings", r"staff reduction",
]
QUALIFIERS = ["금지", "아니", "않", "없", "미산정", "불가", "NOT", "not", "no ", "unsupported", "질문"]


def main():
    files = list(SUBMISSION.glob("*.md")) + list(REPORT.glob("*.md")) + [
        ROOT / "lightguard_app" / "README.md",
        ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "submission_readiness_card.dart",
        ROOT / "lightguard_app" / "docs" / "v21_submission_readiness.md",
    ]
    violations = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        prohibited_policy_block = False
        for number, line in enumerate(text.splitlines(), 1):
            if line.startswith("## "):
                prohibited_policy_block = "금지" in line or "prohibited" in line.lower()
            qualified = prohibited_policy_block or any(q.lower() in line.lower() for q in QUALIFIERS)
            if any(re.search(pattern, line, re.I) for pattern in PATTERNS) and not qualified:
                violations.append(f"{path.relative_to(ROOT)}:{number}")
    assert not violations, "unqualified forbidden claims: " + ", ".join(violations)
    print(f"v0.21 forbidden-claim scan: PASS ({len(files)} files)")


if __name__ == "__main__":
    main()
