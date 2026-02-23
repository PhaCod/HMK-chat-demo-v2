#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_data.py — Export Gold table → data/conversations.csv
==============================================================
Chạy 1 lần để export dữ liệu thực (đã anonymize) cho Streamlit Cloud demo.

Cách dùng:
    python generate_data.py                          # tự detect lakehouse path
    python generate_data.py --lakehouse /opt/lakehouse
    python generate_data.py --synthetic              # tạo dữ liệu tổng hợp

Sau khi chạy xong:  data/conversations.csv  sẽ được tạo.
Commit file này lên GitHub → deploy Streamlit Cloud.
"""
import argparse
import glob
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
GOLD_SUBPATH = "gold/ai_unified_v6"
OUTPUT       = Path(__file__).parent / "data" / "conversations.csv"

# Cột loại bỏ (PII hoặc quá nặng)
DROP_COLS = [
    "full_conversation",   # PII + nặng
    "thread_id",           # internal ID
    "customer_id",         # PII
    "page_id",             # internal
]

# Cột AI có thể không dùng trong demo (tuỳ chọn comment lại)
DEMO_COLS = [
    "conversation_id", "conversation_date", "page_name",
    "message_count",
    "intent_primary", "purchase_stage", "funnel_type",
    "funnel_is_successful",
    "sentiment_overall", "sentiment_score",
    "disc_primary", "generation_cohort", "lifestyle_segment",
    "urgency_level", "trust_level", "price_sensitivity",
    "agent_overall_score", "empathy_score", "agent_closing_skill",
    "predicted_csat", "conversion_probability",
    "competitor_brand", "product_interest",
    "churn_reason",
    "processed_at",
]

# Cái paths có thể tìm lakehouse
POSSIBLE_PATHS = [
    Path(__file__).parent.parent / "chat-analytics-lakehouse" / "lakehouse",
    Path("/opt/lakehouse"),
    Path(os.environ.get("LAKEHOUSE_PATH", "__NONE__")),
]


# ── Helpers ────────────────────────────────────────────────────────────────────
def _find_parquet_files(lakehouse_path: Path) -> list[Path]:
    gold_path = lakehouse_path / GOLD_SUBPATH
    if not gold_path.exists():
        return []
    pattern = str(gold_path / "**" / "*.parquet")
    return [
        Path(f) for f in glob.glob(pattern, recursive=True)
        if "_delta_log" not in f
    ]


def _read_gold(lakehouse_path: Path) -> pd.DataFrame | None:
    files = _find_parquet_files(lakehouse_path)
    if not files:
        return None
    print(f"  → {len(files)} parquet files tại {lakehouse_path / GOLD_SUBPATH}")

    dfs = []
    for f in files:
        try:
            dfs.append(pd.read_parquet(f))
        except Exception as e:
            print(f"  ⚠ Skip {f.name}: {e}")
    if not dfs:
        return None
    return pd.concat(dfs, ignore_index=True)


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # Dedup by conversation_id
    if "conversation_id" in df.columns:
        df = df.sort_values("processed_at", ascending=False) if "processed_at" in df.columns else df
        df = df.drop_duplicates(subset=["conversation_id"], keep="first")

    # Drop PII
    for col in DROP_COLS:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Keep only demo columns (plus any extras)
    keep = [c for c in DEMO_COLS if c in df.columns]
    extra = [c for c in df.columns if c not in keep]
    if extra:
        print(f"  ℹ Cột phụ không dùng trong demo: {extra[:8]}{'...' if len(extra) > 8 else ''}")
    df = df[keep]

    # Parse dates
    if "conversation_date" in df.columns:
        df["conversation_date"] = pd.to_datetime(df["conversation_date"], errors="coerce")

    # Anonymize page_name if needed (giữ nguyên để demo meaningful)

    return df.reset_index(drop=True)


def _add_snippets(df: pd.DataFrame) -> pd.DataFrame:
    """Gán conversation_snippet từ templates (không có PII)."""
    # Import from app.py nếu cần
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from app import _SNIPPETS
        df["conversation_snippet"] = df["intent_primary"].map(
            lambda x: _SNIPPETS.get(str(x), _SNIPPETS.get("hoi_gia", ""))
        )
        print("  ✓ Đã gán conversation_snippet từ templates")
    except ImportError:
        print("  ⚠ Không import được app.py, bỏ qua conversation_snippet")
    return df


def generate_synthetic() -> pd.DataFrame:
    """Fallback: tạo dữ liệu tổng hợp."""
    sys.path.insert(0, str(Path(__file__).parent))
    from app import _generate_synthetic_data
    df = _generate_synthetic_data(n=350)
    print(f"  ✓ Đã tạo {len(df)} rows dữ liệu tổng hợp")
    return df


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Export Gold table cho Streamlit Demo")
    parser.add_argument("--lakehouse", type=str, help="Đường dẫn tới lakehouse root")
    parser.add_argument("--synthetic", action="store_true", help="Dùng dữ liệu tổng hợp thay vì Gold table")
    parser.add_argument("--n", type=int, default=350, help="Số rows nếu dùng synthetic (default: 350)")
    args = parser.parse_args()

    print("=" * 55)
    print("  Chat Analytics — Data Export for Streamlit Demo")
    print("=" * 55)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    df = None

    if args.synthetic:
        print("ℹ Chế độ synthetic được chọn.")
        df = generate_synthetic()

    else:
        # Try explicit path first
        if args.lakehouse:
            paths_to_try = [Path(args.lakehouse)] + POSSIBLE_PATHS
        else:
            paths_to_try = POSSIBLE_PATHS

        for p in paths_to_try:
            if str(p) == "__NONE__" or not p.exists():
                continue
            print(f"🔍 Thử đọc Gold table tại: {p}")
            df = _read_gold(p)
            if df is not None and len(df) > 0:
                print(f"  ✓ Đọc được {len(df)} rows")
                break
            else:
                print(f"  ✗ Không tìm thấy dữ liệu")

        if df is None or len(df) == 0:
            print("\n⚠ Không tìm thấy Gold table. Dùng dữ liệu tổng hợp...")
            df = generate_synthetic()
        else:
            print("\n🧹 Đang làm sạch và anonymize...")
            df = _clean(df)
            df = _add_snippets(df)
            print(f"  ✓ Sau khi clean: {len(df)} rows, {len(df.columns)} cột")

    # Save
    df.to_csv(OUTPUT, index=False)
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"\n✅ Đã lưu → {OUTPUT}  ({size_kb:.0f} KB, {len(df):,} rows)")
    print("\nBước tiếp theo:")
    print("  1. git add data/conversations.csv")
    print("  2. git commit -m 'Add demo data'")
    print("  3. Deploy lên Streamlit Cloud:")
    print("     App file  :  streamlit_demo/app.py")
    print("     Branch    :  main")
    print("=" * 55)


if __name__ == "__main__":
    main()
