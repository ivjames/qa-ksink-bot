from __future__ import annotations

import os
import subprocess
import sys

TARGETS = {
    "clean": {
        "base_url": "http://localhost:5173",
        "api_url": "http://localhost:8000/api",
    },
    "bugs": {
        "base_url": "http://localhost:5173",
        "api_url": "http://localhost:8000/api",
    },
}


def main() -> int:
    target_name = sys.argv[1] if len(sys.argv) > 1 else "clean"
    target = TARGETS.get(target_name)
    if not target:
        print(f"Unknown target: {target_name}")
        print("Use one of: clean, bugs")
        return 2

    env = os.environ.copy()
    env["BASE_URL"] = env.get("BASE_URL", target["base_url"])
    env["API_URL"] = env.get("API_URL", target["api_url"])
    env["HEADED"] = env.get("HEADED", "true")
    env["SLOW_MO"] = env.get("SLOW_MO", "350")

    command = [sys.executable, "-m", "pytest", "--headed", f"--base-url={env['BASE_URL']}", f"--api-url={env['API_URL']}"]
    print(f"Running QA KSink bot against {target_name}: {env['BASE_URL']} / {env['API_URL']}")
    return subprocess.call(command, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
