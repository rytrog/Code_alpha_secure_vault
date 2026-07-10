# SentinelX Constants

# Roles
ROLE_ADMIN = "admin"
ROLE_USER = "user"
ALL_ROLES = [ROLE_ADMIN, ROLE_USER]

# Vault Categories
VAULT_CATEGORIES = ["note", "password", "api_key", "document", "banking", "credential", "image"]

# Severity Levels
SEVERITY_SAFE = "safe"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"
SEVERITY_CRITICAL = "critical"

SEVERITY_LEVELS = [SEVERITY_SAFE, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL]

# Threat Score Ranges
THREAT_RANGES = {
    SEVERITY_SAFE: (0, 30),
    SEVERITY_MEDIUM: (31, 60),
    SEVERITY_HIGH: (61, 80),
    SEVERITY_CRITICAL: (81, 100),
}

# Attack Types
ATTACK_TYPES = [
    "keyword_injection",
    "boolean_injection",
    "comment_injection",
    "time_based_injection",
    "system_function_injection",
    "encoded_payload",
    "union_injection",
    "stacked_query",
]

# Actions
ACTION_ALLOWED = "allowed"
ACTION_BLOCKED = "blocked"

# Report Types
REPORT_DAILY = "daily"
REPORT_WEEKLY = "weekly"
REPORT_CUSTOM = "custom"

# Rate Limit
DEFAULT_RATE_LIMIT = 30
RATE_LIMIT_WINDOW = 60  # seconds

# Password Requirements
MIN_PASSWORD_LENGTH = 8
