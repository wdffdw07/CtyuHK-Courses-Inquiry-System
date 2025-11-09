"""Check layer for filtering courses by allowed list."""
import os
import re
import sqlite3
from shutil import copyfile
from typing import Set, Optional


def load_allowed_codes(path: str) -> Set[str]:
    """Load allowed course codes from a file.
    
    Extracts course-like codes (e.g., CS1102, SDSC3001) from any text/CSV file.
    
    Args:
        path: path to file containing course codes
        
    Returns:
        Set of uppercase course codes
    """
    allowed: Set[str] = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                # extract course-like codes e.g. CS1102, SDSC3001
                for m in re.findall(r"[A-Z]{2,}\d{3,4}", line.upper()):
                    allowed.add(m)
    except Exception:
        return set()
    return allowed


def filter_db_by_allowed(
    db_path: str,
    allowed: Set[str],
    in_place: bool = True,
    verbose: bool = False
) -> str:
    """Remove any course not in 'allowed' from the DB along with related prereqs/exclusions.
    
    Args:
        db_path: path to SQLite database
        allowed: set of allowed course codes
        in_place: if False, creates a filtered copy next to the original with suffix _filtered.db
        verbose: print progress messages
        
    Returns:
        Path to the DB used after filtering
    """
    target = db_path
    if not in_place:
        root, ext = os.path.splitext(db_path)
        target = root + "_filtered" + ext
        try:
            copyfile(db_path, target)
        except Exception:
            target = db_path
    
    try:
        conn = sqlite3.connect(target)
        cur = conn.cursor()
        
        # Clean relations first
        if allowed:
            q_marks = ",".join(["?"] * len(allowed))
            # Keep prerequisites where course_code is in allowed list
            # (prereq_code can be external, so don't filter it)
            cur.execute(
                f"DELETE FROM prerequisites WHERE course_code NOT IN ({q_marks})",
                tuple(allowed)
            )
            # Exclusions: only keep if both codes are in allowed list
            cur.execute(
                f"DELETE FROM exclusions WHERE course_code NOT IN ({q_marks}) OR excluded_code NOT IN ({q_marks})",
                tuple(allowed) + tuple(allowed)
            )
            cur.execute(
                f"DELETE FROM courses WHERE course_code NOT IN ({q_marks})",
                tuple(allowed)
            )
        
        conn.commit()
        conn.close()
        
        if verbose:
            print(f"[check] Filtered DB at: {target} (allowed={len(allowed)})")
    except Exception as e:
        if verbose:
            print(f"[check] Filter DB failed: {e}")
    
    return target
