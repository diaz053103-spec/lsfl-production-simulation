#!/usr/bin/env python3

import argparse
import subprocess
import sys
import time
from pathlib import Path

CONTAINER_NAME = "lsfl-customer-portal"
BACKUP_FILE = Path(__file__).parent / "backups" / "default.conf"
CONTAINER_CONFIG = "/etc/nginx/conf.d/default.conf"
CONTAINER_BACKUP = "/tmp/lsfl-default.conf.backup"


def run(command, check=True):
    result = subprocess.run(command, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(result.returncode)
    return result


def container_running():
    result = run([
        "docker", "inspect", "-f", "{{.State.Status}}", CONTAINER_NAME
    ])
    return result.stdout.strip() == "running"


def inject_container_failure():
    if not container_running():
        sys.exit("ERROR: Container must be running.")

    run(["docker", "stop", CONTAINER_NAME])
    print("Container failure injected. Recover with: docker compose start web")


def inject_nginx_failure():
    if not container_running():
        sys.exit("ERROR: Container must be running.")

    if not BACKUP_FILE.is_file():
        sys.exit(f"ERROR: Config backup not found: {BACKUP_FILE}")

    # Keep a recovery copy inside the container as well.
    run(["docker", "cp", str(BACKUP_FILE),
         f"{CONTAINER_NAME}:{CONTAINER_BACKUP}"])

    # Install a deliberately invalid NGINX site config.
    broken_config = (
        "server {\n"
        "    listen 80;\n"
        "    this_directive_is_intentionally_invalid;\n"
        "}\n"
    )

    result = run([
        "docker", "exec", "-i", CONTAINER_NAME,
        "sh", "-c", f"cat > {CONTAINER_CONFIG}"
    ], check=False) if False else None

    # Write the test config through stdin without requiring a host temp file.
    result = subprocess.run(
        ["docker", "exec", "-i", CONTAINER_NAME,
         "sh", "-c", f"cat > {CONTAINER_CONFIG}"],
        input=broken_config, capture_output=True, text=True
    )

    if result.returncode != 0:
        sys.exit(result.stderr.strip())

    print("Invalid NGINX config installed for the controlled failure test.")
    print("The running NGINX process may continue serving with its old config.")
    print("To activate the failure, validate/reload only in a controlled test.")
    print("This injector does not force-stop NGINX or leave the portal offline.")



def inject_high_cpu():
    if not container_running():
        sys.exit("ERROR: Container must be running.")
    command = 'yes > /dev/null & p=$!; sleep 10; kill "$p" 2>/dev/null || true'
    run(["docker", "exec", "-d", CONTAINER_NAME, "sh", "-c", command])
    print("CPU workload started; automatic cleanup is scheduled for 10 seconds.")


def inject_high_disk_usage():
    if not container_running():
        sys.exit("ERROR: Container must be running.")

    command = (
        "f=/tmp/lsfl-disk-test.bin; "
        "dd if=/dev/zero of=$f bs=1M count=32 2>/dev/null && "
        "echo 'Temporary 32 MiB disk test file created.'; "
        "sleep 15; "
        "rm -f $f; "
        "echo 'Temporary disk test file removed.'"
    )
    run(["docker", "exec", "-d", CONTAINER_NAME, "sh", "-c", command])
    print("Bounded disk test started; temporary file cleanup is scheduled.")


def inject_health_check_failure():
    script = Path(__file__).resolve().parents[2] / "monitoring" / "health_check.sh"
    if not script.is_file():
        sys.exit(f"ERROR: Health-check script not found: {script}")

    result = run([
        "bash", "-c",
        'curl() { printf "000"; }; source "$1"',
        "_", str(script)
    ], check=False)

    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)

    if result.returncode == 1 and "UNHEALTHY" in output:
        print("PASS: Health-check script detected the simulated failure.")
    else:
        sys.exit("FAIL: Expected UNHEALTHY; check the script output.")


def inject_bad_deployment():
    if not container_running():
        sys.exit("ERROR: Container must be running.")
    if not BACKUP_FILE.is_file():
        sys.exit(f"ERROR: Config backup not found: {BACKUP_FILE}")

    try:
        broken_config = (
            "server {\n"
            "    listen 80;\n"
            "    return 503;\n"
            "}\n"
        )
        result = subprocess.run(
            ["docker", "exec", "-i", CONTAINER_NAME,
             "sh", "-c", f"cat > {CONTAINER_CONFIG}"],
            input=broken_config, capture_output=True, text=True
        )
        if result.returncode != 0:
            sys.exit(result.stderr.strip() or "Could not install test config.")

        result = run(
            ["docker", "exec", CONTAINER_NAME, "nginx", "-t"],
            check=False
        )
        if result.returncode != 0:
            sys.exit("Test deployment failed NGINX validation.")

        result = run(
            ["docker", "exec", CONTAINER_NAME, "nginx", "-s", "reload"],
            check=False
        )
        if result.returncode != 0:
            sys.exit("Could not reload NGINX for the test.")

        time.sleep(1)
        probe = run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "http://localhost:8080"],
            check=False
        )
        status = probe.stdout.strip()
        print(f"Faulty deployment probe: HTTP {status}")
        if status != "503":
            sys.exit("FAIL: Expected HTTP 503 from the test deployment.")
        print("PASS: Faulty deployment was detected.")

    finally:
        print("Rolling back to the known-good configuration...")
        restored = run(
            ["docker", "cp", str(BACKUP_FILE),
             f"{CONTAINER_NAME}:{CONTAINER_CONFIG}"],
            check=False
        )
        if restored.returncode != 0:
            sys.exit("CRITICAL: Restore failed; inspect the container config.")

        check = run(
            ["docker", "exec", CONTAINER_NAME, "nginx", "-t"],
            check=False
        )
        if check.returncode != 0:
            sys.exit("CRITICAL: Restored config failed NGINX validation.")

        reload_result = run(
            ["docker", "exec", CONTAINER_NAME, "nginx", "-s", "reload"],
            check=False
        )
        if reload_result.returncode != 0:
            sys.exit("CRITICAL: Restored config could not be reloaded.")

        time.sleep(1)
        probe = run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "http://localhost:8080"],
            check=False
        )
        status = probe.stdout.strip()
        print(f"Post-rollback portal status: HTTP {status}")
        if status != "200":
            sys.exit("CRITICAL: Portal did not return HTTP 200 after rollback.")
        print("PASS: Known-good config restored; portal is healthy.")


def main():
    parser = argparse.ArgumentParser(
        description="LSFL Production Failure Injection Engine"
    )
    parser.add_argument(
        "--inject",
        required=True,
        choices=[
            "container_failure",
            "nginx_failure",
            "bad_deployment",
            "high_disk_usage",
            "high_cpu",
            "health_check_failure",
        ],
        help="Failure scenario to inject",
    )
    args = parser.parse_args()

    if args.inject == "container_failure":
        inject_container_failure()
    elif args.inject == "nginx_failure":
        inject_nginx_failure()
    elif args.inject == "high_cpu":
        inject_high_cpu()
    elif args.inject == "high_disk_usage":
        inject_high_disk_usage()
    elif args.inject == "health_check_failure":
        inject_health_check_failure()
    elif args.inject == "bad_deployment":
        inject_bad_deployment()
    else:
        sys.exit(
            f"{args.inject} is not implemented yet; no changes made."
        )


if __name__ == "__main__":
    main()
