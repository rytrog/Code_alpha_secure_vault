import re
import urllib.parse
from ..constants import (
    SEVERITY_SAFE, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL
)


# ── Detection Patterns ──────────────────────────────────────────

KEYWORD_PATTERNS = [
    (r"\bUNION\b", "union_injection", 30),
    (r"\bSELECT\b", "keyword_injection", 20),
    (r"\bDROP\b", "keyword_injection", 40),
    (r"\bDELETE\b", "keyword_injection", 35),
    (r"\bINSERT\b", "keyword_injection", 25),
    (r"\bUPDATE\b", "keyword_injection", 20),
    (r"\bALTER\b", "keyword_injection", 35),
    (r"\bTRUNCATE\b", "keyword_injection", 40),
    (r"\bEXEC\b", "keyword_injection", 35),
    (r"\bCREATE\b", "keyword_injection", 25),
]

BOOLEAN_PATTERNS = [
    (r"\bOR\s+1\s*=\s*1\b", "boolean_injection", 50),
    (r"\bAND\s+1\s*=\s*1\b", "boolean_injection", 45),
    (r"'\s*=\s*'", "boolean_injection", 40),
    (r"\b1\s*=\s*1\b", "boolean_injection", 35),
    (r"'\s*OR\s+'", "boolean_injection", 50),
    (r"\bOR\s+'[^']*'\s*=\s*'[^']*'", "boolean_injection", 55),
]

COMMENT_PATTERNS = [
    (r"--", "comment_injection", 25),
    (r"#", "comment_injection", 20),
    (r"/\*", "comment_injection", 30),
    (r"\*/", "comment_injection", 30),
]

TIME_BASED_PATTERNS = [
    (r"\bSLEEP\s*\(", "time_based_injection", 60),
    (r"\bWAITFOR\s+DELAY\b", "time_based_injection", 65),
    (r"\bBENCHMARK\s*\(", "time_based_injection", 60),
]

SYSTEM_FUNCTION_PATTERNS = [
    (r"\bxp_cmdshell\b", "system_function_injection", 80),
    (r"\bLOAD_FILE\s*\(", "system_function_injection", 70),
    (r"\bINFORMATION_SCHEMA\b", "system_function_injection", 50),
    (r"\bsys\.\b", "system_function_injection", 40),
    (r"\bINTO\s+OUTFILE\b", "system_function_injection", 70),
    (r"\bINTO\s+DUMPFILE\b", "system_function_injection", 70),
]

UNION_SELECT_PATTERNS = [
    (r"\bUNION\s+(ALL\s+)?SELECT\b", "union_injection", 70),
    (r"\bUNION\s+SELECT\s+NULL\b", "union_injection", 75),
]

STACKED_QUERY_PATTERNS = [
    (r";\s*(SELECT|DROP|DELETE|INSERT|UPDATE|CREATE|ALTER)", "stacked_query", 60),
]


def _decode_payload(payload: str) -> str:
    """Decode URL-encoded and hex-encoded payloads."""
    decoded = payload
    try:
        decoded = urllib.parse.unquote(decoded)
        decoded = urllib.parse.unquote(decoded)  # double decode
    except Exception:
        pass
    # Hex decode attempt
    try:
        hex_pattern = re.findall(r"0x([0-9a-fA-F]+)", decoded)
        for h in hex_pattern:
            decoded = decoded.replace(f"0x{h}", bytes.fromhex(h).decode("utf-8", errors="ignore"))
    except Exception:
        pass
    return decoded


def analyze_payload(raw_payload: str) -> dict:
    """
    Analyze a request payload for SQL injection attempts.
    Returns dict with threat_score, severity, attack_type, details.
    """
    if not raw_payload:
        return {
            "threat_score": 0,
            "severity": SEVERITY_SAFE,
            "attack_type": None,
            "is_malicious": False,
            "details": [],
        }

    decoded = _decode_payload(raw_payload)
    upper_payload = decoded.upper()
    total_score = 0
    detected_types = []
    details = []

    all_patterns = (
        KEYWORD_PATTERNS
        + BOOLEAN_PATTERNS
        + COMMENT_PATTERNS
        + TIME_BASED_PATTERNS
        + SYSTEM_FUNCTION_PATTERNS
        + UNION_SELECT_PATTERNS
        + STACKED_QUERY_PATTERNS
    )

    for pattern, attack_type, score in all_patterns:
        if re.search(pattern, upper_payload, re.IGNORECASE):
            total_score += score
            if attack_type not in detected_types:
                detected_types.append(attack_type)
            details.append({
                "pattern": pattern,
                "type": attack_type,
                "score": score,
            })

    # Check for encoded payloads
    if raw_payload != decoded and total_score > 0:
        total_score += 15
        details.append({
            "pattern": "encoded_payload_detected",
            "type": "encoded_payload",
            "score": 15,
        })
        if "encoded_payload" not in detected_types:
            detected_types.append("encoded_payload")

    # Cap at 100
    total_score = min(total_score, 100)

    severity = _score_to_severity(total_score)
    primary_type = detected_types[0] if detected_types else None

    return {
        "threat_score": total_score,
        "severity": severity,
        "attack_type": primary_type,
        "attack_types": detected_types,
        "is_malicious": total_score > 30,
        "details": details,
    }


def _score_to_severity(score: int) -> str:
    if score <= 30:
        return SEVERITY_SAFE
    elif score <= 60:
        return SEVERITY_MEDIUM
    elif score <= 80:
        return SEVERITY_HIGH
    else:
        return SEVERITY_CRITICAL


def scan_request_data(params: dict | None = None, body: str | None = None, path: str = "") -> dict:
    """Scan all parts of a request for SQL injection."""
    combined = ""
    if params:
        combined += " ".join(str(v) for v in params.values()) + " "
    if body:
        combined += body + " "
    if path:
        combined += path

    return analyze_payload(combined.strip())
