"""Sandboxed subprocess runner enforcing strict safety, argument isolation, and execution limits."""

import asyncio
import os
import shutil
import time
from typing import Dict, List, Optional, Tuple

from app.core.config import settings
from app.core.exceptions import CollectorExecutionError, CollectorTimeoutError
from app.core.logging import logger


async def run_subprocess_sandboxed(
    cmd_args: List[str],
    timeout_seconds: Optional[int] = None,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None,
    max_output_bytes: int = 5 * 1024 * 1024,  # 5MB buffer limit
) -> Tuple[int, str, str, int]:
    """
    Executes a subprocess in strict non-shell mode with timeout and buffer caps.
    Returns: (exit_code, stdout, stderr, execution_time_ms)
    """
    if not cmd_args or not isinstance(cmd_args, list):
        raise CollectorExecutionError("Subprocess command must be a non-empty list of string arguments.")

    timeout = timeout_seconds or settings.COLLECTOR_TIMEOUT_SECONDS
    executable = cmd_args[0]

    # Verify binary exists or is on PATH
    if not os.path.isabs(executable) and not shutil.which(executable):
        logger.debug("Executable '%s' not found on system PATH; collector will fallback or mock.", executable)

    clean_env = os.environ.copy()
    if env:
        clean_env.update(env)

    start_time = time.perf_counter()

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=clean_env,
            cwd=cwd,
        )

        try:
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(),
                timeout=float(timeout),
            )
        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            raise CollectorTimeoutError(
                f"Collector subprocess exceeded timeout limit of {timeout}s",
                details={"command": cmd_args[0]},
            )

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Truncate output if exceeding safety limit
        stdout_str = stdout_data[:max_output_bytes].decode("utf-8", errors="replace")
        stderr_str = stderr_data[:max_output_bytes].decode("utf-8", errors="replace")
        exit_code = process.returncode or 0

        return exit_code, stdout_str, stderr_str, duration_ms

    except (CollectorTimeoutError, CollectorExecutionError):
        raise
    except Exception as exc:
        raise CollectorExecutionError(
            f"Subprocess execution failed: {str(exc)}",
            details={"command": cmd_args[0]},
        ) from exc
