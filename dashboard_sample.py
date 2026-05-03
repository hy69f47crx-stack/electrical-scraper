import streamlit as st
import pandas as pd
import altair as alt
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="مقارنة الأسعار الكهربائية - الكويت",
    page_icon="⚡",
    layout="wide",
)

# ───────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;900&display=swap');

/* Sidebar toggle button */
.sidebar-toggle {
    position: fixed;
    top: 16px;
    right: 16px;
    z-index: 9999;
    background: var(--blue) !important;
    border: none !important;
    color: white !important;
    width: 44px !important;
    height: 44px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.4rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.3) !important;
    transition: all .2s !important;
    padding: 0 !important;
    line-height: 1 !important;
}

.sidebar-toggle:hover {
    background: var(--blue-l) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,.4) !important;
}

.sidebar-toggle:active {
    transform: scale(0.95);
}

:root {
    --bg:       #0f172a;
    --surface:  #1a2742;
    --surface2: #253558;
    --border:   #334155;
    --blue:     #3b82f6;
    --blue-l:   #60a5fa;
    --blue-d:   #1d4ed8;
    --teal:     #14b8a6;
    --teal-l:   #2dd4bf;
    --violet:   #a855f7;
    --violet-l: #d8b4fe;
    --amber:    #fbbf24;
    --amber-d:  #b45309;
    --green:    #10b981;
    --red:      #ef4444;
    --t1:       #f1f5f9;
    --t2:       #cbd5e1;
    --t3:       #94a3b8;
    --r:        10px;
    --r-lg:     16px;
    --sh:       0 4px 16px rgba(0,0,0,.4);
    --sh-md:    0 2px 8px rgba(0,0,0,.3);
}

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    background: var(--bg) !important;
    color: var(--t1);
}

.block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1400px;
    background: var(--bg) !important;
}

/* ══════════════════════════
   SIDEBAR — DARK MODERN
══════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-left: 2px solid var(--blue) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--t1) !important;
    font-family: 'Cairo', sans-serif !important;
}

section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] b {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
    margin: 8px 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stMetricLabel"] * {
    color: var(--t3) !important;
    font-size: 0.7rem !important;
}

section[data-testid="stSidebar"] [data-testid="stMetricValue"] * {
    color: var(--blue-l) !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
}

/* Radio Navigation */
section[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    transition: background .2s !important;
    color: var(--t2) !important;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(59,130,246,.15) !important;
    color: var(--blue-l) !important;
}

section[data-testid="stSidebar"] .stRadio input:checked + label {
    background: rgba(59,130,246,.25) !important;
    color: var(--blue-l) !important;
    border-right: 3px solid var(--blue) !important;
}

/* Sidebar Buttons */
section[data-testid="stSidebar"] .stButton button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--t1) !important;
    border-radius: 8px !important;
    font-family: 'Cairo', sans-serif !important;
    padding: 8px 12px !important;
    transition: all .2s !important;
    font-size: 0.9rem !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--border) !important;
    color: var(--blue-l) !important;
}

/* Primary Button */
section[data-testid="stSidebar"] .stButton [data-testid="baseButton-primary"] {
    background: var(--blue) !important;
    border-color: var(--blue-l) !important;
    color: white !important;
}

section[data-testid="stSidebar"] .stButton [data-testid="baseButton-primary"]:hover {
    background: var(--blue-l) !important;
}

/* Sidebar Caption */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--t3) !important;
    font-size: 0.72rem !important;
}

/* ══════════════════════════
   SIDEBAR COLLAPSE BUTTON - HIDDEN
══════════════════════════ */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stBaseButton-headerNoPadding"] {
    display: none !important;
}

/* Hide expand here */
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* Hide all expand more buttons completely */
[role="button"][aria-label="Expand"],
button[aria-label="Expand"],
.stPopover button[kind="tertiary"],
button[data-testid*="expanderButton"],
div[data-testid="stExpander"] > button {
    display: none !important;
}

/* Hide secondary buttons that might be expand */
button[kind="secondary"] {
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ══════════════════════════
   PAGE HEADER
══════════════════════════ */
.ph {
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(59,130,246,.1) 100%);
    border: 1px solid rgba(59,130,246,.3);
    border-radius: var(--r-lg);
    padding: 32px 40px;
    margin-bottom: 28px;
    box-shadow: var(--sh);
    display: flex;
    align-items: center;
    gap: 24px;
    position: relative;
    overflow: hidden;
}

.ph::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(59,130,246,.1), transparent);
    pointer-events: none;
}

.ph-icon {
    font-size: 2.8rem;
    line-height: 1;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.ph-text {
    flex: 1;
    position: relative;
    z-index: 1;
}

.ph-text h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--t1);
    margin: 0 0 6px;
    letter-spacing: -.02em;
}

.ph-text p {
    font-size: 0.92rem;
    color: var(--t2);
    margin: 0;
}

.ph-badge {
    margin-right: auto;
    background: rgba(20,184,166,.2);
    color: var(--teal-l);
    border: 1px solid rgba(20,184,166,.3);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.8rem;
    font-weight: 700;
    white-space: nowrap;
    position: relative;
    z-index: 1;
}

/* ══════════════════════════
   KPI CARDS
══════════════════════════ */
.kpi {
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(59,130,246,.05) 100%);
    border: 1px solid rgba(59,130,246,.2);
    border-radius: var(--r);
    padding: 20px 16px;
    box-shadow: var(--sh-md);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all .2s;
}

.kpi:hover {
    box-shadow: var(--sh);
    border-color: rgba(59,130,246,.4);
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(59,130,246,.15) 100%);
}

.kpi-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}

.kpi-icon-box.blue   { background: rgba(59,130,246,.25); }
.kpi-icon-box.teal   { background: rgba(20,184,166,.25); }
.kpi-icon-box.violet { background: rgba(168,85,247,.25); }
.kpi-icon-box.amber  { background: rgba(251,191,36,.25); }

.kpi-body {
    flex: 1;
}

.kpi-val {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--t1);
    line-height: 1;
}

.kpi-lbl {
    font-size: 0.8rem;
    color: var(--t3);
    margin-top: 4px;
}

/* ══════════════════════════
   SECTION HEADER
══════════════════════════ */
.sec {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(59,130,246,.2);
}

.sec-icon {
    font-size: 1.2rem;
}

.sec-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--t1);
}

.sec-badge {
    margin-right: auto;
    background: rgba(168,85,247,.2);
    color: var(--violet-l);
    border: 1px solid rgba(168,85,247,.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.76rem;
    font-weight: 700;
}

/* ══════════════════════════
   DEAL ROW
══════════════════════════ */
.deal {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 14px 16px;
    margin-bottom: 10px;
    box-shadow: var(--sh-md);
    display: flex;
    align-items: center;
    gap: 14px;
    transition: all .2s;
}

.deal:hover {
    box-shadow: var(--sh);
    border-color: var(--blue);
}

.deal-num {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(59,130,246,.25);
    color: var(--blue-l);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
}

.deal-num.n1 { background: rgba(251,191,36,.25); color: var(--amber); }
.deal-num.n2 { background: rgba(148,163,184,.15); color: var(--t2); }
.deal-num.n3 { background: rgba(217,119,6,.25); color: #f97316; }

.deal-info {
    flex: 1;
}

.deal-name {
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--t1);
}

.deal-store {
    font-size: 0.8rem;
    color: var(--t3);
    margin-top: 2px;
}

.deal-right {
    text-align: left;
    flex-shrink: 0;
}

.deal-price {
    font-weight: 700;
    color: var(--blue-l);
    font-size: 0.96rem;
}

.deal-save {
    display: inline-block;
    background: rgba(20,184,166,.2);
    color: var(--teal-l);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.74rem;
    font-weight: 700;
    margin-top: 2px;
}

/* ══════════════════════════
   WORK CARD
══════════════════════════ */
.wc {
    background: var(--surface2);
    border: 1px solid rgba(168,85,247,.2);
    border-radius: var(--r);
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: var(--sh-md);
    border-right: 3px solid var(--violet);
    transition: all .2s;
}

.wc:hover {
    box-shadow: var(--sh);
    border-color: rgba(168,85,247,.4);
}

.wc-cat {
    display: inline-block;
    background: rgba(168,85,247,.2);
    color: var(--violet-l);
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.75rem;
    font-weight: 700;
}

.wc-desc {
    font-weight: 600;
    font-size: 0.94rem;
    color: var(--t1);
    margin: 8px 0 5px;
    line-height: 1.5;
}

.wc-meta {
    font-size: 0.85rem;
    color: var(--t2);
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.wc-meta .p {
    color: var(--teal-l);
    font-weight: 700;
}

.wc-meta .s {
    background: rgba(59,130,246,.2);
    color: var(--blue-l);
