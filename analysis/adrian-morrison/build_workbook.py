"""
Adrian Morrison 1-month paid-trial economics workbook.

Switch FROM a 3-month paid trial ($90 / paid trial, ~31% trial->FP conversion)
TO a 1-month paid trial paid PER full-price (FP) conversion (~49% conversion),
across payouts of $250 / $300 / $350, at base (8,900) and stretch (12,000)
paid-trial volumes.

Methodology (confirmed via the Slack threads + River's pull from the warehouse):
  iGA  (incremental gross adds) = paid trials x IAF        (IAF = 0.38)
  FP shops / mo                 = paid trials x CVR         (CVR = 0.49 for 1-mo)
  Monthly spend (new model)     = payout x FP shops         (pay per FP conversion)
  Monthly spend (current model) = $90 x paid trials         (pay per paid trial)
  iCAC                          = monthly spend / iGA  ( = payout x CVR / IAF )
        check: $250 x 0.49 / 0.38 = $322 ; $300 -> $387 ; $350 -> $451  vs $267 target
  Cost per FP shop              = monthly spend / FP shops  ( = payout, new model )
  LTV:CAC                       = LTV per shop / cost per FP shop
        for the new model cost/FP = payout, so LTV:CAC = LTV / payout (CVR & IAF cancel)

LTV per FP shop -- source:
  shopify-dw.marketing.shop_ltv_mart_predictions_with_forecast
  US, payback_channel_group = 'Affiliates',
  per-shop = predicted_cumulative_total_profit_with_forecast / gross_adds_count_with_forecast
    1-month-trial era (Apr-Nov 2024 cohorts):  $93.35 @12mo · $130.12 @24mo · $164.51 @36mo
    3-month-trial era (Feb-Dec 2025 cohorts):  $74.87 @12mo · $128.52 @24mo · n.a. @36mo

Defaults follow River's bolded recommendations: 1-month era = go-forward LTV,
36-month = headline horizon, all-US, IAF held at 0.38 (+ sensitivity tab).
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------- styling
TITLE = Font(bold=True, size=14, color="FFFFFF")
HDR = Font(bold=True, size=11, color="FFFFFF")
SUBHDR = Font(bold=True, size=11)
BOLD = Font(bold=True)
ITAL = Font(italic=True, color="666666", size=9)

DARK = PatternFill("solid", fgColor="263238")
BLUE = PatternFill("solid", fgColor="1565C0")
GREEN = PatternFill("solid", fgColor="2E7D32")
TEAL = PatternFill("solid", fgColor="00695C")
AMBER = PatternFill("solid", fgColor="EF6C00")
GREYHDR = PatternFill("solid", fgColor="ECEFF1")
SECTION = PatternFill("solid", fgColor="CFD8DC")
ROWCUR = PatternFill("solid", fgColor="F5F5F5")
ROWNEW = PatternFill("solid", fgColor="FFFFFF")
INPUT = PatternFill("solid", fgColor="FFF59D")

thin = Side(style="thin", color="B0BEC5")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")

CUR = '"$"#,##0'
CUR2 = '"$"#,##0.00'
PCT = '0%'
PCTSIGN = '+0%;\\-0%;0%'
RATIO = '0.00"x"'
NUM = '#,##0'
NETCUR = '"$"#,##0;[Red]-"$"#,##0'


def sc(ws, ref, *, font=None, fill=None, align=None, fmt=None, border=True, value=None):
    c = ws[ref]
    if value is not None:
        c.value = value
    if font:
        c.font = font
    if fill:
        c.fill = fill
    if align:
        c.alignment = align
    if fmt:
        c.number_format = fmt
    if border:
        c.border = BORDER
    return c


wb = Workbook()

# ================================================================ ASSUMPTIONS
a = wb.active
a.title = "Assumptions"
A = "Assumptions!"

a["A1"] = "Assumptions / Inputs  —  edit these, every other tab recalculates"
a.merge_cells("A1:C1")
sc(a, "A1", font=TITLE, fill=DARK, align=LEFT)
sc(a, "B1", fill=DARK); sc(a, "C1", fill=DARK)
sc(a, "A2", value="Input", font=HDR, fill=DARK, align=LEFT)
sc(a, "B2", value="Value", font=HDR, fill=DARK, align=CENTER)
sc(a, "C2", value="Source / note", font=HDR, fill=DARK, align=LEFT)

# (row, label, value, fmt, source)  -- row index in sheet
arows = {
    3:  ("Paid trials / mo — base (current)", 8900, NUM, "Mar–Apr actuals; held constant in base scenarios."),
    4:  ("Paid trials / mo — stretch", 12000, NUM, "Stretch volume scenario."),
    5:  ("1-month trial → Full-Price CVR", 0.49, PCT, "Historic 1-mo trial conversion (vs ~31% at 3-mo)."),
    6:  ("Current 3-month trial CVR", 0.31, PCT, "Historic 3-mo trial conversion (~30%)."),
    7:  ("IAF — incrementality factor (current)", 0.38, "0.00", "iGA = paid trials × IAF; iCAC = payout × CVR / IAF."),
    8:  ("iCAC target (US, $)", 267, CUR, "US iCAC benchmark."),
    9:  ("Current payout ($ / paid trial)", 90, CUR, "Current 3-mo model pays per paid trial."),
    10: ("Payout 1 ($ / FP conversion)", 250, CUR, "New 1-mo model pays per full-price conversion."),
    11: ("Payout 2 ($ / FP conversion)", 300, CUR, "New 1-mo model pays per full-price conversion."),
    12: ("Payout 3 ($ / FP conversion)", 350, CUR, "New 1-mo model pays per full-price conversion."),
    13: ("LTV/shop — 1-mo era @12mo ($)", 93.35, CUR2, "shop_ltv_mart_predictions_with_forecast · US · Affiliates · Apr–Nov 2024 cohorts."),
    14: ("LTV/shop — 1-mo era @24mo ($)", 130.12, CUR2, "Same source. Go-forward LTV (proposal restores 1-mo trial)."),
    15: ("LTV/shop — 1-mo era @36mo ($)  [HEADLINE]", 164.51, CUR2, "Same source. Headline horizon (matches $267 iCAC basis)."),
    16: ("LTV/shop — 3-mo era @12mo ($)", 74.87, CUR2, "Same source · Feb–Dec 2025 cohorts. Current state."),
    17: ("LTV/shop — 3-mo era @24mo ($)", 128.52, CUR2, "Same source. Current state."),
    18: ("LTV/shop — 3-mo era @36mo ($)", None, CUR2, "Not yet aged to 36mo — left blank → shows 'n.a.'"),
    19: ("LTV realization factor (go-forward)", 1.00, "0%",
         "STRESS-TEST LEVER for the lead's 'LTV drops with a 1-mo trial' concern. "
         "% of observed 1-mo-era LTV assumed to hold. The observed number already includes "
         "marginal (lower-intent) converters, so 100% = no extra haircut; lower it (e.g. 80%) "
         "to be conservative for marginal-converter dilution / forecast risk."),
    20: ("IAF sensitivity — low", 0.38, "0.00", "Current incrementality."),
    21: ("IAF sensitivity — mid", 0.60, "0.00", "If a fresh 1-mo funnel re-baselines incrementality."),
    22: ("IAF sensitivity — high", 0.75, "0.00", "Upper incrementality scenario."),
}
for r, (label, val, fmt, src) in arows.items():
    sc(a, f"A{r}", value=label, font=BOLD, align=LEFT, fill=GREYHDR)
    cell = sc(a, f"B{r}", align=RIGHT, fmt=fmt)
    if val is not None:
        cell.value = val
    sc(a, f"C{r}", value=src, font=ITAL, align=LEFT)

a["B18"].fill = INPUT  # 3-mo @36mo (deliberately blank)
a["B19"].fill = INPUT  # LTV realization factor lever
a.column_dimensions["A"].width = 38
a.column_dimensions["B"].width = 13
a.column_dimensions["C"].width = 72

# absolute refs
TR_BASE, TR_STR = f"{A}$B$3", f"{A}$B$4"
CVR_NEW, CVR_CUR = f"{A}$B$5", f"{A}$B$6"
IAF, TARGET = f"{A}$B$7", f"{A}$B$8"
PAY_CUR = f"{A}$B$9"
PAY = {250: f"{A}$B$10", 300: f"{A}$B$11", 350: f"{A}$B$12"}
LTV_1MO = {12: f"{A}$B$13", 24: f"{A}$B$14", 36: f"{A}$B$15"}
LTV_3MO = {12: f"{A}$B$16", 24: f"{A}$B$17", 36: f"{A}$B$18"}
REAL = f"{A}$B$19"  # LTV realization factor (go-forward stress-test lever)
IAF_SENS = [f"{A}$B$20", f"{A}$B$21", f"{A}$B$22"]

# ================================================================ SCENARIOS
s = wb.create_sheet("Scenarios")

# column layout
headers = [
    ("A", "Scenario", 22, LEFT),
    ("B", "Trial era", 10, CENTER),
    ("C", "Paid trials / mo", 10, CENTER),
    ("D", "Payout ($)", 9, CENTER),
    ("E", "Payout basis", 12, CENTER),
    ("F", "Trial→FP CVR", 9, CENTER),
    ("G", "FP shops / mo", 9, CENTER),
    ("H", "iGA / mo", 9, CENTER),
    ("I", "Monthly spend", 12, CENTER),
    ("J", "Annual spend", 12, CENTER),
    ("K", "Cost / FP shop", 9, CENTER),
    ("L", "iCAC", 9, CENTER),
    ("M", "iCAC vs $267", 9, CENTER),
    ("N", "LTV/shop @12mo", 9, CENTER),
    ("O", "LTV/shop @24mo", 9, CENTER),
    ("P", "LTV/shop @36mo", 9, CENTER),
    ("Q", "LTV:CAC @12mo", 9, CENTER),
    ("R", "LTV:CAC @24mo", 9, CENTER),
    ("S", "LTV:CAC @36mo", 9, CENTER),
    ("T", "Total LTV/mo @36mo", 13, CENTER),
    ("U", "Total LTV/yr @36mo", 13, CENTER),
    ("V", "Net contrib/shop @36mo", 11, CENTER),
    ("W", "Net contrib/yr @36mo", 13, CENTER),
]
last = "W"

s["A1"] = "Adrian Morrison — 1-Month Paid-Trial Economics  (iCAC · LTV · LTV:CAC by payout & volume)"
s.merge_cells(f"A1:{last}1")
sc(s, "A1", font=TITLE, fill=DARK, align=LEFT)
for col, *_ in headers[1:]:
    sc(s, f"{col}1", fill=DARK)

# group header row 2
groups = [
    ("A", "E", "SCENARIO", SECTION, SUBHDR),
    ("F", "H", "WHAT WE GET", BLUE, HDR),
    ("I", "M", "WHAT IT COSTS", AMBER, HDR),
    ("N", "S", "LTV PER SHOP  &  LTV:CAC", TEAL, HDR),
    ("T", "W", "TOTALS & RETURNS", GREEN, HDR),
]
for c0, c1, txt, fill, font in groups:
    s.merge_cells(f"{c0}2:{c1}2")
    sc(s, f"{c0}2", value=txt, font=font, fill=fill, align=CENTER)
    a0, a1 = ord(c0), ord(c1)
    for o in range(a0, a1 + 1):
        sc(s, f"{chr(o)}2", fill=fill)

# column header row 3
for col, label, width, align in headers:
    sc(s, f"{col}3", value=label, font=SUBHDR, fill=GREYHDR, align=CENTER)
    s.column_dimensions[col].width = width

# scenario definitions
scenarios = [
    dict(name="Current (3-mo @ $90)", era="3-mo", trials=TR_BASE, payout=PAY_CUR,
         cvr=CVR_CUR, basis="per paid trial", spend="trial", ltv=LTV_3MO, cur=True),
    dict(name="$250 / FP · base 8.9k", era="1-mo", trials=TR_BASE, payout=PAY[250],
         cvr=CVR_NEW, basis="per FP conv.", spend="fp", ltv=LTV_1MO, cur=False),
    dict(name="$300 / FP · base 8.9k", era="1-mo", trials=TR_BASE, payout=PAY[300],
         cvr=CVR_NEW, basis="per FP conv.", spend="fp", ltv=LTV_1MO, cur=False),
    dict(name="$350 / FP · base 8.9k", era="1-mo", trials=TR_BASE, payout=PAY[350],
         cvr=CVR_NEW, basis="per FP conv.", spend="fp", ltv=LTV_1MO, cur=False),
    dict(name="$250 / FP · stretch 12k", era="1-mo", trials=TR_STR, payout=PAY[250],
         cvr=CVR_NEW, basis="per FP conv.", spend="fp", ltv=LTV_1MO, cur=False),
    dict(name="$300 / FP · stretch 12k", era="1-mo", trials=TR_STR, payout=PAY[300],
         cvr=CVR_NEW, basis="per FP conv.", spend="fp", ltv=LTV_1MO, cur=False),
    dict(name="$350 / FP · stretch 12k", era="1-mo", trials=TR_STR, payout=PAY[350],
         cvr=CVR_NEW, basis="per FP conv.", spend="fp", ltv=LTV_1MO, cur=False),
]

fmt_by_col = {
    "C": NUM, "D": CUR, "F": PCT, "G": NUM, "H": NUM, "I": CUR, "J": CUR,
    "K": CUR, "L": CUR, "M": PCTSIGN, "N": CUR2, "O": CUR2, "P": CUR2,
    "Q": RATIO, "R": RATIO, "S": RATIO, "T": CUR, "U": CUR, "V": NETCUR, "W": NETCUR,
}

r = 4
for sd in scenarios:
    fill = ROWCUR if sd["cur"] else ROWNEW
    ltv36 = sd["ltv"][36]
    guard36 = f'IF({ltv36}="","n.a.",'  # close with )
    # 1-mo (go-forward) LTV gets the realization-factor lever; current/3-mo = actuals
    fac = "" if sd["cur"] else f"*{REAL}"
    l12, l24, l36 = (sd["ltv"][12] + fac), (sd["ltv"][24] + fac), (ltv36 + fac)
    # text/value cells
    sc(s, f"A{r}", value=sd["name"], font=BOLD, align=LEFT, fill=fill)
    sc(s, f"B{r}", value=sd["era"], align=CENTER, fill=fill)
    sc(s, f"E{r}", value=sd["basis"], align=CENTER, fill=fill)
    # formula cells
    f = {
        "C": f"={sd['trials']}",
        "D": f"={sd['payout']}",
        "F": f"={sd['cvr']}",
        "G": f"=C{r}*F{r}",
        "H": f"=C{r}*{IAF}",
        "I": (f"=D{r}*C{r}" if sd["spend"] == "trial" else f"=D{r}*G{r}"),
        "J": f"=I{r}*12",
        "K": f"=I{r}/G{r}",
        "L": f"=I{r}/H{r}",
        "M": f"=L{r}/{TARGET}-1",
        "N": f"={l12}",
        "O": f"={l24}",
        "P": f"={guard36}{l36})",
        "Q": f"=N{r}/K{r}",
        "R": f"=O{r}/K{r}",
        "S": f"={guard36}{l36}/K{r})",
        "T": f"={guard36}{l36}*G{r})",
        "U": f"={guard36}{l36}*G{r}*12)",
        "V": f"={guard36}{l36}-K{r})",
        "W": f"={guard36}({l36}-K{r})*G{r}*12)",
    }
    for col, formula in f.items():
        cell = sc(s, f"{col}{r}", value=formula, align=RIGHT, fmt=fmt_by_col[col], fill=fill)
        if col in ("L", "S", "W"):
            cell.font = BOLD
    r += 1

# notes under the table
note_r = r + 1
notes = [
    "HEADLINE: at 36-mo LTV (~$164.51/shop) the funnel is LTV-negative at every payout — LTV:CAC = LTV ÷ payout = 0.66 ($250) · 0.55 ($300) · 0.47 ($350); iCAC runs 21–69% over the $267 target.",
    "BUT the proposal still wins on both structural axes vs the 3-mo status quo: CVR 31% → 49%, and 1-mo-era per-shop LTV is higher ($93.35 vs $74.87 @12mo).",
    "iGA (incremental gross adds) = paid trials × IAF; iCAC = monthly spend ÷ iGA = payout × CVR ÷ IAF. LTV:CAC uses cost per FP shop (= payout for the new model).",
    "Current state uses 3-mo-era LTV; @36mo not yet aged → shows 'n.a.'. New scenarios use 1-mo-era (go-forward) LTV. All-US.",
    "LTV-DROP CONCERN (lead): go-forward LTV here is the 1-mo-era observed value, which ALREADY includes lower-intent marginal converters. To stress-test further, set 'LTV realization factor' on Assumptions (e.g. 80%) — see the LTV sensitivity tab for the full grid and breakeven.",
]
for i, n in enumerate(notes):
    cell = s[f"A{note_r + i}"]
    cell.value = ("• " + n)
    cell.font = ITAL
    s.merge_cells(f"A{note_r + i}:{last}{note_r + i}")
    cell.alignment = LEFT

s.freeze_panes = "C4"

# ================================================================ IAF SENSITIVITY
iz = wb.create_sheet("IAF sensitivity")
iz["A1"] = "IAF sensitivity — iCAC moves with incrementality (LTV:CAC does not)"
iz.merge_cells("A1:E1")
sc(iz, "A1", font=TITLE, fill=DARK, align=LEFT)
for col in ("B", "C", "D", "E"):
    sc(iz, f"{col}1", fill=DARK)

iz["A2"] = ("LTV:CAC = LTV ÷ payout, so it is INDEPENDENT of IAF: $250→0.66 · $300→0.55 · $350→0.47 (36-mo). "
            "IAF only changes iCAC and iCAC-vs-target below.")
iz.merge_cells("A2:E2")
sc(iz, "A2", font=ITAL, align=LEFT)

iaf_labels = ["IAF 0.38 (low)", "IAF 0.60 (mid)", "IAF 0.75 (high)"]
payout_refs = [PAY[250], PAY[300], PAY[350]]
payout_lbls = ["$250 / FP", "$300 / FP", "$350 / FP"]


def iaf_block(title_row, metric):
    sc(iz, f"A{title_row}", value=("iCAC ($)" if metric == "icac" else "iCAC vs $267 target"),
       font=HDR, fill=(BLUE if metric == "icac" else AMBER), align=LEFT)
    for j in range(1, 5):
        sc(iz, f"{get_column_letter(j+0)}{title_row}",
           fill=(BLUE if metric == "icac" else AMBER))
    hr = title_row + 1
    sc(iz, f"A{hr}", value="Payout \\ IAF", font=SUBHDR, fill=GREYHDR, align=LEFT)
    for k, lab in enumerate(iaf_labels):
        sc(iz, f"{get_column_letter(2+k)}{hr}", value=lab, font=SUBHDR, fill=GREYHDR, align=CENTER)
    for pi, (pref, plab) in enumerate(zip(payout_refs, payout_lbls)):
        rr = hr + 1 + pi
        sc(iz, f"A{rr}", value=plab, font=BOLD, fill=GREYHDR, align=LEFT)
        for k in range(3):
            col = get_column_letter(2 + k)
            icac = f"{pref}*{CVR_NEW}/{IAF_SENS[k]}"
            if metric == "icac":
                formula, fmt = f"={icac}", CUR
            else:
                formula, fmt = f"=({icac})/{TARGET}-1", PCTSIGN
            sc(iz, f"{col}{rr}", value=formula, align=RIGHT, fmt=fmt)
    return hr + 1 + 3


end1 = iaf_block(4, "icac")
iaf_block(end1 + 2, "target")
iz.column_dimensions["A"].width = 18
for col in ("B", "C", "D"):
    iz.column_dimensions[col].width = 15

# ================================================================ LTV SENSITIVITY
lv = wb.create_sheet("LTV sensitivity")
lv["A1"] = "LTV sensitivity — addressing 'LTV drops with a 1-month trial'"
lv.merge_cells("A1:F1")
sc(lv, "A1", font=TITLE, fill=DARK, align=LEFT)
for col in ("B", "C", "D", "E", "F"):
    sc(lv, f"{col}1", fill=DARK)

lv["A2"] = ("The lead's concern is marginal-converter dilution: a shorter trial converts more people (31%→49%), "
            "and the extra converters can be lower-LTV. The 1-mo-era LTV we use ($164.51 @36mo) already reflects that "
            "regime. Below: LTV:CAC and net contribution per shop @36mo as the go-forward LTV is haircut from 100% "
            "down to 60% of observed. BREAKEVEN (LTV:CAC = 1.0) requires LTV/shop = payout.")
lv.merge_cells("A2:F4")
sc(lv, "A2", font=ITAL, align=LEFT)

real_facs = [1.30, 1.00, 0.85, 0.70, 0.60]
fac_lbls = ["130%", "100% (observed)", "85%", "70%", "60%"]
L36 = LTV_1MO[36]  # observed 1-mo era 36mo LTV


def ltv_block(title_row, metric):
    is_ratio = metric == "ratio"
    title = "LTV:CAC @36mo  (= LTV × factor ÷ payout)" if is_ratio else "Net contribution / shop @36mo ($)"
    sc(lv, f"A{title_row}", value=title, font=HDR, fill=(TEAL if is_ratio else GREEN), align=LEFT)
    for j in range(1, 7):
        sc(lv, f"{get_column_letter(j)}{title_row}", fill=(TEAL if is_ratio else GREEN))
    hr = title_row + 1
    sc(lv, f"A{hr}", value="Payout \\ LTV realization", font=SUBHDR, fill=GREYHDR, align=LEFT)
    for k, lab in enumerate(fac_lbls):
        sc(lv, f"{get_column_letter(2+k)}{hr}", value=lab, font=SUBHDR, fill=GREYHDR, align=CENTER)
    for pi, (pref, plab) in enumerate(zip(payout_refs, payout_lbls)):
        rr = hr + 1 + pi
        sc(lv, f"A{rr}", value=plab, font=BOLD, fill=GREYHDR, align=LEFT)
        for k, fac in enumerate(real_facs):
            col = get_column_letter(2 + k)
            ltv_eff = f"{L36}*{fac}"
            if is_ratio:
                formula, fmt = f"={ltv_eff}/{pref}", RATIO
            else:
                formula, fmt = f"={ltv_eff}-{pref}", NETCUR
            cell = sc(lv, f"{col}{rr}", value=formula, align=RIGHT, fmt=fmt)
            if abs(fac - 1.0) < 1e-9:
                cell.font = BOLD
    return hr + 1 + 3


e1 = ltv_block(6, "ratio")
e2 = ltv_block(e1 + 2, "net")

# breakeven callout
br = e2 + 2
sc(lv, f"A{br}", value="Breakeven LTV/shop needed (LTV:CAC = 1.0)  =  the payout itself:",
   font=BOLD, align=LEFT, fill=AMBER)
for col in ("B", "C", "D", "E", "F"):
    sc(lv, f"{col}{br}", fill=AMBER)
sc(lv, f"A{br+1}", value="Payout", font=SUBHDR, fill=GREYHDR, align=LEFT)
sc(lv, f"B{br+1}", value="Breakeven LTV", font=SUBHDR, fill=GREYHDR, align=CENTER)
sc(lv, f"C{br+1}", value="Observed LTV @36mo", font=SUBHDR, fill=GREYHDR, align=CENTER)
sc(lv, f"D{br+1}", value="× uplift needed", font=SUBHDR, fill=GREYHDR, align=CENTER)
for pi, (pref, plab) in enumerate(zip(payout_refs, payout_lbls)):
    rr = br + 2 + pi
    sc(lv, f"A{rr}", value=plab, font=BOLD, fill=GREYHDR, align=LEFT)
    sc(lv, f"B{rr}", value=f"={pref}", align=RIGHT, fmt=CUR)
    sc(lv, f"C{rr}", value=f"={L36}", align=RIGHT, fmt=CUR2)
    sc(lv, f"D{rr}", value=f"={pref}/{L36}", align=RIGHT, fmt='0.00"x"')

lv.column_dimensions["A"].width = 24
for col in ("B", "C", "D", "E", "F"):
    lv.column_dimensions[col].width = 16

# ================================================================ README
rd = wb.create_sheet("README")
rd["A1"] = "How this workbook works"
sc(rd, "A1", font=TITLE, fill=DARK, align=LEFT, border=False)
lines = [
    "", "PURPOSE",
    "Affiliate economics for Adrian Morrison switching from a 3-month paid trial ($90/paid trial,",
    "~31% conversion) to a 1-month paid trial paid per full-price conversion (~49%), at payouts of",
    "$250 / $300 / $350 and at base (8,900) and stretch (12,000) monthly paid-trial volumes.",
    "",
    "TABS",
    "  Assumptions      – every input + source. Edit here; all other tabs recalculate.",
    "  Scenarios        – current state + 3 payouts × 2 volumes, with iCAC, LTV@12/24/36, LTV:CAC, net contribution.",
    "  IAF sensitivity  – how iCAC moves at IAF 0.38 / 0.60 / 0.75 (LTV:CAC is IAF-independent).",
    "  LTV sensitivity  – LTV:CAC & net contribution as go-forward LTV is haircut 130%→60% of observed, plus breakeven.",
    "",
    "KEY FORMULAS",
    "  FP shops/mo    = paid trials × CVR",
    "  iGA/mo         = paid trials × IAF            (incremental gross adds)",
    "  Monthly spend  = payout × FP shops            (new model; current = $90 × paid trials)",
    "  Cost/FP shop   = monthly spend / FP shops     (= payout for the new model)",
    "  iCAC           = monthly spend / iGA          (= payout × CVR / IAF)",
    "  LTV:CAC        = LTV per shop / cost per FP shop",
    "",
    "VALIDATION",
    "  iCAC: $250→$322 · $300→$387 · $350→$451 (vs $267 target).",
    "  LTV:CAC @36mo: $250→0.66 · $300→0.55 · $350→0.47.   (matches River's Slack figures)",
    "",
    "LTV SOURCE",
    "  shopify-dw.marketing.shop_ltv_mart_predictions_with_forecast",
    "  US · payback_channel_group = 'Affiliates' ·",
    "  per-shop = predicted_cumulative_total_profit_with_forecast / gross_adds_count_with_forecast",
    "    1-mo era (Apr–Nov 2024): $93.35 / $130.12 / $164.51 @ 12/24/36mo   (go-forward)",
    "    3-mo era (Feb–Dec 2025): $74.87 / $128.52 / n.a.    @ 12/24/36mo   (current state)",
    "",
    "DEFAULTS APPLIED (per River's recommendation)",
    "  Volume unit = paid trials (49% applied directly to trials).",
    "  Headline horizon = 36 months. LTV era = 1-mo (go-forward). Geo = all-US. IAF = 0.38 (+ sensitivity tab).",
    "",
    "LEAD'S 'LTV DROPS WITH A 1-MO TRIAL' CONCERN — HOW IT'S HANDLED",
    "  The go-forward LTV is the observed 1-mo-era value, which already blends in lower-intent marginal converters.",
    "  An adjustable 'LTV realization factor' (Assumptions!B19, default 100%) lets you haircut it for extra caution,",
    "  and the LTV sensitivity tab shows the full grid + breakeven. Key point: breakeven LTV = the payout, so at $350",
    "  the shop would need ~2.1× its observed LTV just to break even — the conclusion holds across the whole haircut range.",
    "",
    "HEADLINE TAKEAWAY",
    "  On a straight per-shop basis the funnel is LTV-negative at all three payouts (36-mo LTV ~$165 < payout),",
    "  and iCAC is 21–69% over target — i.e. higher payouts buy the SAME customers for more. The structural",
    "  win is still real: compressing 3-mo → 1-mo lifts CVR (31%→49%) AND per-shop LTV ($75→$93 @12mo).",
]
for i, line in enumerate(lines, start=2):
    rd[f"A{i}"] = line
    if line.isupper() and line.strip():
        rd[f"A{i}"].font = BOLD
rd.column_dimensions["A"].width = 105

wb.save("analysis/adrian-morrison/adrian_morrison_1mo_trial_icac_ltv.xlsx")
print("workbook written")
