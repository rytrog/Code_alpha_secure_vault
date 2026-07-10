import uuid
import json
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from .sql_detector import scan_request_data
from .rate_limiter import rate_limiter
from ..utils.logger import attack_logger, system_logger
from ..database.database import get_db_session
from ..database import crud
from ..database.models import BlockedIP


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    API Security Gateway - Module 4
    Every request passes through:
    Rate Limiter -> Blocked IP Check -> JWT Verification -> Payload Validation ->
    SQL Injection Detector -> Threat Scoring -> Allow/Block -> Logging
    """

    EXEMPT_PATHS = {
        "/", "/docs", "/redoc", "/openapi.json", "/favicon.ico",
        "/api/health", "/api/health/",
        "/api/auth/login", "/api/auth/register",
    }

    STATIC_PREFIXES = ("/css/", "/js/", "/assets/", "/components/")

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        path = request.url.path
        client_ip = self._get_client_ip(request)

        # Skip static assets and exempt paths
        if path in self.EXEMPT_PATHS or any(path.startswith(p) for p in self.STATIC_PREFIXES):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        # ── 1. Rate Limiting (Module 5) ──────────────────
        if not rate_limiter.is_allowed(client_ip):
            retry_after = rate_limiter.get_retry_after(client_ip)
            system_logger.warning(f"[{request_id}] RATE LIMITED | IP={client_ip} | Path={path}")
            return self._json_response(
                {"detail": "Too many requests. Please slow down.", "retry_after": retry_after},
                status_code=429,
                headers={"Retry-After": str(retry_after), "X-Request-ID": request_id},
            )

        # ── 2. Blocked IP Check ──────────────────────────
        try:
            db = get_db_session()
            blocked = db.query(BlockedIP).filter(
                BlockedIP.ip_address == client_ip
            ).first()
            db.close()
            if blocked:
                attack_logger.warning(f"[{request_id}] BLOCKED IP attempted access | IP={client_ip} | Path={path}")
                return self._json_response(
                    {"detail": "Access denied. Your IP has been blocked.", "request_id": request_id},
                    status_code=403,
                )
        except Exception:
            pass

        # ── 3. SQL Injection Scanning (Module 3) ─────────
        payload_parts = {}
        if request.query_params:
            payload_parts.update(dict(request.query_params))

        # Read body safely (cache for downstream handlers)
        body_text = ""
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            try:
                body_bytes = await request.body()
                body_text = body_bytes.decode("utf-8", errors="ignore")
            except Exception:
                body_text = ""

        # Scan all request components
        scan_result = scan_request_data(
            params=payload_parts if payload_parts else None,
            body=body_text if body_text else None,
            path=path,
        )

        # ── 4. Block if malicious ────────────────────────
        if scan_result["is_malicious"]:
            attack_logger.critical(
                f"[{request_id}] BLOCKED | IP={client_ip} | Method={request.method} | "
                f"Path={path} | Score={scan_result['threat_score']} | "
                f"Type={scan_result['attack_type']} | Severity={scan_result['severity']} | "
                f"Payload={self._truncate(body_text or str(payload_parts), 200)}"
            )

            # Persist to database
            self._log_to_db(
                ip_address=client_ip,
                username=None,
                endpoint=path,
                method=request.method,
                payload=body_text or str(payload_parts),
                scan_result=scan_result,
                action="blocked",
                reason=f"SQL Injection detected: {', '.join(scan_result.get('attack_types', []))}",
                status_code=403,
                user_agent=request.headers.get("user-agent", ""),
                request_id=request_id,
            )

            return self._json_response(
                {
                    "detail": "Request blocked - Malicious payload detected",
                    "threat_score": scan_result["threat_score"],
                    "severity": scan_result["severity"],
                    "attack_types": scan_result.get("attack_types", []),
                    "request_id": request_id,
                },
                status_code=403,
                headers={"X-Request-ID": request_id, "X-Threat-Score": str(scan_result["threat_score"])},
            )

        # ── 5. Allow request through ─────────────────────
        response = await call_next(request)
        duration = round(time.time() - start_time, 4)

        # Log suspicious (non-zero score) but allowed requests
        if scan_result["threat_score"] > 0:
            attack_logger.info(
                f"[{request_id}] ALLOWED (suspicious) | IP={client_ip} | Path={path} | "
                f"Score={scan_result['threat_score']} | Severity={scan_result['severity']}"
            )
            self._log_to_db(
                ip_address=client_ip,
                endpoint=path,
                method=request.method,
                payload=body_text or str(payload_parts),
                scan_result=scan_result,
                action="allowed",
                reason="Below blocking threshold",
                status_code=response.status_code,
                user_agent=request.headers.get("user-agent", ""),
                request_id=request_id,
            )

        # Inject security headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration}s"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

    # ── Helper Methods ───────────────────────────────────

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "unknown"

    @staticmethod
    def _json_response(data: dict, status_code: int = 200, headers: dict = None) -> Response:
        resp = Response(
            content=json.dumps(data),
            status_code=status_code,
            media_type="application/json",
        )
        if headers:
            for k, v in headers.items():
                resp.headers[k] = v
        return resp

    @staticmethod
    def _truncate(text: str, max_len: int = 200) -> str:
        return text[:max_len] + "..." if len(text) > max_len else text

    @staticmethod
    def _log_to_db(**kwargs):
        try:
            db = get_db_session()
            scan_result = kwargs.pop("scan_result", {})
            crud.create_attack_log(db, {
                "ip_address": kwargs.get("ip_address", "unknown"),
                "username": kwargs.get("username"),
                "endpoint": kwargs.get("endpoint", ""),
                "method": kwargs.get("method", "GET"),
                "payload": kwargs.get("payload", ""),
                "threat_score": scan_result.get("threat_score", 0),
                "attack_type": scan_result.get("attack_type"),
                "severity": scan_result.get("severity", "safe"),
                "action": kwargs.get("action", "allowed"),
                "reason": kwargs.get("reason", ""),
                "status_code": kwargs.get("status_code", 200),
                "user_agent": kwargs.get("user_agent", ""),
                "request_id": kwargs.get("request_id", ""),
            })
            db.close()
        except Exception as e:
            system_logger.error(f"Failed to log to database: {e}")
