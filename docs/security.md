# OSINT-X Security & Defensive Boundaries

## 1. Ethical & Defensive Mandate

OSINT-X is engineered solely for defensive cybersecurity operations, authorized attack-surface mapping, and digital-footprint research.

### Prohibited Functionality
The platform strictly **excludes**:
- Credential harvesting, stuffing, or cracking.
- Password extraction or decryption.
- Vulnerability exploitation or payload execution.
- Arbitrary command execution or backdoor installation.
- Denial of Service or abusive port flooding.
- Unauthorized scanning of non-consenting targets.

---

## 2. Target Validation & Authorization

- **Safe Target Validation**: All input targets (emails, usernames, domains, IPs, URLs) are validated against strict regex patterns and domain allowlists/denylists before any collector runs.
- **Authorization Check**: Infrastructure-level active probing (HTTP probing, port probing, DNS brute-forcing) requires an explicit boolean flag confirming authorization from the target owner.
- **Private Network Blocking**: Scanning private RFC 1918 / loopback ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `::1`) is blocked by default in production mode to avoid SSRF attacks against internal infrastructure.

---

## 3. Subprocess Execution Sandbox

When invoking underlying OSINT CLI utilities:
1. **No Shell Invocations**: `subprocess.run(..., shell=True)` is **strictly prohibited**. All commands are invoked using explicit argument arrays `[executable, arg1, arg2]`.
2. **Input Sanitization**: User input is strictly sanitized and passed as distinct array arguments, never interpolated into command strings.
3. **Execution Timeouts**: Every subprocess is assigned a strict timeout (e.g., 180s) to prevent runaway processes.
4. **Output Buffering Limits**: Subprocess output streams are capped to prevent memory exhaustion (DoS).
5. **No Secret Leakage**: API tokens and database passwords are redacted from application logs, error traces, and report files.
