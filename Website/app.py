"""SkinSense website: katalog produk, detail produk, dan halaman Tentang.

Website ini hanya membaca file CSV hasil CODE 6, CODE 9, dan CODE 10, sehingga tidak menjalankan model apa pun.
Jalankan dari folder utama repository dengan perintah: streamlit run Website/app.py
"""
import ast
import base64
import difflib
import html
import re
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
NORMALIZATION_DIR = ROOT / "Data Preprocessing" / "data_after_normalization"
RECOMMENDER_DIR = ROOT / "Recommender System" / "data_after_recommender_system"
SUMMARY_DIR = ROOT / "Recommender System" / "data_after_ai_summary"
FILES = {
    "products": NORMALIZATION_DIR / "products_normalized.csv",
    "ingredients": NORMALIZATION_DIR / "ingredients_data_normalized.csv",
    "profile": RECOMMENDER_DIR / "product_profile.csv",
    "cards": RECOMMENDER_DIR / "effect_cards.csv",
    "examples": RECOMMENDER_DIR / "review_examples.csv",
    "recommendations": RECOMMENDER_DIR / "recommendations.csv",
    "summaries": SUMMARY_DIR / "ai_summary.csv",
}
OPTIONAL_FILES = {"summaries"}

EFFECTS = ["brightening", "hydrating", "anti-aging", "anti-acne", "soothing"]
LEVELS = ["Low", "Moderate", "High"]
LEVEL_CLASS = {"Low": "low", "Moderate": "mod", "High": "high"}
MATCH_WEIGHTS = [("Kemiripan efek", 60, "#111111"), ("Kategori sama", 30, "#8A8A8A"), ("Brand sama", 10, "#CFCFCF")]  # WEIGHTS di CODE 9
ALL_CATEGORIES = "Semua kategori"
ALL_EFFECTS = "Semua efek"
FILTER_KEYS = ["q", "kategori", "efek"]
PAGE_SIZE = 12
CLAMP_CHARS = 100

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
<defs>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="0.15"><stop offset="0" stop-color="#4A4A4A"/><stop offset="0.38" stop-color="#1F1F1F"/><stop offset="1" stop-color="#030303"/></linearGradient>
<linearGradient id="bulb" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#555555"/><stop offset="0.5" stop-color="#1C1C1C"/><stop offset="1" stop-color="#000000"/></linearGradient>
<linearGradient id="collar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B4B4B4"/><stop offset="0.45" stop-color="#686868"/><stop offset="1" stop-color="#2C2C2C"/></linearGradient>
<linearGradient id="hl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.6"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<linearGradient id="label" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#DCDCDC"/></linearGradient>
<filter id="soft" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="1.5"/></filter>
</defs>
<ellipse cx="32" cy="60.6" rx="17" ry="2.3" fill="#000" opacity="0.22" filter="url(#soft)"/>
<rect x="25.5" y="2.5" width="13" height="17.5" rx="6.5" fill="url(#bulb)"/>
<rect x="27.6" y="4.6" width="2.6" height="10" rx="1.3" fill="url(#hl)" opacity="0.85"/>
<rect x="22.5" y="18" width="19" height="8.5" rx="2.2" fill="url(#collar)"/>
<rect x="22.5" y="18" width="19" height="1.6" rx="0.8" fill="#FFFFFF" opacity="0.35"/>
<rect x="13.5" y="25" width="37" height="35" rx="9.5" fill="url(#glass)"/>
<rect x="16.8" y="29" width="3.2" height="26.5" rx="1.6" fill="url(#hl)" opacity="0.7"/>
<rect x="21" y="34.5" width="23" height="17.5" rx="3.6" fill="url(#label)"/>
<path d="M26.2 43.3 L30.3 47.4 L38.6 39" fill="none" stroke="#111111" stroke-width="3.1" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
AVATAR_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><rect width="24" height="24" fill="#E3E3E3"/>'
              '<circle cx="12" cy="9.3" r="4.2" fill="#A6A6A6"/><path d="M3.6 23c1.1-4.7 4.5-7.2 8.4-7.2s7.3 2.5 8.4 7.2" fill="#A6A6A6"/></svg>')
SEARCH_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8A8A8A" '
              'stroke-width="2" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 L20.5 20.5"/></svg>')


def svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


LOGO = svg_uri(LOGO_SVG)
AVATAR = svg_uri(AVATAR_SVG)
SEARCH_ICON = svg_uri(SEARCH_SVG)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap');
:root {
  --page: #F3F3F3; --card: #FFFFFF; --chip: #ECECEC; --line: #DADADA; --line-soft: #E6E6E6;
  --black: #000000; --text: #2E2E2E; --muted: #6F6F6F;
  --green: #2E6B3D; --green-bg: #D3E7D5; --amber: #7C5A0E; --amber-bg: #F5E5BC; --red: #8E2F28; --red-bg: #EEC9C5;
  --bar-pos: #4F9A5E; --bar-neg: #C0463C;
}
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
.stApp { background: var(--page); }
.stApp, .stApp input, .stApp button { font-family: 'Instrument Sans', sans-serif; }
[data-testid="stMainBlockContainer"] { max-width: 1280px !important; padding: 0 80px 40px !important; }
[data-testid="stVerticalBlock"] { gap: 16px; }
.stApp [data-baseweb="input"], .stApp [data-baseweb="select"] > div { min-height: 44px; background: #FFFFFF; }
.stApp [data-baseweb="input"] input { font-size: 15px; color: var(--black); }
.st-key-more { align-self: center; }
.st-key-more button { background: #FFFFFF; border: 1px solid var(--line-soft); color: var(--black); font-weight: 600; padding: 9px 16px; }
.st-key-more button:hover { border-color: #BDBDBD; color: var(--black); background: #FFFFFF; }
.st-key-more button p { font-weight: 600; font-size: 14.5px; }

.ss { color: var(--text); font-family: 'Instrument Sans', sans-serif; font-size: 15px; line-height: 1.5; -webkit-font-smoothing: antialiased; }
.ss *, .ss *::before, .ss *::after { box-sizing: border-box; }
:where(.ss) p { margin: 0; }
:where(.ss) a { color: inherit; text-decoration: none; }
.ss a:focus-visible, .ss summary:focus-visible, .ss label:focus-visible { outline: 2px solid var(--black); outline-offset: 2px; }
.num { font-family: 'Geist Mono', monospace; font-feature-settings: "tnum"; }
.h1 { color: var(--black); font-weight: 700; }
.h2 { color: var(--black); font-size: 24px; font-weight: 700; letter-spacing: -0.2px; line-height: 1.3; }
.sub { color: var(--muted); margin-top: 2px; }
.card { background: var(--card); border: 1px solid var(--line-soft); border-radius: 10px; }
a.card:hover { border-color: #BDBDBD; }
.pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 4px 12px; font-size: 13.5px; font-weight: 600; line-height: 1.35; white-space: nowrap; }
.pill.gray, .pill.vcg { background: #E4E4E4; color: #1F1F1F; }
.pill.vc, .pill.low { background: var(--green-bg); color: var(--green); }
.pill.mod { background: var(--amber-bg); color: var(--amber); }
.pill.high, .pill.fail { background: var(--red-bg); color: var(--red); }
.pill.neutral { background: var(--chip); color: #3A3A3A; }
.pill.zero { background: #EBEBEB; color: #9A9A9A; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.rule { height: 1px; background: var(--line); }
.btn { display: inline-flex; align-items: center; justify-content: center; white-space: nowrap; border-radius: 6px; padding: 9px 16px; font-weight: 600; font-size: 14.5px; }
.ss a.btn.dark { background: var(--black); color: #FFFFFF; }
.ss a.btn.light { background: #FFFFFF; border: 1px solid var(--line-soft); color: var(--black); }
.ss a.btn.light:hover { border-color: #BDBDBD; }
.star { color: #D4A017; }
.muted { color: var(--muted); }

.nav { height: 68px; display: flex; align-items: center; justify-content: space-between; position: relative; }
.nav::after { content: ""; position: absolute; bottom: 0; left: calc(50% - 50vw); width: 100vw; height: 1px; background: var(--line); }
.brandmark { display: flex; align-items: center; gap: 10px; }
.brandmark .word { font-size: 23px; font-weight: 700; color: var(--black); letter-spacing: -0.4px; }
.navlinks { display: flex; gap: 28px; font-size: 15px; font-weight: 500; }
.ss .navlinks a { color: var(--muted); }
.ss .navlinks a.on, .ss .navlinks a:hover { color: var(--black); }
.foot { margin-top: 48px; padding: 18px 0 8px; border-top: 1px solid var(--line-soft); font-size: 13px; color: var(--muted); display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.foot .brandmark { gap: 8px; font-weight: 700; color: var(--black); font-size: 15px; }

.titlebar { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; padding-top: 20px; }
.titlebar .h1 { font-size: 36px; letter-spacing: -0.6px; line-height: 1.15; }
.grid3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: auto; column-gap: 16px; row-gap: 16px; }
.pcard { padding: 18px; display: grid; grid-row: span 7; grid-template-rows: subgrid; row-gap: 0; }
.pcard > *, .rcard > * { align-self: start; }
.brand { font-size: 14px; color: #5A5A5A; letter-spacing: 0.2px; }
.pname { font-size: 19px; font-weight: 700; color: var(--black); line-height: 1.25; margin-top: 2px; }
.cat { font-size: 13.5px; font-weight: 600; color: #6A6A6A; margin-top: 4px; }
.pcard .chips.safety { margin-top: 12px; }
.pcard .rule { margin: 14px 0 12px; }
.vclabel { font-size: 13.5px; font-weight: 600; color: #4A4A4A; }
.pcard .vcchips { margin-top: 8px; }
.emptystate { padding: 56px 24px 52px; display: flex; flex-direction: column; align-items: center; text-align: center; }
.emptystate .ico { width: 52px; height: 52px; border-radius: 50%; background: #F0F0F0; display: flex; align-items: center; justify-content: center; }
.emptystate .h2 { margin-top: 16px; font-size: 20px; }
.emptystate p { margin-top: 6px; color: var(--muted); max-width: 520px; }
.suggest { margin-top: 16px; display: flex; gap: 10px; align-items: center; font-size: 14.5px; color: #3A3A3A; flex-wrap: wrap; justify-content: center; }
.ss .suggest a { border-radius: 999px; padding: 6px 14px; font-weight: 500; background: #FFFFFF; border: 1px solid var(--line-soft); }
.ss .suggest a:hover { border-color: #BDBDBD; }
.actions { margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }

.back { display: inline-block; margin-top: 24px; font-size: 14.5px; font-weight: 600; }
.ss a.back { color: var(--muted); }
.ss a.back:hover { color: var(--black); }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; margin-top: 18px; }
.head .brand { font-size: 17px; }
.head .h1 { font-size: 40px; letter-spacing: -0.8px; line-height: 1.1; margin-top: 2px; max-width: 880px; }
.head .cat { font-size: 15px; margin-top: 6px; }
.head .btn { margin-top: 28px; }
.meta { display: flex; gap: 18px; margin-top: 12px; align-items: center; flex-wrap: wrap; }
.meta .sep { width: 1px; height: 16px; background: var(--line); }
.ingr { margin-top: 16px; }
.ingr summary { list-style: none; cursor: pointer; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; width: fit-content; }
.ingr summary::-webkit-details-marker { display: none; }
.ingr .toggle { font-size: 14px; font-weight: 600; color: var(--muted); margin-left: 8px; text-decoration: underline; text-underline-offset: 3px; }
.ingr .toggle::after { content: "Lihat nama bahan"; }
.ingr[open] .toggle::after { content: "Sembunyikan nama bahan"; }
.ingr summary:hover .toggle { color: var(--black); }
.ingr-panel { margin-top: 12px; padding: 16px 18px; display: flex; flex-direction: column; gap: 12px; }
.ingr-group { display: grid; grid-template-columns: 170px 1fr; gap: 12px; align-items: start; font-size: 14px; line-height: 1.55; }
.ingr-group .pill { justify-self: start; }
.block { margin-top: 26px; }
.block .label { font-size: 15px; font-weight: 600; color: #4A4A4A; margin-bottom: 10px; }
.summary { padding: 22px 26px; margin-top: 28px; }
.summary .h2 { font-size: 19px; }
.summary p { margin-top: 8px; font-size: 16px; line-height: 1.6; color: #262626; max-width: 1000px; }
.summary .note { margin-top: 10px; font-size: 13px; color: var(--muted); }
.section { margin-top: 48px; }
.grid5 { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
.ecard { padding: 16px 14px; display: flex; flex-direction: column; }
.ecard .h3 { font-size: 17px; font-weight: 700; color: var(--black); }
.checks { margin-top: 12px; display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
.check { display: flex; align-items: center; gap: 8px; }
.mark { width: 18px; height: 18px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex: none; }
.mark.ok { background: var(--black); color: #FFFFFF; }
.mark.no { background: var(--red-bg); color: var(--red); }
.mark.na, .mark.off { background: var(--chip); color: #8A8A8A; }
.ecard .rule { margin: 12px 0; }
.rowline { display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
.rowline .k { font-weight: 600; color: #4A4A4A; }
.bars { display: flex; flex-direction: column; gap: 7px; font-size: 13.5px; margin-top: 8px; }
.bar { display: grid; grid-template-columns: 56px 1fr 46px; align-items: center; gap: 6px; }
.track { height: 8px; background: #E9E9E9; border-radius: 99px; overflow: hidden; }
.fill { height: 100%; border-radius: 99px; }
.bar .v { text-align: right; font-size: 13px; }
.reviews { display: flex; flex-direction: column; gap: 10px; margin-top: 14px; flex: 1; }
.msg { display: flex; gap: 7px; align-items: flex-start; }
.avatar { width: 24px; height: 24px; border-radius: 50%; flex: none; display: block; }
.bubble { position: relative; flex: 1; min-width: 0; background: #F1F1F1; border-radius: 0 12px 12px 12px; padding: 7px 10px 8px; font-size: 12.8px; line-height: 1.45; color: #2B2B2B; }
.bubble::before { content: ""; position: absolute; top: 0; left: -6px; border-right: 6px solid #F1F1F1; border-bottom: 7px solid transparent; }
.bhead { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; column-gap: 5px; margin-bottom: 2px; }
.who { font-size: 11px; font-weight: 600; color: #3A3A3A; white-space: nowrap; }
.sent { font-size: 11px; font-weight: 600; white-space: nowrap; }
.sent.pos { color: var(--green); }
.sent.neg { color: var(--red); }
.btext { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 5; overflow: hidden; overflow-wrap: anywhere; }
.moretoggle { display: none; }
.moretoggle:checked ~ .reviews .btext { display: block; -webkit-line-clamp: unset; }
.more { margin-top: 12px; font-size: 13.5px; font-weight: 600; color: var(--black); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; width: fit-content; }
.more::after { content: "Baca selengkapnya"; }
.moretoggle:checked ~ .more::after { content: "Tutup"; }
.empty { font-size: 13px; color: var(--muted); }
.grid4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-rows: auto; column-gap: 16px; row-gap: 16px; margin-top: 16px; }
.rcard { padding: 18px; display: grid; grid-row: span 6; grid-template-rows: subgrid; row-gap: 0; }
.rcard .pname { font-size: 18px; }
.rcard .rule { margin: 12px 0 10px; }
.rcard .chips { margin-top: 10px; }

.pagetitle { font-size: 36px; letter-spacing: -0.6px; line-height: 1.15; padding-top: 20px; }
.lead { font-size: 18px; line-height: 1.6; color: #2A2A2A; max-width: 760px; margin-top: 12px; }
.about { margin-top: 36px; border-top: 1px solid var(--line); }
.arow { display: grid; grid-template-columns: 280px 1fr; gap: 32px; padding: 32px 0; border-bottom: 1px solid var(--line); }
.arow .h2 { font-size: 20px; }
.abody { max-width: 720px; font-size: 15.5px; line-height: 1.6; color: #2E2E2E; }
.abody > * + * { margin-top: 18px; }
.conds { display: flex; flex-direction: column; gap: 12px; }
.cond { display: grid; grid-template-columns: 18px 1fr; gap: 12px; align-items: start; }
.cond .mark { margin-top: 3px; }
.cond b { display: block; color: var(--black); font-weight: 600; }
.cond .d { color: #555555; }
.legend { display: flex; flex-direction: column; gap: 10px; }
.lrow { display: grid; grid-template-columns: 170px 1fr; gap: 12px; align-items: center; }
.lrow .pill { justify-self: start; }
.wbar { display: flex; height: 12px; border-radius: 99px; overflow: hidden; gap: 2px; }
.wlegend { display: flex; gap: 24px; font-size: 14.5px; flex-wrap: wrap; }
.wlegend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 7px; }
.anote { font-size: 13.5px; color: var(--muted); }
.src { display: grid; grid-template-columns: 200px 1fr; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--line-soft); }
.src:last-child { border-bottom: 0; }
.src b { color: var(--black); font-weight: 600; }
.fineprint { margin-top: 28px; font-size: 13.5px; color: var(--muted); }

@media (max-width: 1100px) {
  .grid5 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .grid4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 900px) {
  [data-testid="stMainBlockContainer"] { padding: 0 24px 32px !important; }
  .grid3 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .arow { grid-template-columns: 1fr; gap: 12px; }
}
@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] { padding: 0 16px 24px !important; }
  .grid3, .grid4, .grid5 { grid-template-columns: minmax(0, 1fr); }
  .head { flex-direction: column; gap: 0; }
  .head .h1 { font-size: 28px; }
  .head .btn { margin-top: 16px; }
  .titlebar .h1, .pagetitle { font-size: 28px; }
  .ingr-group, .lrow, .src { grid-template-columns: 1fr; gap: 6px; }
  .navlinks { gap: 18px; }
}
"""


# ---------- helpers ----------
def esc(text):
    return html.escape(str(text), quote=True)


def idn(value, decimals=1):
    """Format angka Indonesia: titik untuk ribuan, koma untuk desimal."""
    if decimals == 0:
        return f"{int(round(value)):,}".replace(",", ".")
    return f"{value:,.{decimals}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def idn_text(text):
    """Ubah angka di teks ringkasan AI ke format Indonesia (93.0% menjadi 93,0% dan 1156 menjadi 1.156)."""
    text = re.sub(r"(\d+)\.(\d+)%", r"\1,\2%", text)
    return re.sub(r"(?<![\w.,])\d{4,}(?![\w.,%])", lambda match: idn(int(match.group()), 0), text)


def clean_name(text):
    text = " ".join(str(text).split()).replace("Ⓡ", "®")
    return re.sub(r"\s+\)", ")", re.sub(r"\(\s+", "(", text))


def cap(effect):
    return effect[:1].upper() + effect[1:]


def to_list(text):
    if pd.isna(text) or not str(text).strip():
        return []
    return [item.strip() for item in str(text).split(", ")]


def words(text):
    return re.findall(r"[0-9a-z]+", str(text).lower())


def link(**params):
    """Link ke halaman website ini. Parameter yang kosong tidak ditulis."""
    query = urlencode({key: value for key, value in params.items() if value})
    return "?" + query if query else "?"


def current_filters():
    return {key: st.query_params.get(key) for key in FILTER_KEYS if st.query_params.get(key)}


# ---------- data ----------
def is_lfs_pointer(path):
    with open(path, "rb") as file:
        return file.read(40).startswith(b"version https://git-lfs")


def file_problems():
    problems = []
    for name, path in FILES.items():
        if name in OPTIONAL_FILES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if not path.exists():
            problems.append(f"{relative} tidak ditemukan.")
        elif is_lfs_pointer(path):
            problems.append(f"{relative} masih berupa pointer Git LFS. Jalankan git lfs pull.")
    return problems


def file_versions():
    return tuple(path.stat().st_mtime if path.exists() else 0 for path in FILES.values())


@st.cache_data(show_spinner=False)
def load_data(versions):
    products = pd.read_csv(FILES["products"], usecols=["product_id", "product_url", "ingredients_list", "ingredients_count"])
    products["ingredients_list"] = products["ingredients_list"].map(lambda text: ast.literal_eval(text) if isinstance(text, str) else [])
    ingredients = pd.read_csv(FILES["ingredients"], usecols=["ingredient_name", "hazard_level"])
    hazard = {name: level for name, level in zip(ingredients["ingredient_name"], ingredients["hazard_level"]) if level in LEVELS}

    profile = pd.read_csv(FILES["profile"]).merge(products, on="product_id", how="left")
    profile["name"] = profile["product_name"].map(clean_name)
    for column, source in [("claimed", "claimed_effects"), ("supported", "supported_effects"), ("vc", "verified_capabilities")]:
        profile[column] = profile[source].map(to_list)
    profile["haystack"] = (profile["brand"].astype(str) + " " + profile["name"]).str.lower()
    profile = profile.sort_values("name", key=lambda names: names.str.lower()).reset_index(drop=True)

    vocabulary = {}
    for text in list(profile["name"]) + list(profile["brand"].astype(str)):
        for word in re.findall(r"[0-9A-Za-z]+", text):
            vocabulary.setdefault(word.lower(), word)

    summaries = {}
    summary_file = FILES["summaries"]
    if summary_file.exists() and not is_lfs_pointer(summary_file):
        table = pd.read_csv(summary_file, usecols=["product_id", "summary"], keep_default_na=False)
        summaries = {int(pid): text for pid, text in zip(table["product_id"], table["summary"]) if str(text).strip()}

    return {
        "profile": profile,
        "cards": pd.read_csv(FILES["cards"]),
        "examples": pd.read_csv(FILES["examples"]),
        "recommendations": pd.read_csv(FILES["recommendations"]),
        "hazard": hazard,
        "vocabulary": vocabulary,
        "summaries": summaries,
    }


def filter_products(profile, query, category, effect):
    mask = pd.Series(True, index=profile.index)
    for word in words(query):
        mask &= profile["haystack"].str.contains(word, regex=False)
    if category != ALL_CATEGORIES:
        mask &= profile["category"] == category
    if effect != ALL_EFFECTS:
        mask &= profile["vc"].map(lambda effects: effect.lower() in effects)
    return profile[mask]


def suggest_query(data, query, category, effect):
    """Saran ejaan: kata yang tidak ada di nama produk atau brand diganti dengan kata yang paling mirip."""
    vocabulary, haystack = data["vocabulary"], data["profile"]["haystack"]
    suggestion, changed = [], False
    for word in words(query):
        if haystack.str.contains(word, regex=False).any():
            suggestion.append(vocabulary.get(word, word))
            continue
        match = difflib.get_close_matches(word, list(vocabulary), n=1)
        if not match:
            return None
        suggestion.append(vocabulary[match[0]])
        changed = True
    suggestion = " ".join(suggestion)
    if not changed or filter_products(data["profile"], suggestion, category, effect).empty:
        return None
    return suggestion


# ---------- shared blocks ----------
def nav_html(active):
    links = "".join(f'<a class="{"on" if label == active else ""}" href="{esc(href)}">{label}</a>'
                    for label, href in [("Katalog", link()), ("Tentang", link(halaman="tentang"))])
    return (f'<div class="ss nav"><a class="brandmark" href="?"><img src="{LOGO}" width="34" height="34" alt="">'
            f'<span class="word">SkinSense</span></a><nav class="navlinks">{links}</nav></div>')


def footer_html():
    return (f'<div class="ss foot"><a class="brandmark" href="?"><img src="{LOGO}" width="22" height="22" alt="">'
            f'<span>SkinSense</span></a><span>Data dari SOCO by Sociolla, EWG Skin Deep, dan INCIDecoder</span></div>')


def safety_pills(row, prefix):
    pills = []
    for level in LEVELS:
        count = int(row[f"{level.lower()}_count"])
        css = LEVEL_CLASS[level] if count else "zero"
        pills.append(f'<span class="pill {css}"><span class="num">{count}</span>&nbsp;{prefix}{level}</span>')
    return "".join(pills)


def vc_pills(effects, css="vcg"):
    return "".join(f'<span class="pill {css}">{cap(effect)}</span>' for effect in effects)


def empty_state(title, text, actions="", extra=""):
    return (f'<div class="ss"><div class="card emptystate"><div class="ico"><img src="{SEARCH_ICON}" width="24" height="24" alt=""></div>'
            f'<div class="h2" role="heading" aria-level="2">{title}</div><p>{text}</p>{extra}'
            f'<div class="actions">{actions}</div></div></div>')


# ---------- katalog ----------
def product_card(row, filters):
    href = link(produk=row["product_id"], **filters)
    vc = vc_pills(row["vc"]) or '<span class="muted">Belum ada</span>'
    return (f'<a class="card pcard" href="{esc(href)}">'
            f'<div class="brand">{esc(row["brand"])}</div>'
            f'<div class="pname">{esc(row["name"])}</div>'
            f'<div class="cat">{esc(row["category"])}</div>'
            f'<div class="chips safety">{safety_pills(row, "")}</div>'
            f'<div class="rule"></div>'
            f'<div class="vclabel">Verified Capabilities</div>'
            f'<div class="chips vcchips">{vc}</div></a>')


def show_more():
    st.session_state["limit"] = st.session_state.get("limit", PAGE_SIZE) + PAGE_SIZE


def render_catalog(data):
    profile = data["profile"]
    title_slot = st.empty()

    category_options = [ALL_CATEGORIES] + sorted(profile["category"].dropna().unique())
    effect_options = [ALL_EFFECTS] + [cap(effect) for effect in EFFECTS]
    search_col, category_col, effect_col = st.columns([3, 1, 1], gap="small")
    with search_col:
        query = st.text_input("Cari produk", key="q", bind="query-params", live=True,
                              placeholder="Cari nama produk atau brand", label_visibility="collapsed")
    with category_col:
        category = st.selectbox("Kategori", category_options, key="kategori", bind="query-params", label_visibility="collapsed")
    with effect_col:
        effect = st.selectbox("Efek", effect_options, key="efek", bind="query-params", label_visibility="collapsed")

    query = (query or "").strip()
    category = category or ALL_CATEGORIES
    effect = effect or ALL_EFFECTS
    filters = {"q": query, "kategori": category if category != ALL_CATEGORIES else "", "efek": effect if effect != ALL_EFFECTS else ""}
    results = filter_products(profile, query, category, effect)

    title_slot.html(f'<div class="ss titlebar"><div class="h1" role="heading" aria-level="1">Katalog Produk</div>'
                    f'<span class="muted"><span class="num">{len(results)}</span> produk</span></div>')

    if results.empty:
        render_no_results(data, query, category, effect, filters)
        return

    signature = (query, category, effect)
    if st.session_state.get("signature") != signature:
        st.session_state["signature"] = signature
        st.session_state["limit"] = PAGE_SIZE
    limit = st.session_state.get("limit", PAGE_SIZE)
    cards = "".join(product_card(row, filters) for _, row in results.head(limit).iterrows())
    st.html(f'<div class="ss"><div class="grid3">{cards}</div></div>')
    if len(results) > limit:
        st.button("Tampilkan lebih banyak", key="more", on_click=show_more)


def render_no_results(data, query, category, effect, filters):
    has_filter = category != ALL_CATEGORIES or effect != ALL_EFFECTS
    reset_filter = f'<a class="btn light" href="{esc(link(q=query))}">Reset filter</a>'
    if query:
        clear_search = f'<a class="btn light" href="{esc(link(kategori=filters["kategori"], efek=filters["efek"]))}">Hapus pencarian</a>'
        suggestion = suggest_query(data, query, category, effect)
        extra = ""
        if suggestion:
            href = link(q=suggestion, kategori=filters["kategori"], efek=filters["efek"])
            extra = f'<div class="suggest">Mungkin maksudmu <a href="{esc(href)}">{esc(suggestion)}</a></div>'
        hint = "Coba cek ejaan, atau hapus filter kategori dan efek." if has_filter else "Coba cek ejaan, atau cari pakai nama brand."
        actions = clear_search + (reset_filter if has_filter else "")
        st.html(empty_state(f"Tidak ada produk untuk “{esc(query)}”", hint, actions, extra))
        return
    parts = []
    if category != ALL_CATEGORIES:
        parts.append(f"kategori {esc(category)}")
    if effect != ALL_EFFECTS:
        parts.append(f"Verified Capabilities {esc(effect)}")
    st.html(empty_state("Tidak ada produk yang cocok", f"Belum ada produk dengan {' dan '.join(parts)}.", reset_filter))


# ---------- detail produk ----------
def mark(state):
    symbol = {"ok": "✓", "no": "✕", "off": "✕", "na": "–"}[state]
    return f'<span class="mark {state}">{symbol}</span>'


def ingredient_panel(row, hazard):
    groups = {level: [] for level in LEVELS}
    unknown = []
    names = row["ingredients_list"] if isinstance(row["ingredients_list"], list) else []
    for name in names:
        level = hazard.get(name)
        (groups[level] if level else unknown).append(name)
    rows = []
    for level in LEVELS:
        text = ", ".join(esc(name) for name in groups[level]) or '<span class="muted">Tidak ada</span>'
        rows.append(f'<div class="ingr-group"><span class="pill {LEVEL_CLASS[level]}">{level}</span><span>{text}</span></div>')
    if unknown:
        rows.append(f'<div class="ingr-group"><span class="pill zero">Tanpa hazard level</span><span>{", ".join(esc(name) for name in unknown)}</span></div>')
    return f'<div class="card ingr-panel">{"".join(rows)}</div>'


def effect_card(effect, card, row, examples):
    is_claimed = effect in row["claimed"]
    failed = "no" if is_claimed else "off"
    has_reviews = card["review_count"] > 0
    states = [
        ("Diklaim", "ok" if is_claimed else "off"),
        ("Didukung bahan", "ok" if effect in row["supported"] else failed),
        ("Review positif", ("ok" if card["sentiment_label"] == "positif" else failed) if has_reviews else "na"),
    ]
    if effect in row["vc"]:
        status = '<span class="pill vc">Verified</span>'
    elif not is_claimed:
        status = '<span class="pill neutral">Tidak diklaim</span>'
    else:
        status = '<span class="pill fail">Belum terverifikasi</span>'

    def percent(value):
        return f"{idn(value)}%" if has_reviews else "–"

    bubbles = []
    for _, example in examples.iterrows():
        sentiment = "pos" if example["sentiment"] == "positif" else "neg"
        bubbles.append(f'<div class="msg"><img class="avatar" src="{AVATAR}" alt="">'
                       f'<div class="bubble"><div class="bhead"><span class="who">Pengguna SOCO</span>'
                       f'<span class="sent {sentiment}">{esc(str(example["sentiment"]).capitalize())}</span></div>'
                       f'<div class="btext">{esc(" ".join(str(example["review_text"]).split()))}</div></div></div>')
    toggle_id = "more-" + effect
    long_text = any(len(str(text)) > CLAMP_CHARS for text in examples["review_text"])
    toggle_input = f'<input type="checkbox" class="moretoggle" id="{toggle_id}">' if long_text else ""
    toggle_label = f'<label class="more" for="{toggle_id}"></label>' if long_text else ""
    reviews = "".join(bubbles) or '<div class="empty">Belum ada review tentang efek ini.</div>'
    checks = "".join(f'<div class="check">{mark(state)}<span>{label}</span></div>' for label, state in states)
    return (f'<div class="card ecard"><div class="h3" role="heading" aria-level="3">{cap(effect)}</div>'
            f'<div style="margin-top:6px">{status}</div><div class="checks">{checks}</div><div class="rule"></div>'
            f'<div class="rowline"><span class="k">Review</span><span class="num">{idn(card["review_count"], 0)}</span></div>'
            f'<div class="bars">'
            f'<div class="bar"><span>Positif</span><div class="track"><div class="fill" style="width:{card["positive_pct"]}%;background:var(--bar-pos)"></div></div><span class="v num">{percent(card["positive_pct"])}</span></div>'
            f'<div class="bar"><span>Negatif</span><div class="track"><div class="fill" style="width:{card["negative_pct"]}%;background:var(--bar-neg)"></div></div><span class="v num">{percent(card["negative_pct"])}</span></div>'
            f'</div>{toggle_input}<div class="reviews">{reviews}</div>{toggle_label}</div>')


def recommendation_card(rec, row, profile, filters):
    other = profile[profile["product_id"] == rec["recommended_id"]]
    if other.empty:
        return ""
    other = other.iloc[0]
    shared = [effect for effect in EFFECTS if effect in row["vc"] and effect in other["vc"]]
    href = link(produk=other["product_id"], **filters)
    return (f'<a class="card rcard" href="{esc(href)}"><div class="brand">{esc(other["brand"])}</div>'
            f'<div class="pname">{esc(other["name"])}</div><div class="cat">{esc(other["category"])}</div><div class="rule"></div>'
            f'<div class="rowline"><span class="k">Match</span><span class="num" style="font-weight:600">{idn(rec["match"])}%</span></div>'
            f'<div class="chips">{vc_pills(shared, "gray")}</div></a>')


def render_detail(data, product_id):
    profile = data["profile"]
    filters = current_filters()
    back = f'<a class="back" href="{esc(link(**filters))}">‹ Katalog</a>'
    found = profile[profile["product_id"].astype(str) == str(product_id).strip()]
    if found.empty:
        st.html(f'<div class="ss">{back}</div>')
        st.html(empty_state("Produk tidak ditemukan", "Produk ini tidak ada di katalog. Cari produk lain dari halaman katalog.",
                            f'<a class="btn light" href="{esc(link(**filters))}">Kembali ke katalog</a>'))
        return
    row = found.iloc[0]
    pid = int(row["product_id"])

    url = row.get("product_url")
    soco = f'<a class="btn dark" href="{esc(url)}" target="_blank" rel="noopener">Lihat di SOCO</a>' if isinstance(url, str) and url.startswith("http") else ""
    count = row.get("ingredients_count")
    ingredient_meta = f'<span class="sep"></span><span><span class="num">{int(count)}</span> bahan</span>' if pd.notna(count) else ""
    header = (f'{back}<div class="head"><div><div class="brand">{esc(row["brand"])}</div>'
              f'<div class="h1" role="heading" aria-level="1">{esc(row["name"])}</div><div class="cat">{esc(row["category"])}</div>'
              f'<div class="meta"><span><span class="star">★</span> <span class="num">{idn(row["rating"])}</span></span><span class="sep"></span>'
              f'<span><span class="num">{idn(row["review_count"], 0)}</span> review</span>{ingredient_meta}</div></div>{soco}</div>'
              f'<details class="ingr"><summary>{safety_pills(row, "bahan ")}<span class="toggle"></span></summary>'
              f'{ingredient_panel(row, data["hazard"])}</details>'
              f'<div class="rule" style="margin-top:22px"></div>'
              f'<div class="block"><div class="label">Verified Capabilities</div>'
              f'<div class="chips">{vc_pills(row["vc"]) or "<span class=muted>Belum ada</span>"}</div></div>')

    summary = data["summaries"].get(pid)
    summary_html = (f'<div class="card summary"><div class="h2" role="heading" aria-level="2">Ringkasan AI</div>'
                    f'<p>{esc(idn_text(summary))}</p><div class="note">Dibuat oleh AI dari data di halaman ini.</div></div>') if summary else ""

    cards = data["cards"][data["cards"]["product_id"] == pid].set_index("effect")
    examples = data["examples"][data["examples"]["product_id"] == pid].sort_values("rank")
    effect_cards = "".join(effect_card(effect, cards.loc[effect], row, examples[examples["effect"] == effect])
                           for effect in EFFECTS if effect in cards.index)

    recs = data["recommendations"][data["recommendations"]["product_id"] == pid].sort_values("rank")
    rec_cards = "".join(recommendation_card(rec, row, profile, filters) for _, rec in recs.iterrows())
    rec_html = (f'<div class="section"><div class="h2" role="heading" aria-level="2">Produk Serupa</div>'
                f'<div class="sub">Jumlah bahan Moderate dan High tidak lebih banyak daripada produk ini</div>'
                f'<div class="grid4">{rec_cards}</div></div>') if rec_cards else ""

    st.html(f'<div class="ss">{header}{summary_html}'
            f'<div class="section"><div class="h2" role="heading" aria-level="2">Efek Produk</div><div class="grid5">{effect_cards}</div></div>'
            f'{rec_html}</div>')


# ---------- tentang ----------
def render_about(data):
    profile = data["profile"]

    def row(title, body):
        return f'<div class="arow"><div class="h2" role="heading" aria-level="2">{title}</div><div class="abody">{body}</div></div>'

    def cond(title, text):
        return f'<div class="cond">{mark("ok")}<div><b>{title}</b><span class="d">{text}</span></div></div>'

    def legend(pill, text):
        return f'<div class="lrow">{pill}<span>{text}</span></div>'

    conditions = (cond("Diklaim", "Efeknya disebut di deskripsi produk.")
                  + cond("Didukung bahan", "Ada bahan yang fungsinya mendukung efek itu menurut EWG Skin Deep dan INCIDecoder.")
                  + cond("Review positif", "Review yang membahas efek itu lebih banyak yang positif daripada yang negatif."))
    statuses = (legend('<span class="pill vc">Verified</span>', "Ketiga syarat terpenuhi.")
                + legend('<span class="pill fail">Belum terverifikasi</span>', "Diklaim, tapi belum didukung bahan atau review-nya belum lebih banyak yang positif.")
                + legend('<span class="pill neutral">Tidak diklaim</span>', "Tidak disebut di deskripsi, tapi bahan dan review-nya tetap ditampilkan."))
    levels = (legend('<span class="pill low">Low</span>', "Bahaya rendah")
              + legend('<span class="pill mod">Moderate</span>', "Bahaya sedang")
              + legend('<span class="pill high">High</span>', "Bahaya tinggi"))
    weight_bar = "".join(f'<span style="width:{weight}%;background:{color}"></span>' for _, weight, color in MATCH_WEIGHTS)
    weight_legend = "".join(f'<span><i style="background:{color}"></i>{label} <b class="num">{weight}%</b></span>' for label, weight, color in MATCH_WEIGHTS)
    sources = (f'<div class="src"><b>SOCO by Sociolla</b><span>Data produk, deskripsi, dan review. Ada <span class="num">{len(profile)}</span> produk '
               f'dan <span class="num">{idn(profile["review_count"].sum(), 0)}</span> review.</span></div>'
               '<div class="src"><b>EWG Skin Deep</b><span>Hazard level dan fungsi bahan.</span></div>'
               '<div class="src"><b>INCIDecoder</b><span>Fungsi bahan.</span></div>')

    body = (
        '<div class="h1 pagetitle" role="heading" aria-level="1">Tentang SkinSense</div>'
        '<p class="lead">SkinSense membantu kamu mengecek klaim produk skincare sebelum membeli. Setiap klaim di deskripsi produk '
        'dicek dengan daftar bahannya dan dengan review pembeli di SOCO by Sociolla.</p><div class="about">'
        + row("Verified Capabilities", '<p>Verified Capabilities adalah efek yang klaimnya terbukti. Sebuah efek masuk Verified Capabilities '
              f'kalau memenuhi ketiga syarat ini.</p><div class="conds">{conditions}</div><div class="legend">{statuses}</div>')
        + row("Keamanan bahan", '<p>Setiap bahan punya hazard level dari EWG Skin Deep. EWG menilai bahaya setiap bahan dengan skala 1 sampai 10, '
              f'lalu mengelompokkannya menjadi tiga.</p><div class="legend">{levels}</div>'
              '<p class="anote">Bahan yang belum punya hazard level di EWG tidak dihitung.</p>')
        + row("Produk Serupa", '<p>Produk serupa dipilih dari kemiripan Verified Capabilities, kategori, dan brand. Nilai Match adalah gabungan ketiganya.</p>'
              f'<div class="wbar">{weight_bar}</div><div class="wlegend">{weight_legend}</div>'
              '<p>Produk yang jumlah bahan Moderate dan High-nya lebih banyak daripada produk yang sedang kamu lihat tidak akan direkomendasikan.</p>')
        + row("Ringkasan AI", '<p>Ringkasan di halaman produk ditulis oleh AI (gpt-oss-120b) hanya dari data di halaman itu. Sebelum ditampilkan, '
              'setiap ringkasan dicek otomatis supaya angka, efek, dan nama bahannya sesuai data.</p>')
        + row("Sumber data", f'<div>{sources}</div>')
        + '</div><p class="fineprint">SkinSense dibuat sebagai proyek skripsi Data Science di BINUS University. '
          'Informasi di sini bukan pengganti saran dokter kulit.</p>'
    )
    st.html(f'<div class="ss">{body}</div>')


# ---------- app ----------
st.set_page_config(page_title="SkinSense", page_icon="🧴", layout="wide", initial_sidebar_state="collapsed")
st.html(f"<style>{CSS}</style>")

page = st.query_params.get("halaman")
st.html(nav_html("Tentang" if page == "tentang" else "Katalog"))

problems = file_problems()
if problems:
    st.error("Data website belum lengkap.\n\n" + "\n".join(f"- {problem}" for problem in problems))
    st.stop()

data = load_data(file_versions())
if page == "tentang":
    render_about(data)
elif st.query_params.get("produk"):
    render_detail(data, st.query_params.get("produk"))
else:
    render_catalog(data)
st.html(footer_html())
