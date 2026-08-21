#!/usr/bin/env python3
"""Compatibility entry point for the v0.3 audit required by the v0.4 protocol."""

from run_v04_validation import main


if __name__ == "__main__":
    raise SystemExit(main())
