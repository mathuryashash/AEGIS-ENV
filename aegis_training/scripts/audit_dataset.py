#!/usr/bin/env python3
"""
AEGIS Dataset Auditor
Usage: python scripts/audit_dataset.py <dataset.json>
Exits with code 1 if critical issues are found.
"""

import json
import sys
import random
import hashlib
from collections import Counter, defaultdict


def compute_signature(entry: dict) -> str:
    raw = (
        entry.get("worker_cot_trace", "")
        + "||"
        + entry.get("worker_output", "")
        + "||"
        + entry.get("decision", "")
        + "||"
        + entry.get("violation_type", "")
    )
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def audit(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    print("=" * 60)
    print(f"AEGIS DATASET AUDIT: {path}")
    print("=" * 60)

    # 1. Total row count
    print(f"\n[1] TOTAL ROWS: {total}")

    # 2. Label distribution
    decision_counts = Counter(d["decision"] for d in data)
    print("\n[2] LABEL DISTRIBUTION")
    all_labels = ["ALLOW", "BLOCK", "ESCALATE"]
    for label in all_labels:
        count = decision_counts.get(label, 0)
        pct = count / total * 100 if total > 0 else 0.0
        print(f"    {label:10s}: {count:5d}  ({pct:.1f}%)")

    # 3. Flag missing classes
    missing_classes = [lbl for lbl in all_labels if decision_counts.get(lbl, 0) == 0]
    if missing_classes:
        print(f"\n  *** CRITICAL: Missing label class(es): {', '.join(missing_classes)} ***")

    # 4 & 5. Signatures and duplicates
    sigs = [compute_signature(d) for d in data]
    sig_counts = Counter(sigs)
    dup_sigs = {s: c for s, c in sig_counts.items() if c > 1}
    dup_row_count = sum(c - 1 for c in dup_sigs.values())
    dup_pct = dup_row_count / total * 100 if total > 0 else 0.0

    print(f"\n[4-5] DUPLICATE ANALYSIS")
    print(f"    Duplicate rows (extra copies): {dup_row_count}  ({dup_pct:.1f}%)")
    print(f"    Unique signatures: {len(sig_counts)}")
    top5_groups = sorted(dup_sigs.values(), reverse=True)[:5]
    if top5_groups:
        print(f"    Top-5 duplicate group sizes: {top5_groups}")
    else:
        print("    No duplicate groups found.")

    # 6. Unique cot_trace and worker_output
    unique_cots = len(set(d["worker_cot_trace"] for d in data))
    unique_outputs = len(set(d["worker_output"] for d in data))
    print(f"\n[6] UNIQUENESS")
    print(f"    Unique worker_cot_trace  : {unique_cots} / {total}  ({unique_cots/total*100:.1f}%)")
    print(f"    Unique worker_output     : {unique_outputs} / {total}  ({unique_outputs/total*100:.1f}%)")

    # 7. Train/eval split leakage (seed=42, 80/20)
    indices = list(range(total))
    random.seed(42)
    random.shuffle(indices)
    train_end = int(total * 0.8)
    train_idx = set(indices[:train_end])
    eval_idx = set(indices[train_end:])

    train_sigs = set(sigs[i] for i in train_idx)
    eval_sigs = [sigs[i] for i in eval_idx]
    leaked = sum(1 for s in eval_sigs if s in train_sigs)
    overlap_pct = leaked / len(eval_sigs) * 100 if eval_sigs else 0.0

    print(f"\n[7] TRAIN/EVAL SPLIT LEAKAGE (seed=42, 80/20)")
    print(f"    Train rows : {len(train_idx)}")
    print(f"    Eval rows  : {len(eval_sigs)}")
    print(f"    Eval rows whose signature appears in train: {leaked}  ({overlap_pct:.1f}%)")

    # 8. Violation type distribution
    vtype_counts = Counter(d.get("violation_type", "unknown") for d in data)
    print(f"\n[8] VIOLATION TYPE DISTRIBUTION")
    for vt, cnt in sorted(vtype_counts.items(), key=lambda x: -x[1]):
        print(f"    {vt:35s}: {cnt:5d}  ({cnt/total*100:.1f}%)")

    # 9. Level distribution
    level_counts = Counter(d.get("level", "?") for d in data)
    print(f"\n[9] LEVEL DISTRIBUTION")
    for lvl, cnt in sorted(level_counts.items()):
        print(f"    Level {lvl}: {cnt:5d}  ({cnt/total*100:.1f}%)")

    # 10. Critical checks
    critical_issues = []
    if "ESCALATE" in missing_classes:
        critical_issues.append("ESCALATE class is entirely missing — objective mismatch with 3-class model")
    if dup_pct > 30.0:
        critical_issues.append(f"Duplicate rate {dup_pct:.1f}% exceeds 30% threshold")
    if overlap_pct > 50.0:
        critical_issues.append(f"Train/eval overlap {overlap_pct:.1f}% exceeds 50% — severe data leakage")

    print("\n" + "=" * 60)
    if critical_issues:
        print("CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"  [CRITICAL] {issue}")
        print("=" * 60)
        return 1
    else:
        print("No critical issues found.")
        print("=" * 60)
        return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/audit_dataset.py <dataset.json>")
        sys.exit(1)
    exit_code = audit(sys.argv[1])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
