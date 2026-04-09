import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import re
import warnings
warnings.filterwarnings('ignore')

TODAY = date(2026, 4, 2)
TODAY_TS = pd.Timestamp('2026-04-02')

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# HELPERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def add_bdays(start_date, n):
    if pd.isna(start_date) or start_date is None:
        return None
    if isinstance(start_date, str):
        try:
            start_date = pd.to_datetime(start_date).date()
        except:
            return None
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if n == 0:
        return start_date
    count = 0
    d = start_date
    while count < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            count += 1
    return d

def days_overdue(dt):
    if pd.isna(dt) or dt is None:
        return 0
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt).date()
        except:
            return 0
    if isinstance(dt, datetime):
        dt = dt.date()
    return (TODAY - dt).days

def parse_date(s):
    if pd.isna(s) or s is None or str(s).strip() == '':
        return None
    try:
        return pd.to_datetime(str(s)).date()
    except:
        return None

def fmt_date(d):
    if d is None:
        return 'TBD'
    return d.strftime('%m/%d/%Y')

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# TRANSIT LEAD TIMES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TRANSIT_5_ITEMS = {
    '501044','501052','707010','707020','801010','801030','801479',
    '32005112093000','32309112091500',
    '0975.752013PCM','0984.803014M','0984.803018MN',
}
TRANSIT_8_ITEMS = {'400310','4233-1000','12054-664'}

def get_transit_days(item_str):
    if pd.isna(item_str):
        return 7
    item = str(item_str).strip()
    if item in TRANSIT_5_ITEMS:
        return 5
    if item in TRANSIT_8_ITEMS:
        return 8
    if re.match(r'^0777', item):
        return 5
    if re.match(r'^(0716|0747)', item):
        return 8
    if re.match(r'^(32|12)\d{9,}', item):
        return 5
    if re.match(r'^0(975|984)\.', item):
        return 5
    return 7

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# LOAD DATA
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with open('/mnt/user-data/tool_results/NetSuite_ns_runSavedSearch_toolu_01Brs6wp2kMUvbCVNNgFwjVt.json') as f:
    raw = json.load(f)
bo = pd.DataFrame(json.loads(raw[0]['text']))

with open('/mnt/user-data/tool_results/NetSuite_ns_runSavedSearch_toolu_016iJFmR6tDfQCDTY4fCacxV.json') as f:
    raw2 = json.load(f)
po = pd.DataFrame(json.loads(raw2[0]['text']))

evo_open = pd.read_csv('/mnt/user-data/uploads/EVO_OPEN_ORDER_and_SHIP_REPORT.csv', low_memory=False)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PREP POs â€” CORRECTED IN-TRANSIT LOGIC
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
po['qty_billed'] = pd.to_numeric(po['Qty Billed'], errors='coerce').fillna(0)
po['qty_received'] = pd.to_numeric(po['Qty Received'], errors='coerce').fillna(0)
po['qty_to_go'] = pd.to_numeric(po['Qty To Go'], errors='coerce').fillna(0)
po['po_qty'] = pd.to_numeric(po['Quantity'], errors='coerce').fillna(0)
po['item'] = po['Item'].str.strip()
po['po_num'] = po['Document Number'].str.strip()
po['exp_ship'] = po['Expected Ship Date'].apply(parse_date)
po['date_shipped_parsed'] = pd.to_datetime(po['Date Shipped'], errors='coerce')
po['po_date'] = po['Date'].apply(parse_date)

# CORRECT in-transit detection:
# A PO line's remaining quantity (Qty To Go) is in transit when:
# 1. Date Shipped is populated (vendor actually shipped)
# 2. Date Shipped is recent â€” within 14 business days of today (still en route to TCW)
# 3. Qty To Go > 0 (there's still open quantity expected at TCW)
po['days_since_shipped'] = (TODAY_TS - po['date_shipped_parsed']).dt.days
po['is_in_transit'] = (
    po['date_shipped_parsed'].notna() &
    (po['days_since_shipped'] >= 0) &
    (po['days_since_shipped'] <= 14) &
    (po['qty_to_go'] > 0)
)

print(f"PO lines truly in transit (shipped within 14 days, Qty To Go > 0): {po['is_in_transit'].sum()}")
print(f"PO lines with old ship dates but Qty To Go > 0 (open/overdue): {((po['days_since_shipped'] > 14) & (po['qty_to_go'] > 0) & po['date_shipped_parsed'].notna()).sum()}")
print(f"PO lines with no ship date (not yet shipped): {(po['date_shipped_parsed'].isna() & (po['qty_to_go'] > 0)).sum()}")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PREP BACKORDERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
bo['bo_qty'] = pd.to_numeric(bo['Backordered'], errors='coerce').fillna(0)
bo['orig_promise'] = bo['Original Promise Date'].apply(parse_date)
bo['item'] = bo['DISPLAY NAME B1'].str.strip()
bo['so_num'] = bo['Sales Order#'].str.strip()
bo['internal_id'] = bo['Internal ID'].astype(str)
bo['item_internal_id'] = bo['Item Upload Name'].astype(str)
bo['is_blanket'] = bo['so_num'].str.contains(r'-', regex=True)

# ─────────────────────────────────────────────
# ITEM UPLOAD NAME — SUITEQL FULLNAME LOOKUP
# Item Upload Name field in customsearch3326 returns the item's internal NetSuite
# ID (e.g. 60670), not the display name. Load the lookup JSON built by the Claude
# tool call that runs before this script each session. The lookup maps internal
# item ID -> fullname (e.g. 'Constant Force Accessories : 501052').
# ─────────────────────────────────────────────
lookup_path = '/home/claude/item_name_lookup.json'
if not os.path.exists(lookup_path):
    raise FileNotFoundError(
        "item_name_lookup.json not found. "
        "Run the SuiteQL item fullname lookup step before running this script."
    )
with open(lookup_path) as _f:
    id_to_fullname = json.load(_f)
print(f"Item name lookup loaded: {len(id_to_fullname)} entries")

bo['item_upload'] = bo['item_internal_id'].map(id_to_fullname).fillna(bo['item_internal_id'])
missing_names = (bo['item_upload'] == bo['item_internal_id']).sum()
if missing_names > 0:
    print(f"WARNING: {missing_names} items could not be resolved to fullname — showing internal ID")
else:
    print(f"Item Upload Name resolved for all {len(bo)} backorder lines")

bo_sorted = bo.sort_values(['is_blanket', 'orig_promise'], ascending=[False, True]).reset_index(drop=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# EVO FULLY COVERED LOOKUP
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
evo_open['cust_mat'] = evo_open['Customer Material'].astype(str).str.strip()
evo_open['po_base'] = evo_open['Customer PO'].astype(str).str.extract(r'(PO\d+)', expand=False)

# Build lookup: (po_num, customer_material) pairs where Fully Covered Ind = 'Y' explicitly.
# Match on our PO number + our item number (Customer Material column).
# Blank/NaN Fully Covered Ind rows are NOT covered â€” must be exactly 'Y'.
fully_covered_lookup = set()
for _, row in evo_open.iterrows():
    if str(row.get('Fully Covered Ind', '')).strip() != 'Y':
        continue
    po_base = str(row.get('po_base', '')).strip()
    cust_mat = str(row.get('cust_mat', '')).strip()
    if po_base and cust_mat and cust_mat != 'nan':
        fully_covered_lookup.add((po_base, cust_mat))

def is_fully_covered(po_num, item):
    # Return True only if this exact PO + our item number has Fully Covered Ind = Y
    return (str(po_num).strip(), str(item).strip()) in fully_covered_lookup


# ─────────────────────────────────────────────────────────────
# EVO CS COMMENTS LOOKUP
# ─────────────────────────────────────────────────────────────
# The EVO Open Order report includes a CS Comments column with real-time
# vendor status notes, keyed on (PO, Customer Material). Priority: below
# EVO Updates-Active but above Fully Covered Ind / in-transit fallback.
#
# Known patterns:
#   "ESD 3/21"                       -> Estimated Ship Date from vendor DC
#   "COMPLETE TO SHP"                -> Ready to ship
#   "PENDING SHIPMENT FROM JZ"       -> Juarez plant, staged, pending ship
#   "PENDING RECEIPT OF COMPONENT"   -> Waiting on sub-component
#   "PENDING UPDATE"                 -> No info, following up
#   "PENDING UPDATE/SHORT COMPONENT" -> Short on component, no date

cs_comments_lookup = {}  # (po_base, cust_mat) -> comment_text
for _, row in evo_open.iterrows():
    cs_text = str(row.get('CS Comments', '')).strip()
    if not cs_text or cs_text.lower() == 'nan':
        continue
    po_base = str(row.get('po_base', '')).strip()
    cust_mat = str(row.get('cust_mat', '')).strip()
    if po_base and cust_mat and cust_mat != 'nan':
        cs_comments_lookup[(po_base, cust_mat)] = cs_text

def get_cs_comment(po_num, item):
    return cs_comments_lookup.get((str(po_num).strip(), str(item).strip()), None)

def parse_cs_comment(cs_text, item):
    """Parse EVO CS Comments into (vendor_ship_date, comment_type)."""
    if not cs_text:
        return None, None
    text_upper = cs_text.strip().upper()

    # ETA TO WSI pattern: "ETA TO WSI 5/11" — ETA at vendor DC, then +3BD to ship to TCW
    eta_wsi_match = re.search(r'ETA\s+TO\s+WSI\s+(\d{1,2}/\d{1,2})', text_upper)
    if eta_wsi_match:
        try:
            raw = eta_wsi_match.group(1)
            eta_date = pd.to_datetime(f"{raw}/2026").date()
            if eta_date < TODAY and (TODAY - eta_date).days > 14:
                eta_date = pd.to_datetime(f"{raw}/2027").date()
            vendor_ship = add_bdays(eta_date, 3)
            return vendor_ship, 'eta_to_wsi_cs'
        except:
            pass

    # ESD week pattern: "ESD WK 4/14" — week of date, treat start of that week as ESD
    esd_wk_match = re.match(r'ESD\s+WK\s+(\d{1,2}/\d{1,2})', text_upper)
    if esd_wk_match:
        try:
            raw = esd_wk_match.group(1)
            candidate = pd.to_datetime(f"{raw}/2026").date()
            if candidate < TODAY and (TODAY - candidate).days > 14:
                candidate = pd.to_datetime(f"{raw}/2027").date()
            return candidate, 'esd_week_cs'
        except:
            pass

    # ESD date pattern: "ESD 3/21", "ESD 6/8", "ESD 4/10 FROM MTY TO WSI", "ESD  4/3 FROM MTY..."
    # Use \s+ to handle double-spaces; extract date before any trailing text
    esd_match = re.match(r'ESD\s+(\d{1,2}/\d{1,2})', text_upper)
    if esd_match:
        try:
            raw = esd_match.group(1)
            candidate = pd.to_datetime(f"{raw}/2026").date()
            # Only roll to next year if >14 days stale (true year-boundary).
            # ESDs within 14 days in the past are recently-due — keep as 2026.
            if candidate < TODAY and (TODAY - candidate).days > 14:
                candidate = pd.to_datetime(f"{raw}/2027").date()
            # If ESD includes "FROM MTY TO WSI" the date is an ESD at vendor DC — treat same as esd_cs
            comment_type = 'esd_cs'
            return candidate, comment_type
        except:
            pass

    if re.search(r'COMPLETE TO SHP|COMPLETE TO SHIP', text_upper):
        return add_bdays(TODAY, 3), 'complete_to_ship_cs'

    if 'PENDING SHIPMENT FROM JZ' in text_upper:
        return None, 'pending_jz'

    # "PENDING SHIPMENT FROM MTY TO WSI" — material at MTY plant, not yet shipped to WSI
    if 'PENDING SHIPMENT FROM MTY' in text_upper:
        return None, 'pending_mty'

    if 'PENDING RECEIPT OF COMPONENT' in text_upper:
        return None, 'pending_component'

    # "NEED NEW UPDATE" — stale status, treat as pending
    if 'NEED NEW UPDATE' in text_upper or 'NEED UPDATE' in text_upper:
        return None, 'pending_cs'

    if 'PENDING' in text_upper:
        return None, 'pending_cs'

    return None, 'cs_informational'

def build_cs_comment_text(po_num, cs_text, comment_type, vendor_ship, item):
    """Build SC Procurement Update comment from a parsed CS Comment."""
    transit = get_transit_days(item)
    wh_avail = add_bdays(vendor_ship, transit) if vendor_ship else None

    if comment_type == 'esd_cs':
        esd_match = re.match(r'ESD\s+(\d{1,2}/\d{1,2})', cs_text.strip().upper())
        esd_str = esd_match.group(1) if esd_match else fmt_date(vendor_ship)
        return (f"{po_num} - Vendor ESD {esd_str}. "
                f"Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    if comment_type == 'complete_to_ship_cs':
        return (f"{po_num} - Vendor confirms material complete to ship. "
                f"Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    if comment_type == 'eta_to_wsi_cs':
        # ETA at vendor DC; vendor ships to TCW from there
        eta_match = re.search(r'ETA\s+TO\s+WSI\s+(\d{1,2}/\d{1,2})', cs_text.strip().upper())
        eta_str = eta_match.group(1) if eta_match else ''
        return (f"{po_num} - Material ETA to vendor distribution center {eta_str}. "
                f"Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    if comment_type == 'esd_week_cs':
        wk_match = re.search(r'ESD\s+WK\s+(\d{1,2}/\d{1,2})', cs_text.strip().upper())
        wk_str = wk_match.group(1) if wk_match else ''
        return (f"{po_num} - Vendor ESD week of {wk_str}. "
                f"Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    if comment_type == 'pending_jz':
        return (f"{po_num} - Material staged at vendor JZ plant, pending shipment. "
                f"Following up for confirmed ship date.")
    if comment_type == 'pending_mty':
        return (f"{po_num} - Material at vendor MTY plant, pending shipment to distribution center. "
                f"Following up for confirmed ship date.")
    if comment_type == 'pending_component':
        return (f"{po_num} - Vendor pending receipt of component. "
                f"Following up for updated ship date once component received.")
    if comment_type in ('pending_cs', 'cs_informational'):
        return f"{po_num} - Vendor update pending. Following up for revised ship date."
    return None

print(f"CS Comments lookup built: {len(cs_comments_lookup)} entries")


# ─────────────────────────────────────────────────────────────────────────
# PARSE EXISTING SC PROCUREMENT UPDATE NOTES
# ─────────────────────────────────────────────────────────────────────────
# Phrases that are hallmarks of a previously-generated SC Procurement Update comment.
_GENERATED_COMMENT_PATTERNS = re.compile(
    r'(?:'
    r'PO\d+\s*[-\u2013]\s*(?:Material in transit|Was supposed|Expected vendor|'
    r'PO confirmed|Vendor confirms|EVO open order|Vendor update|Vendor MTY|'
    r'Partial quantity|Following up|Balance of|Vendor ESD|'
    r'Material staged at vendor|Vendor pending receipt)'
    r'|Researching procurement status\.\s*Item not currently on open PO'
    r'|Item not currently on open PO\.\s*Checking with vendor'
    r')',
    re.IGNORECASE
)

# Matches a full generated-comment SENTENCE to strip templated text.
_GENERATED_SENTENCE = re.compile(
    r'PO\d+\s*[-\u2013]\s*(?:Material in transit|Was supposed|Expected vendor ship|'
    r'PO confirmed|Vendor confirms|EVO open order|Vendor update pending|Vendor MTY|'
    r'Partial quantity|Following up|Balance of|Vendor ESD|'
    r'Material staged at vendor|Vendor pending receipt)[^.]*\.',
    re.IGNORECASE
)

def extract_manual_note_prefix(note_text):
    """
    Separate the manually-typed portion of a Procurement Update Notes value from
    any previously-generated SC Procurement Update text that was appended to it.

    Strategy:
    1. If the note begins with (or contains) a generated-comment stem, strip the
       generated sentence(s) and keep any text that follows — that trailing text is
       the human-typed update appended after the prior upload.
    2. If no generated sentence is found, return the full text.
    3. Strip a leading 'SC Note:' prefix from the returned text so we don't
       double-prefix it when re-appending as 'SC Note: <text>'.
    """
    if not note_text or str(note_text).strip().lower() in ('', 'nan'):
        return ''
    text = str(note_text).strip()

    # Iteratively strip all generated sentences from the text.
    # Each iteration removes the first generated sentence found; loop until none remain.
    # Any text not consumed by a generated sentence is kept.
    remaining = text
    found_any = False
    while True:
        m = _GENERATED_SENTENCE.search(remaining)
        if not m:
            break
        found_any = True
        # Keep text before the match (manual prefix) + text after the match (manual suffix)
        before = remaining[:m.start()].strip()
        after = remaining[m.end():].strip()
        # Reconstruct: if there was text before the generated sentence, it's the manual prefix;
        # if there's text after, it's a manual update appended post-upload.
        parts = [p for p in [before, after] if p]
        remaining = ' '.join(parts)

    result = remaining.strip()

    # Also check for the RESEARCH-tier template which doesn't start with PO\d+
    if result and _GENERATED_COMMENT_PATTERNS.search(result):
        m2 = _GENERATED_COMMENT_PATTERNS.search(result)
        if m2:
            prefix = result[:m2.start()].strip()
            after2 = result[m2.end():].strip()
            result = ' '.join(p for p in [prefix, after2] if p).strip()

    # Discard residuals that are themselves generated boilerplate tails
    # (e.g. 'Expected warehouse availability MM/DD/YYYY.' left over after
    # stripping 'PO12345 - Expected vendor ship ...' from the front)
    # Also catches multi-sentence residuals like:
    #   'Expected vendor ship 03/21/2026. Expected warehouse availability 03/31/2026. Balance of...'
    _GENERATED_TAIL = re.compile(
        r'^(?:'
        r'Expected vendor ship \d{2}/\d{2}/\d{4}.*'
        r'|Expected warehouse availability \d{2}/\d{2}/\d{4}.*'
        r'|Balance of \d+ units on PO\d+.*'
        r'|to ship \d{1,2}/\d{1,2}/\d{4} \(\d+ days ago\)\. Following up.*'
        r'|Following up with vendor for (?:update|revised ship date).*'
        r'|Checking with vendor for availability.*'
        r'|Will provide update by \d{2}/\d{2}/\d{4}\.'
        r'|PO confirmed, awaiting vendor ship confirmation\.'
        r')\s*$',
        re.IGNORECASE | re.DOTALL
    )
    if _GENERATED_TAIL.match(result):
        result = ''

    # Also strip trailing generated boilerplate fragments that got left behind
    # (e.g. '2/19: checking w Measia on shortage  Following up.' -> '2/19: checking...')
    if result:
        _GENERATED_TAIL_SUFFIX = re.compile(
            r'\s*(?:Following up(?:\s+with vendor for(?:\s+update|\s+revised ship date)?)?\.'
            r'|Expected vendor ship \d{2}/\d{2}/\d{4}.*'
            r'|Expected warehouse availability \d{2}/\d{2}/\d{4}.*'
            r'|Balance of \d+ units on PO\d+.*'
            r'|[.\s]*Checking with vendor for availability.*'
            r'|[.\s]*Will provide update by \d{2}/\d{2}/\d{4}\.)$',
            re.IGNORECASE | re.DOTALL
        )
        result = _GENERATED_TAIL_SUFFIX.sub('', result).strip()

    # Strip a leading 'SC Note:' prefix to avoid double-prefixing on re-append
    result = re.sub(r'^SC\s+Note\s*:\s*', '', result, flags=re.IGNORECASE).strip()

    return result


def parse_existing_note(note_text, item):
    """Parse SC-entered Procurement Update Notes for actionable dates/status.
    Returns (vendor_ship_date, wh_avail_date, note_type, summary) or all None if unrecognized.

    Only the manually-typed prefix (before any prior generated comment) is parsed.
    """
    manual_prefix = extract_manual_note_prefix(note_text)
    if not manual_prefix:
        return None, None, None, None

    text = manual_prefix
    text_lower = text.lower()
    transit = get_transit_days(item)

    # Extract the note date prefix (e.g. "2/10", "1/29")
    note_date = None
    nd_match = re.match(r'^(\d{1,2}/\d{1,2})\s*[-:]?\s*', text)
    if nd_match:
        try:
            note_date = pd.to_datetime(nd_match.group(1) + '/2026').date()
        except:
            pass

    # Delivered / received at TCW â€” material is there, just pending warehouse receipt
    if re.search(r'deliver|rcvd|received|inbound.*tcw|tcw.*inbound', text_lower):
        return None, None, 'delivered_to_tcw', text

    # Ready to ship / complete to ship
    if re.search(r'ready to ship|complete to ship|rts', text_lower):
        vendor_ship = add_bdays(note_date or TODAY, 3)
        wh_avail = add_bdays(vendor_ship, transit)
        return vendor_ship, wh_avail, 'ready_to_ship', text

    # In transit to WSI with ETA
    eta_match = re.search(r'in transit.*eta[\s:]*([\d/]+)', text_lower)
    if eta_match:
        try:
            eta = pd.to_datetime(eta_match.group(1) + '/2026').date()
            vendor_ship = add_bdays(eta, 3)
            return vendor_ship, add_bdays(vendor_ship, transit), 'in_transit_eta', text
        except: pass

    # ETA to WSI
    eta2_match = re.search(r'eta.*wsi.*?([\d/]+)', text_lower)
    if eta2_match:
        try:
            eta = pd.to_datetime(eta2_match.group(1) + '/2026').date()
            vendor_ship = add_bdays(eta, 3)
            return vendor_ship, add_bdays(vendor_ship, transit), 'eta_to_wsi', text
        except: pass

    # MTY production scheduled
    mty_match = re.search(r'mty\s+prod(?:uct(?:ion|on))?\s+(?:scheduled\s+)?([\d/]+)', text_lower)
    if mty_match:
        try:
            prod_date = pd.to_datetime(mty_match.group(1) + '/2026').date()
            vendor_ship = add_bdays(prod_date, 10)
            return vendor_ship, add_bdays(vendor_ship, transit), 'mty_production', text
        except: pass

    # Generic future date mentioned (e.g. "ship date 3/15")
    date_match = re.search(r'(?:ship|est|expect|scheduled|sched).*?([\d]{1,2}/[\d]{1,2}(?:/\d{2,4})?)', text_lower)
    if date_match:
        try:
            vendor_ship = pd.to_datetime(date_match.group(1)).date()
            if vendor_ship > TODAY:
                return vendor_ship, add_bdays(vendor_ship, transit), 'ship_date', text
        except: pass

    # Pending / waiting for update â€” recognized but no actionable date
    if re.search(r'pending|waiting|no update|follow.?up', text_lower):
        return None, None, 'pending', text

    # Informational status note — no date pattern but worth preserving verbatim
    if text:
        return None, None, 'informational', text

    return None, None, 'unrecognized', text

def build_existing_note_comment(po_num, note_type, vendor_ship, wh_avail, note_text):
    """Build a SC Procurement Update comment from a parsed existing note."""
    if note_type == 'delivered_to_tcw':
        return (f"{po_num} - Material delivered to TCW, pending warehouse receipt. "
                f"Will update once received into inventory.")
    if note_type in ('ready_to_ship', 'complete_to_ship'):
        return (f"{po_num} - Vendor confirms material ready to ship. "
                f"Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    if note_type in ('in_transit_eta', 'eta_to_wsi'):
        return (f"{po_num} - Material in transit to vendor distribution center. "
                f"Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    if note_type == 'mty_production':
        mty_match = re.search(r'(\d{1,2}/\d{1,2})', note_text)
        prod_str = mty_match.group(1) if mty_match else ''
        return (f"{po_num} - Vendor MTY production scheduled {prod_str}. "
                f"Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    if note_type == 'ship_date':
        return (f"{po_num} - Expected vendor ship {fmt_date(vendor_ship)}. "
                f"Expected warehouse availability {fmt_date(wh_avail)}.")
    return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def build_fully_covered_comment(po_num, vendor_ship, wh_avail):
    """Generate the fully covered comment.
    Vendor ship date = TODAY + 5 business days (per established rule).
    PO expected ship date is disregarded — Fully Covered Ind is the most accurate signal.
    """
    return (f"{po_num} - EVO open order report confirms material fully covered "
            f"(ready to ship). Expected vendor ship {fmt_date(vendor_ship)}. "
            f"Expected warehouse availability {fmt_date(wh_avail)}.")

# BUILD PO LOOKUP + FIFO TRACKING
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _prior_note_beats_fully_covered(po_num, note_text, item):
    if not note_text or str(note_text).strip().lower() in ('','nan'):
        return False
    text = str(note_text).strip()
    if str(po_num).strip() not in text:
        return False
    if not _GENERATED_COMMENT_PATTERNS.search(text):
        return False
    dates = re.findall(r'(\d{2}/\d{2}/\d{4})', text)
    for d in dates:
        try:
            dt = pd.to_datetime(d).date()
            if dt > TODAY:
                return True
        except:
            pass
    return False

def _extract_prior_note_comment(po_num, note_text, item):
    if not note_text:
        return None, None, None
    text = str(note_text).strip()
    po_str = str(po_num).strip()
    idx = text.find(po_str)
    if idx < 0:
        return None, None, None
    segment = text[idx:]
    rest = segment[len(po_str):]
    next_po = re.search(r'\bPO\d+\b', rest)
    if next_po:
        segment = segment[:len(po_str) + next_po.start()].strip()
    if len(segment) > 300:
        segment = segment[:297] + '...'
    dates = re.findall(r'(\d{2}/\d{2}/\d{4})', segment)
    vendor_ship = None
    wh_avail = None
    if len(dates) >= 1:
        try: vendor_ship = pd.to_datetime(dates[0]).date()
        except: pass
    if len(dates) >= 2:
        try: wh_avail = pd.to_datetime(dates[1]).date()
        except: pass
    return segment.strip(), vendor_ship, wh_avail

po_sorted_df = po.sort_values(['item', 'po_date'], ascending=[True, True])
po_by_item = {}
for item, grp in po_sorted_df.groupby('item'):
    po_by_item[item] = grp.to_dict('records')

po_remaining = {}
for _, row in po.iterrows():
    key = (row['po_num'], row['item'])
    # Available qty = Qty To Go (unshipped remaining)
    po_remaining[key] = float(row['qty_to_go'])

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# FIFO ALLOCATION
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
results = []

for _, bo_row in bo_sorted.iterrows():
    item = bo_row['item']
    bo_qty_needed = float(bo_row['bo_qty'])
    so_num = bo_row['so_num']
    internal_id = bo_row['internal_id']
    item_upload = bo_row['item_upload']
    orig_promise = bo_row['orig_promise']
    transit_days = get_transit_days(item)

    # Parse existing SC Procurement Update Notes (manually entered from prior vendor calls)
    existing_note_raw = str(bo_row.get('Procurement Update Notes', '') or '').strip()
    ex_vendor_ship, ex_wh_avail, ex_note_type, ex_note_text = parse_existing_note(existing_note_raw, item)
    existing_note_actionable = ex_note_type not in (None, 'unrecognized')
    # 'informational' notes don't have actionable dates but we still want to preserve them
    existing_note_has_manual_text = ex_note_text and ex_note_type in ('pending', 'informational')

    # FIFO PO allocation
    available_pos = po_by_item.get(item, [])
    allocated = []
    remaining_need = bo_qty_needed

    for po_line in available_pos:
        if remaining_need <= 0:
            break
        key = (po_line['po_num'], po_line['item'])
        avail = po_remaining.get(key, 0)
        if avail <= 0:
            continue
        take = min(avail, remaining_need)
        allocated.append({'po': po_line, 'qty': take})
        po_remaining[key] = avail - take
        remaining_need -= take

    # â”€â”€ Build comment â”€â”€
    if not allocated:
        priority = 4; tier = 'RESEARCH'
        comment = ("Researching procurement status. Item not currently on open PO. "
                   "Checking with vendor for availability and lead time. "
                   f"Will provide update by {fmt_date(add_bdays(TODAY, 3))}.")
    else:
        primary_po = allocated[0]['po']
        po_num = primary_po['po_num']
        is_in_transit_flag = bool(primary_po['is_in_transit'])
        exp_ship = primary_po['exp_ship']
        date_shipped = parse_date(primary_po.get('Date Shipped',''))
        days_ago = primary_po.get('days_since_shipped')

        if existing_note_actionable and ex_note_type not in ('pending', 'informational'):
            # SC-entered note from a prior vendor call has actionable info — use it instead of generic fallback
            ex_comment = build_existing_note_comment(po_num, ex_note_type, ex_vendor_ship, ex_wh_avail, ex_note_text)
            if ex_comment:
                comment = ex_comment
                priority = 1 if ex_note_type == 'delivered_to_tcw' else 2
                tier = 'IMMEDIATE' if ex_note_type == 'delivered_to_tcw' else 'HIGH'
            else:
                existing_note_actionable = False  # fallthrough handled below

        elif get_cs_comment(po_num, item):
            # EVO CS Comments column — real-time vendor note on this PO + item
            _cs_text = get_cs_comment(po_num, item)
            _cs_ship, _cs_type = parse_cs_comment(_cs_text, item)
            _cs_built = build_cs_comment_text(po_num, _cs_text, _cs_type, _cs_ship, item)
            if _cs_built:
                comment = _cs_built
                # ESD and complete-to-ship are actionable dates -> HIGH or IMMEDIATE
                if _cs_type in ('esd_cs', 'complete_to_ship_cs'):
                    priority = 2; tier = 'HIGH'
                elif _cs_type == 'pending_jz':
                    priority = 2; tier = 'HIGH'
                else:
                    priority = 2; tier = 'HIGH'
            else:
                # Fallthrough to Fully Covered check
                if is_fully_covered(po_num, item):
                    priority = 1; tier = 'IMMEDIATE'
                    vendor_ship = add_bdays(TODAY, 5)
                    wh_avail = add_bdays(vendor_ship, transit_days)
                    comment = build_fully_covered_comment(po_num, vendor_ship, wh_avail)

        elif is_fully_covered(po_num, item):
            # EVO Open Order report confirms Fully Covered — material ready to ship
            priority = 1; tier = 'IMMEDIATE'
            vendor_ship = add_bdays(TODAY, 5)
            wh_avail = add_bdays(vendor_ship, transit_days)
            comment = build_fully_covered_comment(po_num, vendor_ship, wh_avail)

        elif is_in_transit_flag:
            # Truly in transit: Date Shipped within last 14 days
            priority = 1; tier = 'IMMEDIATE'
            wh_avail = add_bdays(date_shipped, transit_days)
            comment = (f"{po_num} - Material in transit to TCW "
                       f"(shipped {fmt_date(date_shipped)}). "
                       f"Expected warehouse availability {fmt_date(wh_avail)}.")

        elif date_shipped and days_ago and days_ago > 14:
            # Old ship date with remaining Qty To Go — likely partial receipt, remainder is open
            ref_date = exp_ship if (exp_ship and days_overdue(exp_ship) > 0) else date_shipped
            overdue = days_overdue(ref_date) if ref_date else int(days_ago)
            priority = 2; tier = 'HIGH'
            comment = (f"{po_num} - Was supposed to ship {fmt_date(ref_date)} "
                       f"({overdue} days ago). Following up with vendor for update on remaining balance.")
        elif exp_ship and days_overdue(exp_ship) > 0:
            # PO expected ship date has passed with no shipment recorded — overdue, follow up
            priority = 2; tier = 'HIGH'
            overdue_days = days_overdue(exp_ship)
            comment = (f"{po_num} - Was supposed to ship {fmt_date(exp_ship)} "
                       f"({overdue_days} days ago). Following up with vendor for update.")

        elif orig_promise and orig_promise < TODAY:
            priority = 2; tier = 'HIGH'
            if exp_ship:
                wh_avail = add_bdays(exp_ship, transit_days)
                comment = (f"{po_num} - Expected vendor ship {fmt_date(exp_ship)}. "
                           f"Expected warehouse availability {fmt_date(wh_avail)}.")
            else:
                comment = f"{po_num} - Following up with vendor for updated ship date."

        else:
            priority = 3; tier = 'STANDARD'
            if exp_ship:
                wh_avail = add_bdays(exp_ship, transit_days)
                comment = (f"{po_num} - Expected vendor ship {fmt_date(exp_ship)}. "
                           f"Expected warehouse availability {fmt_date(wh_avail)}.")
            else:
                comment = f"{po_num} - PO confirmed, awaiting vendor ship confirmation."

        # Multi-PO split
        if len(allocated) > 1:
            second = allocated[1]['po']
            s_po = second['po_num']
            s_ship = second['exp_ship']
            if s_ship:
                s_wh = add_bdays(s_ship, get_transit_days(second['item']))
                comment += (f" Balance of {int(allocated[1]['qty'])} units on {s_po} - "
                            f"Expected ship {fmt_date(s_ship)}.")

        # Append manual note text if it exists and wasn't already used as the primary comment
        # This preserves SC-entered status notes (informational/pending) even when a higher-priority
        # source (EVO file, in-transit, etc.) drove the main comment
        if ex_note_text and ex_note_type in ('pending', 'informational') and ex_note_text.strip():
            comment += f" SC Note: {ex_note_text.strip()}"

    is_past_due = bool(orig_promise and orig_promise < TODAY)

    results.append({
        'Priority_Tier': priority,
        'Tier_Label': tier,
        'Internal ID': internal_id,
        'Sales Order': so_num,
        'Item Upload Name': item_upload,
        'Item': item,
        'Company Name': bo_row.get('Company Name',''),
        'Backorder Qty': int(bo_qty_needed),
        'Original Promise Date': fmt_date(orig_promise),
        'Is Past Due': is_past_due,
        'Allocated PO': allocated[0]['po']['po_num'] if allocated else 'NONE',
        'PO Exp Ship Date': fmt_date(allocated[0]['po']['exp_ship']) if allocated and allocated[0]['po']['exp_ship'] else 'TBD',
        'Is In Transit': allocated[0]['po']['is_in_transit'] if allocated else False,
        'Is Fully Covered': is_fully_covered(allocated[0]['po']['po_num'], item) if allocated else False,
        'CS Comment Applied': 'Yes' if (get_cs_comment(allocated[0]['po']['po_num'], item) if allocated else None) else 'No',
        'CS Comment Raw': get_cs_comment(allocated[0]['po']['po_num'], item) if allocated else '',
        'Existing Note Applied': 'Yes' if existing_note_actionable else 'No',
        'Existing Note Raw': existing_note_raw,
        'Existing Procurement Notes': extract_manual_note_prefix(bo_row.get('Procurement Update Notes','')),
        'CSR Request Notes': str(bo_row.get('Procurement Request Notes','') or '') + ' ' + str(bo_row.get('Date Update Comments','') or ''),
        'SC Procurement Update': comment,
    })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(['Priority_Tier','Original Promise Date']).reset_index(drop=True)

print(f"\nResults: {len(results_df)} lines")
print(f"Tier breakdown: {results_df['Tier_Label'].value_counts().to_dict()}")
print(f"In transit: {results_df['Is In Transit'].sum()}")
print(f"Past due: {results_df['Is Past Due'].sum()}")

# Verify SO67229 / 01150376001
check = results_df[results_df['Sales Order']=='SO67229']
print("\nSO67229 check:")
print(check[['Sales Order','Item','Tier_Label','Allocated PO','Is In Transit','SC Procurement Update']].to_string())

results_df.to_pickle('/home/claude/results_df_v2.pkl')
print("\nSaved to results_df_v2.pkl")
