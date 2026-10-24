#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from tistory_bot import run_web_dashboard

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    run_web_dashboard()
