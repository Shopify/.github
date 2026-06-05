"""
Generates the Adrian Morrison 1-month paid-trial economics workbook.

Model context (reverse-engineered from the existing "US rate scenarios" analysis
and confirmed with the requester):

  * Affiliate is moving FROM a 3-month paid trial paid at $90 / paid trial
    (historic ~31% trial->full-price conversion) TO a 1-month paid trial where
    the affiliate is paid PER FULL-PRICE conversion (historic ~49% conversion).
  * Volumes: 8,900 paid trials / mo (base), 12,000 paid trials / mo (stretch).
  * iCAC = payout x CVR / IAF, where IAF (incrementality factor) = 0.38.
        check: $207 -> $267, $225 -> $290, $250 -> $322  (matches prior deck)
  * Monthly spend (new model) = payout x FP shops (pay per FP conversion).
  * LTV per FP shop comes from:
        shopify-dw.marketing.shop_ltv_mart_predictions_with_forecast
    That value is the single yellow INPUT cell (Assumptions!B9). Every LTV /
    LTV:CAC figure recomputes the moment it is filled in.

Everything in the Scenarios sheet is LIVE FORMULAS referencing the Assumptions
sheet, so payouts, volumes, CVR, IAF and LTV can all be tweaked in Google Sheets.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment

# ---------------------------------------------------------------- styling
TITLE = Font(bold=True, size=14, color="FFFFFF")
HDR = Font(bold=True, size=11, color="FFFFFF")
SUBHDR = Font(bold=True, size=11)
BOLD = Font(bold=True)
ITAL = Font(italic=True, color="666666")

GREEN = PatternFill("solid", fgColor="2E7D32")
DARK = PatternFill("solid", fgColor="37474F")
BLUE = PatternFill("solid", fgColor="1565C0")
GREYHDR = PatternFill("solid", fgColor="ECEFF1")
INPUT = PatternFill("solid", fgColor="FFF59D")  # yellow = editable input
SECTION = PatternFill("solid", fgColor="CFD8DC")

thin = Side(style="thin", color="B0BEC5")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")

CUR = '"$"#,##0'
CUR2 = '"$"#,##0.00'
PCT = '0%'
PCT1 = '0.0%'
RATIO = '0.00"x"'
NUM = '#,##0'


def style_cell(ws, ref, *, font=None, fill=None, align=None, fmt=None, border=True):
    c = ws[ref]
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


# ================================================================ ASSUMPTIONS
wb = Workbook()
a = wb.active
a.title = "Assumptions"

a["A1"] = "Assumptions / Inputs  (edit these — everything else recalculates)"
a.merge_cells("A1:C1")
style_cell(a, "A1", font=TITLE, fill=DARK, align=LEFT)
for col in ("B1", "C1"):
    a[col].fill = DARK

rows = [
    ("Paid trials / mo — base (current)", 8900, NUM, "Held constant in base scenarios."),
    ("Paid trials / mo — stretch", 12000, NUM, "Stretch volume scenario."),
    ("1-month trial -> Full-Price CVR", 0.49, PCT, "Historic 1-mo trial conversion."),
    ("Current 3-month trial CVR", 0.31, PCT, "Historic 3-mo trial conversion (~30%)."),
    ("IAF (incrementality factor)", 0.38, "0.00", "iCAC = payout x CVR / IAF."),
    ("iCAC target ($)", 267, CUR, "US iCAC benchmark."),
    ("Current payout ($ / paid trial)", 90, CUR, "Current 3-mo model pays per paid trial."),
    ("LTV per FP shop ($)", None, CUR,
     "INPUT: predicted LTV per shop from "
     "shopify-dw.marketing.shop_ltv_mart_predictions_with_forecast "
     "(US new shops via Adrian's funnel). Fill this cell."),
    ("New payout 1 ($ / FP conversion)", 250, CUR, "Per full-price conversion."),
    ("New payout 2 ($ / FP conversion)", 300, CUR, "Per full-price conversion."),
    ("New payout 3 ($ / FP conversion)", 350, CUR, "Per full-price conversion."),
]
for i, (label, val, fmt, note) in enumerate(rows, start=2):
    style_cell(a, f"A{i}", font=BOLD, align=LEFT, fill=GREYHDR)
    a[f"A{i}"] = label
    c = style_cell(a, f"B{i}", align=RIGHT, fmt=fmt)
    if val is not None:
        c.value = val
    style_cell(a, f"C{i}", font=ITAL, align=LEFT)
    a[f"C{i}"] = note

# Highlight the LTV input cell (row 9)
ltv_cell = a["B9"]
ltv_cell.fill = INPUT
ltv_cell.font = Font(bold=True, color="B71C1C")
ltv_cell.comment = Comment(
    "Paste predicted LTV per shop from\n"
    "shopify-dw.marketing.shop_ltv_mart_predictions_with_forecast\n"
    "(filtered to US new shops acquired via Adrian Morrison's funnel).\n"
    "Until filled, all LTV / LTV:CAC rows show '-'.",
    "model")

a.column_dimensions["A"].width = 34
a.column_dimensions["B"].width = 14
a.column_dimensions["C"].width = 60

# Named references for readability in formulas
A = "Assumptions!"
TRIALS_BASE = f"{A}$B$2"
TRIALS_STR = f"{A}$B$3"
CVR_NEW = f"{A}$B$4"
CVR_CUR = f"{A}$B$5"
IAF = f"{A}$B$6"
TARGET = f"{A}$B$7"
PAY_CUR = f"{A}$B$8"
LTV = f"{A}$B$9"

# ================================================================ SCENARIOS
s = wb.create_sheet("Scenarios")

# columns: A label | B Current | C-E base(8900) 250/300/350 | F-H stretch(12000) 250/300/350
cols = ["A", "B", "C", "D", "E", "F", "G", "H"]
# new-model columns -> (payout assumption cell, paid-trials cell)
new_cols = {
    "C": (f"{A}$B$10", TRIALS_BASE),
    "D": (f"{A}$B$11", TRIALS_BASE),
    "E": (f"{A}$B$12", TRIALS_BASE),
    "F": (f"{A}$B$10", TRIALS_STR),
    "G": (f"{A}$B$11", TRIALS_STR),
    "H": (f"{A}$B$12", TRIALS_STR),
}

# ---- title
s["A1"] = "Adrian Morrison — 1-Month Paid-Trial Economics (iCAC & LTV by payout)"
s.merge_cells("A1:H1")
style_cell(s, "A1", font=TITLE, fill=DARK, align=LEFT)
for col in cols[1:]:
    s[f"{col}1"].fill = DARK

# ---- group header row (2)
s["A2"] = ""
style_cell(s, "A2", fill=GREYHDR)
s["B2"] = "Current (Mar–Apr)"
style_cell(s, "B2", font=HDR, fill=DARK, align=CENTER)
s.merge_cells("C2:E2")
s["C2"] = "Base volume — 8,900 paid trials / mo"
style_cell(s, "C2", font=HDR, fill=BLUE, align=CENTER)
for col in ("D", "E"):
    s[f"{col}2"].fill = BLUE
s.merge_cells("F2:H2")
s["F2"] = "Stretch volume — 12,000 paid trials / mo"
style_cell(s, "F2", font=HDR, fill=GREEN, align=CENTER)
for col in ("G", "H"):
    s[f"{col}2"].fill = GREEN

# ---- payout header row (3)
s["A3"] = "Payout"
style_cell(s, "A3", font=SUBHDR, fill=GREYHDR, align=LEFT)
s["B3"] = "$90 / paid trial"
style_cell(s, "B3", font=HDR, fill=DARK, align=CENTER)
payout_hdr = {"C": "$250 / FP", "D": "$300 / FP", "E": "$350 / FP",
              "F": "$250 / FP", "G": "$300 / FP", "H": "$350 / FP"}
for col, txt in payout_hdr.items():
    s[f"{col}3"] = txt
    fill = BLUE if col in ("C", "D", "E") else GREEN
    style_cell(s, f"{col}3", font=HDR, fill=fill, align=CENTER)

row = 4


def section(title):
    global row
    s[f"A{row}"] = title
    s.merge_cells(f"A{row}:H{row}")
    style_cell(s, f"A{row}", font=SUBHDR, fill=SECTION, align=LEFT)
    for col in cols[1:]:
        s[f"{col}{row}"].fill = SECTION
    row += 1


def metric(label, builder, fmt, *, note=None, bold=False):
    """builder(col) -> formula string (without '='), or None to leave blank."""
    global row
    style_cell(s, f"A{row}", font=BOLD if bold else None, align=LEFT, fill=GREYHDR)
    s[f"A{row}"] = label
    if note:
        s[f"A{row}"].comment = Comment(note, "model")
    for col in cols[1:]:
        f = builder(col)
        c = style_cell(s, f"{col}{row}", align=RIGHT, fmt=fmt)
        if f is not None:
            c.value = "=" + f
        if bold:
            c.font = BOLD
    row += 1


def rate_ref(col):
    if col == "B":
        return PAY_CUR
    return new_cols[col][0]


def trials_ref(col):
    if col == "B":
        return TRIALS_BASE
    return new_cols[col][1]


def cvr_ref(col):
    if col == "B":
        return CVR_CUR
    return CVR_NEW


# cell helpers (current-row references)
def C(col, r):
    return f"{col}{r}"


# ---- WHAT WE GET
section("WHAT WE GET")
r_rate = row
metric("Payout rate ($)", lambda c: rate_ref(c), CUR)
r_trials = row
metric("Paid trials / mo", lambda c: trials_ref(c), NUM)
r_cvr = row
metric("Trial -> Full-Price CVR", lambda c: cvr_ref(c), PCT)
r_fp = row
metric("Full-Price shops / mo", lambda c: f"{C(c, r_trials)}*{C(c, r_cvr)}", NUM, bold=True)
r_fpgain = row
metric("FP shops gained / mo vs current",
       lambda c: f"{C(c, r_fp)}-$B${r_fp}", NUM)
metric("FP shops gained / yr vs current",
       lambda c: f"({C(c, r_fp)}-$B${r_fp})*12", NUM)

# ---- WHAT IT COSTS
section("WHAT IT COSTS")
r_spend = row
metric("Monthly spend ($)",
       lambda c: (f"{C(c, r_rate)}*{C(c, r_trials)}" if c == "B"
                  else f"{C(c, r_rate)}*{C(c, r_fp)}"),
       CUR,
       note="Current pays per paid trial ($90 x trials). New model pays per "
            "full-price conversion (payout x FP shops).")
metric("Annual spend ($)", lambda c: f"{C(c, r_spend)}*12", CUR)
r_cpfp = row
metric("Cost per FP shop ($)", lambda c: f"{C(c, r_spend)}/{C(c, r_fp)}", CUR)
r_icac = row
metric("iCAC ($)",
       lambda c: (f"{C(c, r_rate)}/{IAF}" if c == "B"
                  else f"{C(c, r_rate)}*{C(c, r_cvr)}/{IAF}"),
       CUR, bold=True,
       note="iCAC = payout x CVR / IAF (new model). Current = $90 / IAF. "
            "Reported Mar–Apr actual iCAC was ~$241.")
metric("iCAC vs $267 target", lambda c: f"{C(c, r_icac)}/{TARGET}-1", PCT,
       note="Positive = over target, negative = under target.")

# ---- LTV
section("LTV  (fill Assumptions!B9 to populate)")
r_ltvshop = row
metric("LTV per FP shop ($)", lambda c: f'IF({LTV}="","-",{LTV})', CUR,
       note="From shopify-dw.marketing.shop_ltv_mart_predictions_with_forecast.")
metric("Total LTV of new FP shops / mo ($)",
       lambda c: f'IF({LTV}="","-",{LTV}*{C(c, r_fp)})', CUR)
metric("Total LTV of new FP shops / yr ($)",
       lambda c: f'IF({LTV}="","-",{LTV}*{C(c, r_fp)}*12)', CUR)
metric("LTV : iCAC ratio",
       lambda c: f'IF({LTV}="","-",{LTV}/{C(c, r_icac)})', RATIO, bold=True,
       note="Lifetime value vs incremental CAC.")
metric("LTV : cost-per-FP-shop ratio",
       lambda c: f'IF({LTV}="","-",{LTV}/{C(c, r_cpfp)})', RATIO)
metric("Net LTV per FP shop ($)  (LTV - cost/FP shop)",
       lambda c: f'IF({LTV}="","-",{LTV}-{C(c, r_cpfp)})', CUR)

# widths
s.column_dimensions["A"].width = 38
for col in cols[1:]:
    s.column_dimensions[col].width = 16
s.freeze_panes = "B4"

# ================================================================ README
rd = wb.create_sheet("README")
rd["A1"] = "How this workbook works"
style_cell(rd, "A1", font=TITLE, fill=DARK, align=LEFT)
notes = [
    "",
    "PURPOSE",
    "Compare Adrian Morrison's affiliate economics when switching from a 3-month",
    "paid trial ($90 / paid trial, ~31% conversion) to a 1-month paid trial paid",
    "PER full-price conversion (~49% conversion), across payouts of $250/$300/$350.",
    "",
    "WHAT TO EDIT",
    "Only the Assumptions tab. Everything on Scenarios is live formulas.",
    "The yellow cell Assumptions!B9 (LTV per FP shop) is the one external input —",
    "paste the predicted LTV per shop from:",
    "    shopify-dw.marketing.shop_ltv_mart_predictions_with_forecast",
    "(filtered to US new shops acquired through Adrian's funnel).",
    "Until it is filled, all LTV / LTV:CAC rows display '-'.",
    "",
    "KEY FORMULAS",
    "  FP shops / mo      = paid trials x CVR",
    "  Monthly spend      = payout x FP shops        (new model, paid per FP)",
    "                     = $90 x paid trials         (current model)",
    "  Cost per FP shop   = monthly spend / FP shops",
    "  iCAC               = payout x CVR / IAF        (IAF = 0.38)",
    "  LTV : iCAC         = LTV per FP shop / iCAC",
    "",
    "VALIDATION (against prior US rate-scenarios deck)",
    "  $207 -> iCAC $267 | $225 -> iCAC $290 | $250 -> iCAC $322   (matches)",
    "",
    "NOTE ON 'CURRENT' COLUMN",
    "Formula-derived current iCAC = $90 / 0.38 = ~$237; the deck's reported",
    "Mar–Apr actual was ~$241 (minor real-world variance).",
    "",
    "LTV ACCESS NOTE",
    "This workbook was generated in an environment without shopify-dw / BigQuery",
    "credentials, so the LTV value could not be auto-queried. It is wired as an",
    "input cell so it populates instantly once the value is entered.",
]
for i, line in enumerate(notes, start=2):
    rd[f"A{i}"] = line
    if line.isupper() and line.strip():
        rd[f"A{i}"].font = BOLD
rd.column_dimensions["A"].width = 90

wb.save("analysis/adrian-morrison/adrian_morrison_1mo_trial_icac_ltv.xlsx")
print("workbook written")
