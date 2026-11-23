#!/usr/bin/env python3
"""
Look up ORCID iDs, Scopus author IDs and Google Scholar IDs for a list of people.

Input (first argument) can be any of:
  * a directory of make_cv faculty folders ("Last, First" or "Last, First - EmployeeID")
  * an .xlsx or .csv file with a "Name" column, or "First"/"Last" columns
    (also accepts "First Name"/"Last Name"/"FIRST_NAME"/"LAST_NAME"),
    and optionally an "Affiliation" column
  * a .txt file with one name per line ("First Last" or "Last, First")

Output is a spreadsheet (default researcher_ids.xlsx) with, for each source,
the best ID, a match confidence and the list of candidates that were found:
  high      one candidate whose name and affiliation (or email domain) both match
  medium    one candidate whose name matches, affiliation not confirmed
  ambiguous several candidates match; the ID column holds the most likely one
  none      nothing found
  error     the lookup failed (e.g. Google Scholar blocked the request)

With a faculty folder directory and --write, IDs with at least
--min-confidence (default high) are written into each folder's
make_cv/PersonalData/personal_data.txt as orcid / scopusid / googleid.
Existing non-empty IDs are never overwritten unless --overwrite is given, and
by default people who already have an ID are not looked up again for it.

Scopus needs an Elsevier API key: --scopus-key, the SCOPUS_API_KEY
environment variable, or the APIKey in ~/.config/pybliometrics.cfg (the same
key make_cv uses). The Author Search API generally only answers from a
subscribing institution's network (or with --scopus-insttoken).

Google Scholar has no API; this uses the scholarly package, which Google often
blocks.  Pass a ScraperAPI key with --scraper-id (same as make_cv's
webscraperid) if it does, or use --sources orcid,scopus to skip it.

Examples:
    python find_researcher_ids.py names.txt --affiliation "Clarkson University"
    python find_researcher_ids.py ~/Desktop/departments/MAE --affiliation Clarkson \\
        --email-domain clarkson.edu --write
    python find_researcher_ids.py faculty.xlsx -o ids.csv --sources orcid,scopus
"""

import argparse
import configparser
import itertools
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import pandas as pd
import requests

PERSONAL_DATA = Path("make_cv") / "PersonalData" / "personal_data.txt"
ID_KEYS = {"orcid": "orcid", "scopus": "scopusid", "scholar": "googleid"}
ALL_SOURCES = ("orcid", "scopus", "scholar")
RANK = {"high": 3, "medium": 2, "ambiguous": 1, "none": 0, "error": 0, "skipped": 0}
AFFIL_STOPWORDS = {"university", "of", "the", "college", "institute", "school", "at",
                   "and", "dept", "department", "inc", "llc", "&"}

ORCID_SEARCH = "https://pub.orcid.org/v3.0/expanded-search/"
SCOPUS_SEARCH = "https://api.elsevier.com/content/search/author"


# -------------------------------
# Name helpers
# -------------------------------

def norm(s):
    """Lower case, accents removed, punctuation turned into spaces."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


def split_name(name):
    """Return (given, family) from "Last, First M." or "First M. Last"."""
    name = re.sub(r"\s+-\s+\S+$", "", str(name).strip())  # drop " - EmployeeID"
    if "," in name:
        family, given = [p.strip() for p in name.split(",", 1)]
    else:
        parts = name.split()
        given, family = " ".join(parts[:-1]), (parts[-1] if parts else "")
    return given, family


def name_matches(want_given, want_family, given, family):
    """0 = no match, 1 = family + first initial, 2 = family + first name."""
    wf, f = norm(want_family), norm(family)
    if not wf or not f:
        return 0
    # allow hyphenated / compound surnames to match on either part
    if wf != f and wf not in f.split() and f not in wf.split():
        return 0
    wg, g = norm(want_given).split(), norm(given).split()
    if not wg or not g:
        return 1
    if wg[0] == g[0]:
        return 2
    if wg[0][0] == g[0][0] and (len(wg[0]) == 1 or len(g[0]) == 1):
        return 1
    return 0


def affil_matches(want, have):
    """True if every significant word of the wanted affiliation appears in have."""
    if not want or not have:
        return False
    words = [w for w in norm(want).split() if w not in AFFIL_STOPWORDS] or norm(want).split()
    have = norm(have)
    return all(re.search(rf"\b{re.escape(w)}\b", have) for w in words)


def decide(cands, affil_key="affil_ok"):
    """Pick an ID and confidence from scored candidates.

    Each candidate is a dict with "id", "name_score", affil_key, "weight"
    (documents or citations, used to break ties) and "desc".
    """
    named = [c for c in cands if c["name_score"] > 0]
    if not named:
        return "", "none"
    affil = [c for c in named if c.get(affil_key)]
    pool = affil or named
    best_score = max(c["name_score"] for c in pool)
    pool = sorted([c for c in pool if c["name_score"] == best_score],
                  key=lambda c: -(c.get("weight") or 0))
    if len(pool) > 1:
        return pool[0]["id"], "ambiguous"
    return pool[0]["id"], ("high" if affil else "medium")


def describe(cands, limit=8):
    named = [c for c in cands if c["name_score"] > 0] or cands
    return "; ".join(c["desc"] for c in named[:limit])


# -------------------------------
# ORCID
# -------------------------------

def orcid_query(q, rows=25):
    r = requests.get(ORCID_SEARCH, params={"q": q, "rows": rows},
                     headers={"Accept": "application/json"}, timeout=20)
    r.raise_for_status()
    return r.json().get("expanded-result") or []


def lookup_orcid(given, family, affiliation, args):
    def q_escape(s):
        return re.sub(r'([+\-!(){}\[\]^"~*?:\\/]|&&|\|\|)', r"\\\1", s)

    first = given.split()[0] if given else ""
    q = f"family-name:{q_escape(family)}"
    if first and len(first.rstrip(".")) > 1:
        q += f" AND given-names:{q_escape(first)}"
    results = []
    if affiliation:
        results = orcid_query(q + f' AND affiliation-org-name:"{q_escape(affiliation)}"')
    if not results:
        results = orcid_query(q)

    cands = []
    for r in results:
        insts = r.get("institution-name") or []
        inst_str = " | ".join(insts)
        emails = r.get("email") or []
        email_ok = bool(args.email_domain) and any(
            e.lower().endswith("@" + args.email_domain.lower()) or e.lower().endswith("." + args.email_domain.lower())
            for e in emails)
        g, f = r.get("given-names") or "", r.get("family-names") or ""
        cands.append({
            "id": r.get("orcid-id", ""),
            "name_score": name_matches(given, family, g, f),
            "affil_ok": email_ok or any(affil_matches(affiliation, i) for i in insts),
            "weight": len(insts),
            "desc": f"{r.get('orcid-id')} {g} {f} [{inst_str[:120]}]",
        })
    return cands


# -------------------------------
# Scopus
# -------------------------------

def scopus_api_keys(args):
    """All available Elsevier keys, in order (pybliometrics allows a comma list)."""
    if args.scopus_key:
        raw = args.scopus_key
    elif os.environ.get("SCOPUS_API_KEY"):
        raw = os.environ["SCOPUS_API_KEY"]
    else:
        raw = ""
        for cfg in (Path.home() / ".config" / "pybliometrics.cfg", Path.home() / ".pybliometrics" / "config.ini"):
            if cfg.is_file():
                cp = configparser.ConfigParser()
                cp.read(cfg)
                raw = cp.get("Authentication", "APIKey", fallback="")
                if raw:
                    break
    return [k.strip() for k in raw.split(",") if k.strip()]


_last_scopus_call = 0.0


def scopus_query(query, args):
    """Run one Author Search, pacing requests and handling 429 throttling.

    Elsevier returns 429 both for going too fast (retry after a pause) and
    for an exhausted weekly quota (X-RateLimit-Remaining = 0).  On an
    exhausted quota the next key from the list is tried, if there is one.
    """
    global _last_scopus_call
    for attempt in range(6):
        wait = args.scopus_delay - (time.time() - _last_scopus_call)
        if wait > 0:
            time.sleep(wait)
        headers = {"X-ELS-APIKey": args.scopus_key_resolved[0], "Accept": "application/json"}
        if args.scopus_insttoken:
            headers["X-ELS-Insttoken"] = args.scopus_insttoken
        r = requests.get(SCOPUS_SEARCH, params={"query": query, "count": 25}, headers=headers, timeout=30)
        _last_scopus_call = time.time()
        if r.status_code in (401, 403):
            raise RuntimeError(f"Scopus refused the request ({r.status_code}): {r.text[:200]}")
        if r.status_code != 429:
            break
        remaining = r.headers.get("X-RateLimit-Remaining")
        reset = r.headers.get("X-RateLimit-Reset")
        if remaining == "0":
            when = time.strftime("%a %b %d %H:%M", time.localtime(int(reset))) if reset and reset.isdigit() else "unknown"
            if len(args.scopus_key_resolved) > 1:
                print(f"   Scopus quota used up for key ...{args.scopus_key_resolved[0][-4:]}; trying next key")
                args.scopus_key_resolved.pop(0)
                continue
            raise RuntimeError(f"Scopus quota exhausted for this API key (resets {when})")
        pause = float(r.headers.get("Retry-After") or 0) or min(2 ** attempt, 30)
        print(f"   Scopus is throttling requests; waiting {pause:.0f} s")
        time.sleep(pause)
    r.raise_for_status()
    entries = r.json().get("search-results", {}).get("entry", []) or []
    return [e for e in entries if "error" not in e]


def lookup_scopus(given, family, affiliation, args, orcid=""):
    def q_escape(s):
        return s.replace('"', "").replace("(", " ").replace(")", " ")

    entries, by_orcid = [], False
    if orcid:
        entries = scopus_query(f"ORCID({orcid})", args)
        by_orcid = bool(entries)
    if not entries:
        q = f"AUTHLASTNAME({q_escape(family)})"
        if given:
            q += f" AND AUTHFIRST({q_escape(given.split()[0])})"
        if affiliation:
            entries = scopus_query(q + f' AND AFFIL("{q_escape(affiliation)}")', args)
        if not entries:
            entries = scopus_query(q, args)

    cands = []
    for e in entries:
        pn = e.get("preferred-name") or {}
        aff = e.get("affiliation-current") or {}
        if isinstance(aff, list):
            aff = aff[0] if aff else {}
        aff_name = f"{aff.get('affiliation-name', '')}, {aff.get('affiliation-city', '')}".strip(", ")
        author_id = str(e.get("dc:identifier", "")).replace("AUTHOR_ID:", "")
        docs = int(e.get("document-count") or 0)
        g, f = pn.get("given-name") or "", pn.get("surname") or ""
        cands.append({
            "id": author_id,
            "name_score": name_matches(given, family, g, f),
            "affil_ok": by_orcid or affil_matches(affiliation, aff_name),
            "weight": docs,
            "desc": f"{author_id} {g} {f} ({docs} docs) [{aff_name}]",
        })
    return cands


# -------------------------------
# Google Scholar
# -------------------------------

_scholarly = None


def get_scholarly(args):
    global _scholarly
    if _scholarly is None:
        try:
            from scholarly import scholarly, ProxyGenerator
        except ImportError as exc:
            sys.exit(f"Could not load the scholarly package ({exc}). Install it with: pip3 install scholarly "
                     "(or skip Google Scholar with --sources orcid,scopus)")
        if args.scraper_id:
            pg = ProxyGenerator()
            if pg.ScraperAPI(args.scraper_id):
                scholarly.use_proxy(pg)
                print("ScraperAPI in use for Google Scholar")
        _scholarly = scholarly
    return _scholarly


def lookup_scholar(given, family, affiliation, args):
    scholarly = get_scholarly(args)
    full = f"{given} {family}".strip()
    results = []
    for query in ([f"{full}, {affiliation}"] if affiliation else []) + [full]:
        results = list(itertools.islice(scholarly.search_author(query), 10))
        if results:
            break
    cands = []
    for r in results:
        sg, sf = split_name(r.get("name", ""))
        aff = r.get("affiliation", "") or ""
        email = r.get("email_domain", "") or ""
        email_ok = bool(args.email_domain) and email.lower().lstrip("@").endswith(args.email_domain.lower())
        cites = int(r.get("citedby") or 0)
        cands.append({
            "id": r.get("scholar_id", ""),
            "name_score": name_matches(given, family, sg, sf),
            "affil_ok": email_ok or affil_matches(affiliation, aff),
            "weight": cites,
            "desc": f"{r.get('scholar_id')} {r.get('name')} ({cites} cites) [{aff[:80]}{' ' + email if email else ''}]",
        })
    time.sleep(args.delay)
    return cands


LOOKUPS = {"orcid": lookup_orcid, "scopus": lookup_scopus, "scholar": lookup_scholar}


# -------------------------------
# Input / output
# -------------------------------

def read_personal_data(path):
    data = {}
    if path.is_file():
        for line in path.read_text().splitlines():
            m = re.match(r"^\s*(\w+)\s*=\s*(.*?)\s*$", line)
            if m:
                data[m.group(1).lower()] = m.group(2)
    return data


def write_personal_data(path, updates):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text() if path.is_file() else "# Personal data (IDs) for make_cv\n"
    for key, val in updates.items():
        line = f"{key} = {val}"
        pattern = re.compile(rf"(?im)^[ \t]*{key}[ \t]*=.*$")
        if pattern.search(text):
            text = pattern.sub(line, text, count=1)
        else:
            if text and not text.endswith("\n"):
                text += "\n"
            text += line + "\n"
    path.write_text(text)


def pick_col(df, *names):
    lower = {str(c).strip().lower(): c for c in df.columns}
    for n in names:
        if n in lower:
            return lower[n]
    return None


def read_people(source, default_affil):
    """Return a list of dicts: name, given, family, affiliation, folder, existing."""
    src = Path(source).expanduser()
    people = []
    if src.is_dir():
        for d in sorted(src.iterdir()):
            if d.is_dir() and "," in d.name:
                given, family = split_name(d.name)
                people.append({"name": d.name, "given": given, "family": family,
                               "affiliation": default_affil, "folder": d,
                               "existing": read_personal_data(d / PERSONAL_DATA)})
        return people

    if src.suffix.lower() in (".xlsx", ".xls", ".csv"):
        df = pd.read_csv(src, dtype=str) if src.suffix.lower() == ".csv" else pd.read_excel(src, dtype=str)
        df = df.fillna("")
        name_c = pick_col(df, "name", "faculty", "facultyname", "full name")
        first_c = pick_col(df, "first", "first name", "first_name", "given name", "given")
        last_c = pick_col(df, "last", "last name", "last_name", "family name", "surname")
        aff_c = pick_col(df, "affiliation", "institution", "university")
        if not name_c and not (first_c and last_c):
            sys.exit(f"{src} needs a Name column or First and Last columns; found {list(df.columns)}")
        for _, row in df.iterrows():
            if first_c and last_c and str(row[last_c]).strip():
                given, family = str(row[first_c]).strip(), str(row[last_c]).strip()
                name = f"{family}, {given}"
            elif name_c and str(row[name_c]).strip():
                name = str(row[name_c]).strip()
                given, family = split_name(name)
            else:
                continue
            existing = {}
            for src_key, pd_key in (("orcid", "orcid"), ("scopus", "scopusid"), ("scopusid", "scopusid"),
                                    ("googleid", "googleid"), ("google scholar", "googleid")):
                c = pick_col(df, src_key)
                if c and str(row[c]).strip():
                    existing[pd_key] = str(row[c]).strip()
            people.append({"name": name, "given": given, "family": family,
                           "affiliation": (str(row[aff_c]).strip() if aff_c else "") or default_affil,
                           "folder": None, "existing": existing})
        return people

    for line in src.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            given, family = split_name(line)
            people.append({"name": line, "given": given, "family": family,
                           "affiliation": default_affil, "folder": None, "existing": {}})
    return people


# -------------------------------
# Main
# -------------------------------

def main():
    p = argparse.ArgumentParser(description="Find ORCID, Scopus and Google Scholar IDs for a list of names.",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("source", help="faculty folder directory, .xlsx/.csv, or .txt list of names")
    p.add_argument("-o", "--output", default="researcher_ids.xlsx", help="output .xlsx or .csv")
    p.add_argument("-a", "--affiliation", default="", help='institution used to disambiguate, e.g. "Clarkson University"')
    p.add_argument("-e", "--email-domain", default="", help="verified email domain, e.g. clarkson.edu (Scholar/ORCID)")
    p.add_argument("--sources", default="orcid,scopus,scholar", help="comma list from: orcid,scopus,scholar")
    p.add_argument("--scopus-key", help="Elsevier API key (else $SCOPUS_API_KEY or pybliometrics config)")
    p.add_argument("--scopus-insttoken", default=os.environ.get("SCOPUS_INSTTOKEN"), help="Elsevier institutional token")
    p.add_argument("-s", "--scraper-id", help="ScraperAPI key for Google Scholar if Google blocks requests")
    p.add_argument("--delay", type=float, default=2.0, help="seconds to wait between Google Scholar searches")
    p.add_argument("--scopus-delay", type=float, default=0.5, help="minimum seconds between Scopus requests")
    p.add_argument("--write", action="store_true", help="write IDs into each folder's personal_data.txt")
    p.add_argument("--min-confidence", choices=["high", "medium", "ambiguous"], default="high",
                   help="lowest confidence written with --write (default high)")
    p.add_argument("--overwrite", action="store_true", help="replace existing IDs in personal_data.txt")
    p.add_argument("--recheck", action="store_true", help="look up people even if they already have an ID")
    args = p.parse_args()

    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    bad = [s for s in sources if s not in ALL_SOURCES]
    if bad:
        sys.exit(f"Unknown source(s): {', '.join(bad)}")
    if "scopus" in sources:
        args.scopus_key_resolved = scopus_api_keys(args)
        if not args.scopus_key_resolved:
            print("No Scopus API key found (--scopus-key, $SCOPUS_API_KEY or ~/.config/pybliometrics.cfg); skipping Scopus.")
            sources.remove("scopus")

    people = read_people(args.source, args.affiliation)
    if not people:
        sys.exit(f"No names found in {args.source}")
    print(f"Looking up {len(people)} people in: {', '.join(sources)}")

    rows = []
    disabled = set()
    for i, person in enumerate(people, 1):
        given, family, affil = person["given"], person["family"], person["affiliation"]
        row = {"Name": person["name"], "Affiliation": affil}
        print(f"[{i}/{len(people)}] {given} {family}")
        orcid_for_scopus = person["existing"].get("orcid", "")
        updates = {}
        for src in ALL_SOURCES:
            label = {"orcid": "ORCID", "scopus": "Scopus", "scholar": "GoogleScholar"}[src]
            existing = person["existing"].get(ID_KEYS[src], "")
            row[f"{label}_existing"] = existing
            if src not in sources or src in disabled or (existing and not args.recheck):
                row[label], row[f"{label}_match"], row[f"{label}_candidates"] = "", "skipped", ""
                continue
            try:
                if src == "scopus":
                    cands = lookup_scopus(given, family, affil, args, orcid=orcid_for_scopus)
                else:
                    cands = LOOKUPS[src](given, family, affil, args)
                found, conf = decide(cands)
                row[label], row[f"{label}_match"], row[f"{label}_candidates"] = found, conf, describe(cands)
            except Exception as exc:  # network errors, Scholar blocking, bad key
                found, conf = "", "error"
                row[label], row[f"{label}_match"], row[f"{label}_candidates"] = "", "error", str(exc)[:300]
                print(f"   {label} lookup failed: {exc}")
                if src == "scopus" and ("refused" in str(exc) or "quota" in str(exc)):
                    print("   Disabling Scopus for the rest of the run.")
                    disabled.add(src)
                elif src == "scholar" and "MaxTries" in type(exc).__name__ + str(exc):
                    print("   Google Scholar is blocking requests; disabling it for the rest of the run "
                          "(try --scraper-id).")
                    disabled.add(src)
            print(f"   {label}: {found or '-'} ({conf})")
            if src == "orcid" and found and conf in ("high", "medium"):
                orcid_for_scopus = orcid_for_scopus or found
            if found and RANK[conf] >= RANK[args.min_confidence] and (args.overwrite or not existing):
                updates[ID_KEYS[src]] = found
        if args.write and person["folder"] is not None and updates:
            write_personal_data(person["folder"] / PERSONAL_DATA, updates)
            print(f"   wrote {', '.join(f'{k}={v}' for k, v in updates.items())}")
        rows.append(row)

    df = pd.DataFrame(rows)
    out = Path(args.output)
    if out.suffix.lower() == ".csv":
        df.to_csv(out, index=False)
    else:
        df.to_excel(out, index=False)
    print(f"Wrote {out}")
    if args.write and not any(p["folder"] for p in people):
        print("Note: --write only applies when the input is a directory of faculty folders.")


if __name__ == "__main__":
    main()
