#!/usr/bin/env python3
"""Fail-fast guard for AlexLab Magnetra's repository invariants.

Uses only Python's standard library so it can run before build toolchains are
installed or signing material is materialized.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "project-invariants.json"
STATE_PATH = ROOT / "docs" / "PROJECT_STATE.md"
AGENTS_PATH = ROOT / "AGENTS.md"
ANDROID_GRADLE = ROOT / "app" / "build.gradle.kts"

ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"required file missing: {path.relative_to(ROOT)}")


def load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("config/project-invariants.json is missing")
    except json.JSONDecodeError as exc:
        fail(f"config/project-invariants.json is invalid JSON: {exc}")
    return {}


def nested(data: dict, *keys: str):
    cur = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            fail("missing invariant key: " + ".".join(keys))
            return None
        cur = cur[key]
    return cur


def require_equal(actual, expected, label: str) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, found {actual!r}")


def first_regex(text: str, pattern: str, label: str):
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        fail(f"could not locate {label} in app/build.gradle.kts")
        return None
    return match.group(1)


def check_required_memory_files(config: dict) -> None:
    for path in (STATE_PATH, AGENTS_PATH, ANDROID_GRADLE):
        require_file(path)

    if not STATE_PATH.is_file() or not AGENTS_PATH.is_file():
        return

    state = STATE_PATH.read_text(encoding="utf-8")
    agents = AGENTS_PATH.read_text(encoding="utf-8")

    product_name = nested(config, "project", "product_name")
    repository = nested(config, "project", "repository")
    upstream = nested(config, "project", "upstream_repository")

    for value, label in (
        (product_name, "product name"),
        (repository, "canonical repository"),
        (upstream, "upstream repository"),
    ):
        if value and value not in state:
            fail(f"PROJECT_STATE.md does not mention canonical {label}: {value}")

    for required_reference in (
        "docs/PROJECT_STATE.md",
        "config/project-invariants.json",
        "scripts/check-project-invariants.py",
        "docs/NEXT_CHAT_HANDOFF.md",
    ):
        if required_reference not in agents:
            fail(f"AGENTS.md must reference {required_reference}")

    handoff_rel = nested(config, "delivery", "handoff_document")
    if handoff_rel != "docs/NEXT_CHAT_HANDOFF.md":
        fail("delivery.handoff_document must point to the canonical next-chat handoff")
    else:
        handoff_path = ROOT / handoff_rel
        require_file(handoff_path)
        if handoff_path.is_file():
            handoff = handoff_path.read_text(encoding="utf-8")
            for required in (
                "docs/PROJECT_STATE.md",
                "config/project-invariants.json",
                "https://index.alexlab.media",
                "46",
                "Flud Companion",
                "BTDigg",
            ):
                if required not in handoff:
                    fail(f"handoff missing essential project context: {required}")
    if nested(config, "delivery", "handoff_subordinate_to_repository_truth") is not True:
        fail("new-chat handoff must remain subordinate to current main and canonical checkpoint")


def check_project_identity(config: dict) -> None:
    require_equal(nested(config, "schema_version"), 1, "schema_version")
    require_equal(nested(config, "project", "product_name"), "AlexLab Magnetra", "product name")
    require_equal(
        nested(config, "project", "repository"),
        "Zuzuitu/AlexLab-Magnetra",
        "canonical repository",
    )
    require_equal(
        nested(config, "project", "upstream_repository"),
        "prajwalch/TorrentSearch",
        "upstream repository",
    )
    require_equal(nested(config, "project", "default_branch"), "main", "default branch")
    require_equal(nested(config, "project", "license"), "MIT", "license")

    github_repo = os.environ.get("GITHUB_REPOSITORY")
    if github_repo and github_repo != nested(config, "project", "repository"):
        fail(
            "CI repository does not match project invariant: "
            f"GITHUB_REPOSITORY={github_repo!r}"
        )

    license_path = ROOT / "LICENSE"
    require_file(license_path)
    if license_path.is_file() and "MIT License" not in license_path.read_text(
        encoding="utf-8", errors="replace"
    ):
        fail("LICENSE no longer contains the MIT License baseline")


def check_cost_policy(config: dict) -> None:
    require_equal(
        nested(config, "cost_policy", "unapproved_paid_services_allowed"),
        False,
        "unapproved paid services policy",
    )
    require_equal(
        nested(config, "cost_policy", "max_unapproved_recurring_cost_eur"),
        0,
        "maximum unapproved recurring cost",
    )


def check_android_baseline(config: dict) -> None:
    if not ANDROID_GRADLE.is_file():
        return

    text = ANDROID_GRADLE.read_text(encoding="utf-8")
    expected_app_id = nested(config, "android_baseline", "application_id")
    expected_min_sdk = nested(config, "android_baseline", "min_sdk")
    expected_target_sdk = nested(config, "android_baseline", "target_sdk")
    expected_java = nested(config, "android_baseline", "java_version")

    actual_app_id = first_regex(text, r'applicationId\s*=\s*"([^"]+)"', "applicationId")
    actual_min_sdk = first_regex(text, r'\bminSdk\s*=\s*(\d+)', "minSdk")
    actual_target_sdk = first_regex(text, r'\btargetSdk\s*=\s*(\d+)', "targetSdk")
    actual_source_java = first_regex(
        text,
        r'sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)',
        "Java sourceCompatibility",
    )
    actual_target_java = first_regex(
        text,
        r'targetCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)',
        "Java targetCompatibility",
    )

    if actual_app_id is not None:
        require_equal(actual_app_id, expected_app_id, "Android applicationId")
    if actual_min_sdk is not None:
        require_equal(int(actual_min_sdk), expected_min_sdk, "Android minSdk")
    if actual_target_sdk is not None:
        require_equal(int(actual_target_sdk), expected_target_sdk, "Android targetSdk")
    if actual_source_java is not None:
        require_equal(int(actual_source_java), expected_java, "Java source compatibility")
    if actual_target_java is not None:
        require_equal(int(actual_target_java), expected_java, "Java target compatibility")

    expected_jbr_version = nested(config, "android_baseline", "ci_gradle_daemon_java")
    expected_jbr_vendor = nested(config, "android_baseline", "ci_gradle_daemon_vendor")
    daemon_config = ROOT / "gradle" / "gradle-daemon-jvm.properties"
    require_file(daemon_config)
    if daemon_config.is_file():
        daemon_text = daemon_config.read_text(encoding="utf-8")
        if f"toolchainVersion={expected_jbr_version}" not in daemon_text:
            fail("Gradle daemon JDK version differs from protected CI toolchain")
        if f"toolchainVendor={str(expected_jbr_vendor).upper()}" not in daemon_text:
            fail("Gradle daemon JVM vendor differs from protected CI toolchain")

    expected_variants = nested(config, "android_baseline", "build_variants") or []
    variant_patterns = {
        "debug": r"(?m)^\s*debug\s*\{",
        "release": r"(?m)^\s*release\s*\{",
        "staging": r'create\("staging"\)\s*\{',
    }
    for variant in expected_variants:
        pattern = variant_patterns.get(variant)
        if pattern is None:
            fail(f"guard has no validation rule for configured build variant {variant!r}")
        elif not re.search(pattern, text):
            fail(f"required Android build variant is missing: {variant}")


def check_manual_magnetra_worker_staging(config: dict) -> None:
    """Guard the version-only manual Cloudflare stage, not a production deploy."""
    stage = nested(config, "cloudflare_worker_stage")
    expected = {
        "staged_secret_version_owner_reported": "ce808b27",
        "active_production_version_owner_reported": "a9df4429",
        "active_traffic_owner_reported_percent": 100,
        "manual_version_upload_workflow": ".github/workflows/stage-magnetra-worker.yml",
        "stage_workflow_has_no_deploy_command": True,
        "stage_workflow_has_required_secret_name_checks": True,
        "worker_code_version_uploaded": True,
        "manual_stage_workflow_run_succeeded_owner_screenshot": True,
        "manual_stage_workflow_run_number_owner_screenshot": 1,
        "manual_stage_workflow_branch_owner_screenshot": "main",
        "manual_stage_workflow_duration_seconds_owner_screenshot": 23,
        "new_code_version_cloudflare_id_verified": True,
        "new_code_version_id_verified_from_actions": "249d6767-f4dc-4f4d-bbf7-f57bea2e5554",
        "read_only_version_inspection_workflow": ".github/workflows/inspect-magnetra-cloudflare-version.yml",
        "new_code_version_required_bindings_verified": True,
        "read_only_version_audit_run": 39047958484,
        "read_only_version_audit_result": "PASS",
        "zero_percent_slot_owner_approved": True,
        "zero_percent_slot_owner_approval_date": "2026-10-17",
        "zero_percent_slot_configured": True,
        "zero_percent_slot_run": 39053562983,
        "zero_percent_slot_verified_by_api": True,
        "candidate_e2e_diagnostic_workflow": ".github/workflows/test-magnetra-candidate-e2e.yml",
        "candidate_e2e_diagnostic_executed": True,
        "candidate_e2e_diagnostic_last_run": 39119359606,
        "candidate_e2e_diagnostic_last_result": "SUCCESS_FOCUSED_EZTV29_BTDIGG_SOURCE_TIMEOUT_HTTP_504",
        "candidate_eztv_recent_original_source_positive_samples_discovered": 2,
        "candidate_btdigg_upstream_error_observed": True,
        "candidate_eztv_upstream_error_observed": True,
        "eztv_rate_limit_minimum_gap_seconds": 3,
        "eztv_rate_limit_as_root_cause_confirmed": False,
        "candidate_e2e_focused_gateway_mode_staged": True,
        "candidate_e2e_override_attribution_verified": True,
        "candidate_e2e_html_search_and_magnet_passed": ["oxtorrent", "torrent9"],
        "candidate_eztv_positive_e2e_verified": True,
        "candidate_eztv_positive_e2e_result_count": 29,
        "candidate_eztv_last_success_run": 39119359606,
        "candidate_btdigg_positive_e2e_verified": False,
        "candidate_btdigg_source_timeout_http_504_observed": True,
        "btdigg_differential_workflow": ".github/workflows/diagnose-btdigg-differential.yml",
        "btdigg_differential_executed": False,
        "btdigg_differential_outcome": "PENDING_OWNER_MANUAL_RUN",
        "btdigg_differential_old_first_no_retry": True,
        "btdigg_gateway_code_changed": False,
        "btdigg_source_timeout_fix_verified": False,
        "candidate_btdigg_last_diagnostic_run": 39119359606,
        "candidate_e2e_verified_provider_ids": ["eztvx", "oxtorrent", "torrent9"],
        "candidate_all_46_providers_e2e_verified": False,
        "eztv_min_gap_mitigation_success_observed": True,
        "candidate_btdigg_e2e_observed": True,
        "zero_percent_deployment_workflow": ".github/workflows/configure-magnetra-zero-percent.yml",
        "zero_percent_target_traffic_percent": 0,
        "zero_percent_rollback_traffic_percent": 100,
        "zero_percent_no_fractional_fallback": True,
        "active_100_percent_after_stage_reverified": True,
        "staged_worker_authenticated_test_passed": True,
        "canary_rollout_approved": False,
        "production_worker_promotion_completed": False,
        "worker_code_version_activated": False,
        "requires_binding_review_before_activation": True,
        "rollout_rollback_version_owner_reported": "a9df4429",
        "worker_to_tunnel_authenticated_e2e_confirmed": True,
    }
    if not isinstance(stage, dict):
        fail("Cloudflare staged Worker state is missing.")
        return
    for key, value in expected.items():
        require_equal(stage.get(key), value, "cloudflare_worker_stage." + key)
    btdigg_workflow = ROOT / ".github/workflows/diagnose-btdigg-differential.yml"
    require_file(btdigg_workflow)
    if btdigg_workflow.is_file():
        body = btdigg_workflow.read_text(encoding="utf8")
        for marker in ("workflow_dispatch:", "github.ref == 'refs/heads/main'",
                       "COMPARE_OLD_THEN_CANDIDATE",
                       "Explicit BTDigg diagnostic approval before network use",
                       "python3 scripts/check-project-invariants.py",
                       "python3 scripts/diagnose-btdigg-production-vs-candidate.py"):
            if marker not in body:
                fail("BTDigg read-only diagnostic must be manual with gate: " + marker)
        for forbidden in ("push:", "schedule:", "wrangler versions deploy",
                          "wrangler deploy", "[deploy-pwa]", "curl --request POST"):
            if forbidden in body:
                fail("BTDigg diagnostic must never auto-deploy or post: " + forbidden)
    btdigg_script = ROOT / "scripts/diagnose-btdigg-production-vs-candidate.py"
    require_file(btdigg_script)
    if btdigg_script.is_file():
        source = btdigg_script.read_text(encoding="utf8")
        for marker in ('COMPARE_OLD_THEN_CANDIDATE', 'e2e.check_deployment()',
                       'e2e.check_routing_fingerprint()', 'check_one_version(candidate=False)',
                       'if old_status != "PASS":', 'check_one_version(candidate=True)'):
            if marker not in source:
                fail("BTDigg diagnostic missing fail-closed source gating: " + marker)
        for forbidden in ("subprocess.run(", "urllib.request.urlretrieve",
                          "wrangler versions deploy", "time.sleep("):
            if forbidden in source:
                fail("BTDigg diagnostic must not mutate or retry source requests: " + forbidden)

    candidate_e2e_workflow = ROOT / ".github/workflows/test-magnetra-candidate-e2e.yml"
    require_file(candidate_e2e_workflow)
    if candidate_e2e_workflow.is_file():
        e2e_wf = candidate_e2e_workflow.read_text(encoding="utf8")
        for marker in ("workflow_dispatch:", "github.ref == 'refs/heads/main'",
                       "RUN_READONLY_E2E", "python3 scripts/check-project-invariants.py",
                       "python3 scripts/check-magnetra-candidate-e2e.py",
                       "Mandatory manual approval before any network request",
                       "FOCUSED_GATEWAYS", "MAGNETRA_E2E_SCOPE"):
            if marker not in e2e_wf:
                fail("Candidate E2E approval/diagnostic guard missing: " + marker)
        for forbidden in ("push:", "schedule:", "wrangler deploy",
                          "wrangler versions deploy", "curl --request POST",
                          "npm run deploy", "[deploy-pwa]"):
            if forbidden in e2e_wf:
                fail("Candidate E2E workflow must remain manual, non-deploying: " + forbidden)
    e2e_script = ROOT / "scripts/check-magnetra-candidate-e2e.py"
    require_file(e2e_script)
    if e2e_script.is_file():
        e2e_txt = e2e_script.read_text(encoding="utf8")
        for marker in ('EZTV_ZERO_SAMPLE', 'check_eztv_positive()', 'discover_recent_eztv_ids()',
                       'check_btdigg_observational()'):
            if marker not in e2e_txt:
                fail("Candidate E2E must distinguish valid EZTV zero from positive data: " + marker)
        for marker in ('Cloudflare-Workers-Version-Overrides', 'check_routing_fingerprint()',
                       'check_resolve(provider, items)', 'check_deployment()',
                       'MAGNETRA_E2E_READONLY_APPROVAL', 'EZTV_MIN_GAP_SECONDS',
                       'safe_provider_error_code', 'EZTV_MAX_POSITIVE_SAMPLES'):
            if marker not in e2e_txt:
                fail("Candidate E2E script missing safe gate: " + marker)
        for forbidden in ('subprocess.run(', 'wrangler versions deploy', 'urllib.request.urlretrieve'):
            if forbidden in e2e_txt:
                fail("Candidate E2E script must not deploy or download torrent data: " + forbidden)

    zero_workflow = ROOT / ".github/workflows/configure-magnetra-zero-percent.yml"
    zero_script = ROOT / "scripts/deploy_magnetra_zero_percent.py"
    require_file(zero_workflow)
    require_file(zero_script)
    if zero_workflow.is_file():
        body = zero_workflow.read_text(encoding="utf8")
        for marker in ("workflow_dispatch:", "github.ref == 'refs/heads/main'",
                       "CONFIRM_OLD_100_NEW_0",
                       "python3 scripts/check-project-invariants.py",
                       "python3 scripts/deploy_magnetra_zero_percent.py"):
            if marker not in body:
                fail("zero-percent manual gate missing: " + marker)
        auth_step = body.find("Explicit owner confirmation gate (before any Cloudflare calls)")
        execution_step = body.find("python3 scripts/deploy_magnetra_zero_percent.py")
        if auth_step < 0 or execution_step < 0 or auth_step >= execution_step:
            fail("zero-percent manual approval validation must run before Cloudflare requests")
        if "if: github.ref == 'refs/heads/main' && inputs.confirm_zero_percent" in body:
            fail("zero-percent invalid approval must FAIL clearly, not silently SKIP")
        if "OWNER_CHOICE: ${{ inputs.confirm_zero_percent }}" not in body:
            fail("zero-percent manual approval must use the explicit workflow input")
        for forbidden in ("push:", "schedule:", "wrangler deploy",
                          "[deploy-pwa]"):
            if forbidden in body:
                fail("zero-percent manual workflow has unsafe automatic/deploy marker: " + forbidden)
    if zero_script.is_file():
        script = zero_script.read_text(encoding="utf8")
        for marker in ('VERSION + "@0%"', 'old + "@100%"',
                       '_recover(old)', '"CLOUDFLARE_API_TOKEN"'):
            if marker not in script:
                fail("zero-percent guarded script missing: " + marker)
        if '@0.01%' in script or '@1%' in script:
            fail("zero-percent slot must NEVER substitute positive traffic")

    inspector = ROOT / ".github/workflows/inspect-magnetra-cloudflare-version.yml"
    require_file(inspector)
    if inspector.is_file():
        body = inspector.read_text(encoding="utf8")
        for marker in ("workflow_dispatch:", "github.ref == 'refs/heads/main'",
                       "python3 scripts/check-project-invariants.py",
                       "python3 scripts/inspect_cloudflare_version.py"):
            if marker not in body:
                fail("read-only version inspector missing: " + marker)
        for forbidden in ("wrangler versions upload", "wrangler deploy",
                          "wrangler versions deploy", "curl -X POST", "curl --request POST"):
            if forbidden in body:
                fail("read-only version inspector would mutate Cloudflare: " + forbidden)

    target = ROOT / ".github/workflows/stage-magnetra-worker.yml"
    require_file(target)
    if target.is_file():
        txt = target.read_text(encoding="utf8")
        required = (
            "workflow_dispatch:",
            "github.ref == 'refs/heads/main'",
            "python3 scripts/check-project-invariants.py",
            "wrangler@4.102.0 versions upload",
            "--keep-vars",
            "'BTDIGG_GATEWAY_TOKEN','MAGNETRA_GATEWAY_TOKEN'",
            "--dry-run",
            "zero production traffic",
        )
        for token in required:
            if token not in txt:
                fail("manual Cloudflare staging safety guard missing: " + token)
        forbidden = ("wrangler versions deploy", "wrangler secret put",
                     "wrangler@4.102.0 deploy --config worker/.wrangler-stage-only.jsonc --yes")
        for token in forbidden:
            if token in txt:
                fail("manual Cloudflare stage would activate traffic or credentials: " + token)


def check_workflow_guards(config: dict) -> None:
    command = nested(config, "delivery", "invariant_check_command")
    workflows = nested(config, "delivery", "guarded_workflows") or []

    for relative in workflows:
        path = ROOT / relative
        require_file(path)
        if not path.is_file() or not command:
            continue

        text = path.read_text(encoding="utf-8")
        if "./gradlew" in text and ("distribution: 'jetbrains'" not in text or "java-version: '21'" not in text):
            fail(f"{relative}: missing JBR 21 Gradle daemon setup required by gradle/gradle-daemon-jvm.properties")
        guard_index = text.find(command)
        if guard_index < 0:
            fail(f"{relative}: invariant guard command is missing")
            continue

        sensitive_markers = (
            "./gradlew",
            "npm run build",
            "pnpm build",
            "yarn build",
            "wrangler deploy",
            "pages deploy",
            "base64-to-file@",
        )
        for marker in sensitive_markers:
            marker_index = text.find(marker)
            if marker_index >= 0 and guard_index > marker_index:
                fail(
                    f"{relative}: invariant guard must run before sensitive step containing {marker!r}"
                )

    workflows_dir = ROOT / ".github" / "workflows"
    configured = {str(Path(p)) for p in workflows}
    if workflows_dir.is_dir():
        for path in sorted(workflows_dir.glob("*.y*ml")):
            text = path.read_text(encoding="utf-8")
            has_build_or_deploy = any(
                marker in text
                for marker in ("./gradlew", "npm run build", "pnpm build", "yarn build", "wrangler deploy")
            )
            if has_build_or_deploy:
                relative = str(path.relative_to(ROOT))
                if relative not in configured:
                    fail(
                        f"{relative}: build/deploy workflow is not listed in delivery.guarded_workflows"
                    )


def extract_crons() -> list[str]:
    results: list[str] = []
    workflows_dir = ROOT / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return results
    cron_re = re.compile(r"""\bcron\s*:\s*['"]?([^'"\n#]+)""")
    for path in workflows_dir.glob("*.y*ml"):
        text = path.read_text(encoding="utf-8")
        for match in cron_re.finditer(text):
            results.append(match.group(1).strip())
    return sorted(set(results))


def check_crons(config: dict) -> None:
    allowed = sorted(nested(config, "delivery", "allowed_cron_expressions") or [])
    actual = extract_crons()
    if actual != allowed:
        fail(f"cron schedules differ from invariant: expected {allowed!r}, found {actual!r}")


def iter_repo_files():
    ignored_parts = {".git", ".gradle", "build", "node_modules", "dist", ".idea"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in ignored_parts for part in relative.parts):
            continue
        yield path, relative


def check_forbidden_files(config: dict) -> None:
    forbidden_globs = nested(config, "cleanup", "forbidden_globs") or []

    for path, relative in iter_repo_files():
        rel = relative.as_posix()
        for pattern in forbidden_globs:
            if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(rel, pattern):
                fail(f"forbidden temporary/debug artifact committed: {rel}")
                break

        lower_name = path.name.lower()
        if lower_name == ".env" or (
            lower_name.startswith(".env.") and lower_name not in {".env.example", ".env.sample"}
        ):
            fail(f"real environment file must not be committed: {rel}")

        if path.suffix.lower() in {".jks", ".keystore", ".p12", ".pfx", ".pem", ".key"}:
            fail(f"private key/keystore-like file must not be committed: {rel}")

        if re.fullmatch(r"(service[-_]?account|credentials)([-_.].*)?\.json", lower_name):
            fail(f"credential/service-account file must not be committed: {rel}")


def check_secret_content(config: dict) -> None:
    if not nested(config, "security", "frontend_must_not_contain_secrets"):
        return

    textual_suffixes = {
        ".kt", ".kts", ".java", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml",
        ".md", ".properties", ".toml", ".xml", ".html", ".css", ".py", ".sh", ".txt"
    }

    secret_patterns = [
        ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("GitHub classic token", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
        ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
        ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("Stripe live secret", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b")),
    ]

    for path, relative in iter_repo_files():
        if path.suffix.lower() not in textual_suffixes:
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            fail(f"could not scan {relative.as_posix()}: {exc}")
            continue

        for label, pattern in secret_patterns:
            if pattern.search(text):
                fail(f"possible {label} committed in {relative.as_posix()}")

        if relative.parts and relative.parts[0] == "web":
            if re.search(
                r"\bVITE_[A-Z0-9_]*(?:SECRET|PASSWORD|PRIVATE_KEY|ACCESS_TOKEN)[A-Z0-9_]*\b",
                text,
            ):
                fail(
                    f"frontend references a secret-class VITE_* variable: {relative.as_posix()}"
                )


def check_architecture_roots(config: dict) -> None:
    android_root = nested(config, "architecture", "android_source_root")
    preserve = nested(config, "architecture", "preserve_upstream_android_baseline")
    if preserve is not True:
        fail("architecture.preserve_upstream_android_baseline must remain true")
    if android_root and not (ROOT / android_root).is_dir():
        fail(f"protected Android source root is missing: {android_root}")

    web_root = nested(config, "architecture", "planned_web_source_root")
    worker_root = nested(config, "architecture", "planned_backend_source_root")
    if web_root == android_root or worker_root == android_root:
        fail("PWA/backend roots must remain separate from the protected Android source root")


def check_web_parity_and_companion(config: dict) -> None:
    parity = nested(config, "provider_parity")
    companion = nested(config, "companion")
    if not parity or not companion:
        return

    registry = ROOT / parity["original_registry"]
    catalog = ROOT / parity["web_catalog"]
    source_worker = ROOT / "worker" / "src" / "index.mjs"
    frontend = ROOT / "web" / "app.js"
    web_ci = ROOT / ".github" / "workflows" / "pwa.yml"
    for path in (registry, catalog, source_worker, frontend, web_ci):
        require_file(path)
    if not all(x.is_file() for x in (registry, catalog, source_worker, frontend, web_ci)):
        return

    classes = re.findall(
        r"^\s+([A-Za-z0-9]+)\(networkClient\),$",
        registry.read_text(encoding="utf-8"),
        re.MULTILINE
    )
    expected_ids = set()
    for class_name in classes:
        source = ROOT / "app" / "src" / "main" / "kotlin" / "com" / "prajwalch" / "torrentsearch" / "providers" / (class_name + ".kt")
        require_file(source)
        if not source.is_file():
            continue
        match = re.search(r'override val id\s*=\s*"([^"]+)"', source.read_text(encoding="utf-8"))
        if not match:
            fail("upstream provider has no parseable ID: " + class_name)
        else:
            expected_ids.add(match.group(1))

    raw_catalog = catalog.read_text(encoding="utf-8")
    actual_ids = re.findall(r'^\s+"id": "([^"]+)"', raw_catalog, re.MULTILINE)
    count = parity["required_builtin_count"]
    if len(classes) != count or len(expected_ids) != count:
        fail(f"upstream indexer inventory diverged: expected {count}, registered {len(classes)}, IDs {len(expected_ids)}")
    if len(actual_ids) != count or len(set(actual_ids)) != count:
        fail(f"PWA indexer registry must contain exactly {count} distinct IDs, got {len(actual_ids)}")
    if set(actual_ids) != expected_ids:
        fail(f"PWA indexer registry differs from upstream IDs (missing={sorted(expected_ids-set(actual_ids))}, extra={sorted(set(actual_ids)-expected_ids)})")

    legacy_specs = ROOT / parity.get("legacy_specs_path", "")
    legacy_module = ROOT / "worker" / "src" / "legacy-adapters.mjs"
    provider_impl = ROOT / "worker" / "src" / "providers.mjs"
    selector_worker = ROOT / "worker" / "test" / "selectors.worker.mjs"
    selector_config = ROOT / "worker" / "test" / "wrangler-selector.jsonc"
    for path in (legacy_specs, legacy_module, provider_impl, selector_worker, selector_config):
        require_file(path)
    if legacy_specs.is_file() and provider_impl.is_file():
        legacy_text = legacy_specs.read_text(encoding="utf-8")
        legacy_ids = set(re.findall(r'^  "([^"]+)": \{', legacy_text, re.MULTILINE))
        expected_count = parity.get("legacy_adapter_count")
        if len(legacy_ids) != expected_count:
            fail(f"legacy provider specs count changed: expected {expected_count}, found {len(legacy_ids)}")
        catalog_active = len(re.findall(r'"ported": true', raw_catalog))
        required_active = parity.get("required_executable_adapter_count")
        if catalog_active != required_active:
            fail(f"active provider adapters changed: expected {required_active}, found {catalog_active}")
        if '"ported": false' in raw_catalog and required_active == count:
            fail("an original indexer was silently marked as missing after full-parity port")
        if "legacySearch(id,q,category,fetcher)" not in provider_impl.read_text(encoding="utf-8"):
            fail("provider registry does not attach the legacy adapter implementations")
        if "deferred_magnet_resolution_required" in parity and parity["deferred_magnet_resolution_required"]:
            if not legacy_module.is_file() or "resolveLegacy" not in legacy_module.read_text(encoding="utf-8"):
                fail("deferred magnet resolver has been removed")
    if selector_config.is_file() and selector_worker.is_file() and web_ci.is_file():
        config_text = selector_config.read_text(encoding="utf-8")
        if '"main": "./selectors.worker.mjs"' not in config_text:
            fail("CI selector validation must use dedicated workerd entrypoint, not PWA assets")
        if 'x.checked!==35' not in web_ci.read_text(encoding="utf-8"):
            fail("CI must validate the actual JSON result for all 35 HTML selector adapters")

    recovery = nested(config, "provider_recovery")
    if recovery and recovery.get("eztv_api"):
        eztv = recovery["eztv_api"]
        expected = {
            "host": "https://eztvx.to",
            "upstream_api": "https://eztvx.to/api/get-torrents",
            "metadata_lookup": "https://api.tvmaze.com/search/shows",
            "series_only": True,
            "exact_title_match_required": True,
            "exact_imdb_id_required": True,
            "tvmaze_attribution_required": True,
            "external_api_keys_required": False,
            "fabricated_legacy_html_results_forbidden": True,
        }
        for key, value in expected.items():
            require_equal(eztv.get(key), value, "provider_recovery.eztv_api." + key)
        eztv_module = ROOT / "worker" / "src" / "eztv-official-api.mjs"
        eztv_test = ROOT / "worker" / "test" / "eztv-official-api.test.mjs"
        for path in (eztv_module, eztv_test):
            require_file(path)
        if eztv_module.is_file():
            code = eztv_module.read_text(encoding="utf-8")
            for token in (expected["upstream_api"], expected["metadata_lookup"],
                          "exact.length!==1", "imdb_id", "sourceMagnet"):
                if token not in code:
                    fail("EZTV official API parity or attribution guard missing: " + token)
        if provider_impl.is_file() and 'async eztvx(q,category,fetcher)' not in provider_impl.read_text(encoding="utf-8"):
            fail("EZTV must use the original-source official API adapter")
        if frontend.is_file() and 'href="https://www.tvmaze.com"' not in frontend.parent.joinpath("index.html").read_text(encoding="utf-8"):
            fail("PWA must attribute TVmaze title metadata")
    if recovery:
        recovery_path = ROOT / "worker" / "src" / "provider-recovery.mjs"
        recovery_test = ROOT / "worker" / "test" / "provider-recovery.test.mjs"
        for path in (recovery_path, recovery_test):
            require_file(path)
        if recovery_path.is_file():
            recovery_text = recovery_path.read_text(encoding="utf-8")
            if recovery.get("source_links_must_use_catalog_allowlist") and (
                "PROVIDER_MAP.get(id)" not in recovery_text
                or "target.origin!==expected.origin" not in recovery_text
                or 'target.protocol!=="https:"' not in recovery_text
            ):
                fail("provider recovery links must use exact HTTPS catalog origins")
            if recovery.get("auto_retry_rate_limited_sources") is not False:
                fail("do not automatically retry a rate-limited provider")
            if recovery.get("never_relabel_alternative_results") and "RATE_LIMIT" not in recovery_text:
                fail("source error status classifier is missing")
        if source_worker.is_file() and recovery.get("provider_errors_must_report_code"):
            worker_text_recovery = source_worker.read_text(encoding="utf-8")
            if "classifyProviderError(e)" not in worker_text_recovery or "directSearchUrl(id,q)" not in worker_text_recovery:
                fail("Worker does not expose typed provider errors and exact source recovery URL")
        if frontend.is_file() and recovery.get("clipboard_read_requires_explicit_user_action"):
            frontend_clip = frontend.read_text(encoding="utf-8")
            if ('$("pasteMagnetButton").addEventListener("click"' not in frontend_clip
                    or "navigator.clipboard.readText()" not in frontend_clip):
                fail("clipboard access must be initiated by explicit user interaction")
            if recovery.get("manual_magnets_use_existing_companion_dispatch") and "sendMagnet({magnet}" not in frontend_clip:
                fail("manual clipboard magnet must reuse the approved Companion dispatch path")
        if frontend.is_file() and recovery.get("never_relabel_alternative_results"):
            frontend_recovery = frontend.read_text(encoding="utf-8")
            if "renderProviderErrors" not in frontend_recovery or "Search with available indexers" not in frontend_recovery:
                fail("PWA must provide explicitly attributed alternative search on source failure")

    if recovery and recovery.get("manual_btdigg_import_forbidden"):
        for retired in (
            ROOT / "web" / "btdigg-bridge.js",
            ROOT / "worker" / "test" / "btdigg-browser-import.test.mjs",
            ROOT / "worker" / "test" / "btdigg-three-step-guide.test.mjs",
        ):
            if retired.exists():
                fail("retired BTDigg manual import file must not exist: " + str(retired.relative_to(ROOT)))
        for rel in ("web/index.html", "web/app.js", "web/styles.css", "web/sw.js"):
            source = ROOT / rel
            if source.is_file():
                text = source.read_text(encoding="utf-8")
                if any(x in text for x in (
                    "BTDiggBridge", "btdiggDialog", "btdigg-guide-step",
                    "copyBTDiggBookmarklet", "btdigg-bridge.js"
                )):
                    fail("retired BTDigg manual import UI remains in " + rel)

    pwa_cache = nested(config, "pwa_cache")
    if pwa_cache:
        sw_path = ROOT / "web" / "sw.js"
        require_file(sw_path)
        if sw_path.is_file():
            sw_text = sw_path.read_text(encoding="utf-8")
            if pwa_cache.get("api_requests_never_cached") and 'url.pathname.startsWith("/api/")' not in sw_text:
                fail("service worker must never cache /api/ requests")
            if pwa_cache.get("application_assets_network_first") and (
                'fetch(event.request,{cache:"no-store"})' not in sw_text
                or '"/app.js"' not in sw_text or '"/styles.css"' not in sw_text
            ):
                fail("PWA JavaScript and CSS must use network-first refresh")
            if pwa_cache.get("offline_shell_preserved") and 'caches.match("/")' not in sw_text:
                fail("PWA offline shell fallback must remain available")

    recovery = nested(config, "provider_recovery")
    if recovery and recovery.get("audited_results_selection_separate_from_select_all"):
        audit_module = ROOT / recovery["audit_snapshot_module"]
        require_file(audit_module)
        if audit_module.is_file():
            audit_content = audit_module.read_text(encoding="utf-8")
            if f'workflowRunId: {recovery["audit_source_workflow_run"]}' not in audit_content:
                fail("provider audit snapshot no longer points to the source workflow run")
            if "export const SOURCE_AUDIT" not in audit_content:
                fail("the date-stamped provider audit snapshot was removed")
        default_ids = recovery.get("default_searched_provider_ids", [])
        if not default_ids or len(default_ids) != 5 or default_ids[0] != "btdigg":
            fail("the PWA and API must default to BTDigg first and four audited companion sources")
        else:
            ids_str = ",".join('"' + i + '"' for i in default_ids)
            if "const DEFAULT_IDS=[" + ids_str + "]" not in source_worker.read_text(encoding="utf-8"):
                fail("Worker API default sources diverged from the project invariants")
            if "const preferred=[" + ids_str + "]" not in frontend.read_text(encoding="utf-8"):
                fail("PWA default sources diverged from API/project invariants")
        frontend_content = frontend.read_text(encoding="utf-8")
        if 'p.lastAudit?.state==="results"' not in frontend_content:
            fail("last-audit result selection must exclude sources with unverified uptime")
        if '$("selectAllProviders")' not in frontend_content:
            fail("full all-46 indexer selection must remain independently available")
        if 'state.audit=audit||null' not in frontend_content:
            fail("provider health UI must display the explicit dated audit")
        endpoint_content = source_worker.read_text(encoding="utf-8")
        if "auditFor(p.id)" not in endpoint_content:
            fail("provider API must expose the last known audit source metadata")

    headers_path = ROOT / "worker" / "src" / "request-headers.mjs"
    require_file(headers_path)
    if headers_path.is_file():
        headers_text = headers_path.read_text(encoding="utf-8")
        expected_agent = parity.get("upstream_user_agent")
        if not expected_agent or expected_agent not in headers_text:
            fail("outbound source User-Agent differs from the protected Android baseline")
        if parity.get("max_same_origin_redirects") != 1:
            fail("provider redirect limit must remain exactly 1")
        if "target.origin!==original.origin" not in headers_text or "target.protocol!==\"https:\"" not in headers_text:
            fail("provider redirect helper lost strict origin/HTTPS requirements")
    for source_name in ("legacy-adapters.mjs", "html-adapters.mjs"):
        path = ROOT / "worker" / "src" / source_name
        if path.is_file() and "fetchProviderSameOrigin" not in path.read_text(encoding="utf-8"):
            fail(f"{source_name}: must use the origin-restricted provider request helper")
    worker_text = source_worker.read_text(encoding="utf-8")
    origin = companion["allowed_remote_relay_origin"]
    if f'COMPANION_RELAY_ORIGIN="{origin}"' not in worker_text:
        fail("Flud Companion relay must remain fixed to the approved HTTPS origin")
    if 'crypto.randomUUID()' not in worker_text or '"requestId"' not in worker_text and "requestId:" not in worker_text:
        fail("Companion command must use an idempotent request ID")
    if "checkSameOrigin(request)" not in worker_text:
        fail("Companion API must retain same-origin submission checks")
    if '"/api/resolve"' not in worker_text:
        fail("deferred magnet resolution endpoint missing in Worker")
    if "validateLegacyDetail(provider,details)" not in worker_text:
        fail("deferred magnet resolution lost provider origin allowlisting")
    frontend_text = frontend.read_text(encoding="utf-8")
    if companion.get("command_receipt_polling_required") and "verifyCompanionReceipt" not in frontend_text:
        fail("Companion command acknowledgement polling was removed")
    if companion.get("queued_is_not_delivery_confirmation") and "Shield acknowledged" not in frontend_text:
        fail("Companion UI no longer separates queue acceptance from Shield acknowledgement")
    if 'searchParams.set("token"' in frontend_text or "location.hash=" in frontend_text:
        fail("PWA must not serialize remote Companion credentials into URLs")
    if "python3 scripts/check-project-invariants.py" not in web_ci.read_text(encoding="utf-8"):
        fail("PWA CI must run the invariant gate before JS tests")
    audit_path = ROOT / parity.get("production_audit_script", "")
    require_file(audit_path)
    deploy_workflow = ROOT / ".github" / "workflows" / "deploy-pwa.yml"
    if deploy_workflow.is_file() and parity.get("production_audit_script"):
        expected_audit = "python3 " + parity["production_audit_script"]
        if expected_audit not in deploy_workflow.read_text(encoding="utf-8"):
            fail("explicit production deploy must audit all 46 source search responses")



    deployment = nested(config, "deployment")
    if deployment:
        wrangler = ROOT / "worker" / "wrangler.jsonc"
        deploy_ci = ROOT / ".github" / "workflows" / "deploy-pwa.yml"
        for path in (wrangler, deploy_ci):
            require_file(path)
        if wrangler.is_file():
            wrangler_text = wrangler.read_text(encoding="utf-8")
            domain = deployment["production_domain"]
            if f'"pattern": "{domain}"' not in wrangler_text or '"custom_domain": true' not in wrangler_text:
                fail("Cloudflare Worker must retain the canonical custom domain binding")
        if deploy_ci.is_file():
            deploy_text = deploy_ci.read_text(encoding="utf-8")
            marker = deployment["explicit_commit_marker"]
            if marker not in deploy_text:
                fail("production deploy workflow must require the explicit deploy marker")
            if 'branches: [ "main" ]' not in deploy_text:
                fail("production push deploy must remain limited to main")
            if "CLOUDFLARE_API_TOKEN" not in deploy_text or "CLOUDFLARE_ACCOUNT_ID" not in deploy_text:
                fail("production deploy must use external Cloudflare credentials")
            if "python3 scripts/check-project-invariants.py" not in deploy_text:
                fail("production deploy must run invariants before deployment")


            smoke_cmd = deployment.get("production_smoke_command")
            if not smoke_cmd or smoke_cmd not in deploy_text:
                fail("production deploy must verify live PWA endpoints after publishing")
            elif deploy_text.find(smoke_cmd) <= deploy_text.find("npx --yes wrangler@4.45.4 deploy --config worker/wrangler.jsonc"):
                fail("production smoke must run AFTER deployment, not before")
        smoke_workflow = ROOT / ".github" / "workflows" / "production-smoke.yml"
        smoke_script = ROOT / "scripts" / "check-production-smoke.py"
        for path in (smoke_workflow, smoke_script):
            require_file(path)
        if smoke_workflow.is_file() and deployment.get("production_smoke_command") not in smoke_workflow.read_text(encoding="utf-8"):
            fail("standalone production smoke workflow must execute the canonical check")
        if smoke_script.is_file():
            smoke_text = smoke_script.read_text(encoding="utf-8")
            for endpoint in deployment.get("production_smoke_required_endpoints", []):
                if endpoint not in smoke_text:
                    fail(f"production smoke script must cover endpoint: {endpoint}")



def check_btdigg_residential_gateway(config: dict) -> None:
    """Prevent an accidentally open proxy or a BTDigg source substitution."""
    gateway = nested(config, "btdigg_residential_gateway")
    if not isinstance(gateway, dict):
        return
    expected = {
        "upstream_origin": "https://btdig.com",
        "tunnel_origin": "https://btdigg-rock64.alexlab.media",
        "worker_secret_name": "BTDIGG_GATEWAY_TOKEN",
        "rock64_secret_name": "MAGNETRA_BTDIGG_TOKEN",
        "loopback_listener": "127.0.0.1:8796",
        "max_content_bytes": 3000000,
        "auth_required": True,
        "disabled_without_worker_secret": True,
        "open_proxy_forbidden": True,
        "provider_substitution_forbidden": True,
        "auto_retry_429_forbidden": True,
        "must_not_modify_companion_or_other_providers": True,
        "requires_real_rock64_probe_before_production_activation": True,
    }
    for key, value in expected.items():
        require_equal(gateway.get(key), value, "btdigg_residential_gateway." + key)
    files = [
        ROOT / "worker" / "src" / "btdigg-rock64.mjs",
        ROOT / "rock64" / "btdigg_gateway.py",
        ROOT / "rock64" / "check-btdigg.py",
        ROOT / "rock64" / "magnetra-btdigg.service",
        ROOT / "rock64" / "magnetra-btdigg-tunnel.service",
        ROOT / "rock64" / "test_btdigg_gateway.py",
        ROOT / "rock64" / "install-btdigg.sh",
        ROOT / "rock64" / "README.md",
        ROOT / "worker" / "test" / "btdigg-rock64.test.mjs",
    ]
    for path in files:
        require_file(path)
    if any(not path.is_file() for path in files):
        return
    gateway_py = (ROOT / "rock64" / "btdigg_gateway.py").read_text(encoding="utf-8")
    gateway_js = (ROOT / "worker" / "src" / "btdigg-rock64.mjs").read_text(encoding="utf-8")
    worker = (ROOT / "worker" / "src" / "index.mjs").read_text(encoding="utf-8")
    for required in ("127.0.0.1", "https://btdig.com", "NoRedirect",
                     "hmac.compare_digest", "MIN_SEARCH_INTERVAL = 5",
                     "MAGNETRA_BTDIGG_TOKEN"):
        if required not in gateway_py:
            fail("gateway safety guard missing: " + required)
    for required in ("https://btdigg-rock64.alexlab.media",
                     "BTDIGG_GATEWAY_TOKEN", "redirect:\"manual\"",
                     "source.origin!==\"https://btdig.com\""):
        if required not in gateway_js:
            fail("worker BTDigg tunnel safety guard missing: " + required)
    for required in ("rock64BTDiggFetcher(env)", 'id==="btdigg"&&btdiggFetcher'):
        if required not in worker:
            fail("Worker no longer scopes private gateway to BTDigg alone: " + required)
    pwa_workflow = (ROOT / ".github" / "workflows" / "pwa.yml").read_text(encoding="utf-8")
    if "python3 -m unittest discover -s rock64" not in pwa_workflow:
        fail("CI must exercise Rock64 loopback gateway tests")
    state = STATE_PATH.read_text(encoding="utf-8")
    if "BTDigg Rock64" not in state:
        fail("project state missing Rock64 gateway decision")


def check_eztv_residential_gateway(config: dict) -> None:
    """Never allow the EZTV feature flag to broaden the original source proxy."""
    gw = nested(config, "eztv_residential_gateway")
    if not isinstance(gw, dict):
        return
    expected = {
        "upstream_api": "https://eztvx.to/api/get-torrents",
        "legacy_inactive_worker_origin": "https://eztv-rock64.alexlab.media",
        "dedicated_cloudflare_tunnel_deprecated": True,
        "worker_secret_name": "MAGNETRA_GATEWAY_TOKEN",
        "rock64_secret_name": "MAGNETRA_EZTV_TOKEN",
        "loopback_listener": "127.0.0.1:8797",
        "allowed_provider": "eztvx",
        "max_response_bytes": 1000000,
        "auth_required": True,
        "disabled_without_worker_secret": True,
        "open_proxy_forbidden": True,
        "no_cross_origin_redirects": True,
        "independent_of_btdigg_and_other_services": True,
        "activation_requires_owner_approval": True,
    }
    for key, value in expected.items():
        require_equal(gw.get(key), value, "eztv_residential_gateway." + key)
    required = [
        "worker/src/eztv-rock64.mjs",
        "worker/test/eztv-rock64.test.mjs",
        "rock64/eztv_gateway.py",
        "rock64/test_eztv_gateway.py",
        "rock64/magnetra-eztv.service",
        "rock64/install-eztv.sh",
        "rock64/README_EZTV.md",
    ]
    for p in required:
        require_file(ROOT / p)
    if any(not (ROOT / p).is_file() for p in required):
        return
    worker = (ROOT / "worker/src/index.mjs").read_text(encoding="utf8")
    proxy = (ROOT / "worker/src/eztv-rock64.mjs").read_text(encoding="utf8")
    gateway = (ROOT / "rock64/eztv_gateway.py").read_text(encoding="utf8")
    for phrase in ('id==="eztvx"&&eztvFetcher', 'rock64EZTVFetcher(env)'):
        if phrase not in worker:
            fail("EZTV gateway missing source-scoped Worker integration: " + phrase)
    for phrase in ("MAGNETRA_GATEWAY_TOKEN", "https://magnetra-rock64.alexlab.media",
                   "/v1/eztvx/torrents",
                   "https://eztvx.to/api/get-torrents", "redirect:\"manual\""):
        if phrase not in proxy:
            fail("EZTV Rock64 Worker allowlist/auth is missing: " + phrase)
    if "https://eztv-rock64.alexlab.media" in proxy or "env?.EZTV_GATEWAY_TOKEN" in proxy:
        fail("obsolete per-indexer EZTV Worker route or token must not be activated")
    for phrase in ("127.0.0.1", "https://eztvx.to/api/get-torrents",
                   "MAGNETRA_EZTV_TOKEN", "hmac.compare_digest",
                   "NoRedirect", "ProxyHandler({})"):
        if phrase not in gateway:
            fail("EZTV Rock64 source isolation missing: " + phrase)
    pwa = (ROOT / ".github/workflows/pwa.yml").read_text(encoding="utf8")
    if "rock64/eztv_gateway.py" not in pwa or "test_*.py" not in pwa:
        fail("PWA CI must compile and test EZTV gateway")
    state = STATE_PATH.read_text(encoding="utf8")
    if "EZTV residential gateway" not in state:
        fail("canonical project state must include EZTV residential gateway decision")



def check_shared_magnetra_gateway(config: dict) -> None:
    """Owner requires reuse of the existing Tunnel, not one per indexer."""
    gw = nested(config, "shared_magnetra_gateway")
    expected = {
        "reuse_existing_btdigg_tunnel": True,
        "per_indexer_new_tunnel_forbidden": True,
        "proposed_gateway_origin": "https://magnetra-rock64.alexlab.media",
        "proposed_loopback_listener": "127.0.0.1:8798",
        "gateway_deployed": True,
        "physical_8798_acceptance_passed": True,
        "installer_code_staged": True,
        "read_only_acceptance_code_staged": True,
        "worker_activated": False,
        "dispatcher_code_staged": True,
        "new_tunnel_installed": False,
        "new_dns_route_created": True,
        "public_unauth_https_401_verified": True,
        "rock64_default_ipv4_dns_resolved": True,
        "worker_1042_probe_code_staged": True,
        "worker_1042_git_build_config_staged": True,
        "worker_1042_git_connected": False,
        "worker_1042_live_test_passed": True,
        "worker_1042_live_authenticated_test_passed": False,
        "worker_1042_temporary_worker_cleanup_confirmed": True,
        "worker_secret_name": "MAGNETRA_GATEWAY_TOKEN",
        "allowed_provider_paths": ["/v1/eztvx/torrents", "/v1/oxtorrent/html", "/v1/torrent9/html"],
        "html_8798_implementation_staged": True,
        "html_8798_physical_update_confirmed": True,
        "html_8798_real_source_acceptance_passed": True,
        "html_8798_physical_acceptance_providers": ["oxtorrent", "torrent9"],
        "html_authenticated_worker_e2e_passed": True,
        "html_8798_startup_readiness_patch_staged": True,
        "html_8798_owner_rollback_verified": True,
        "legacy_btdigg_route_must_remain_unchanged": True,
        "authenticated_provider_allowlist_required": True,
        "global_worker_compatibility_changes_forbidden": True,
        "requires_physical_and_dash_verification": True,
        "requires_separate_activation_approval": True,
    }
    for key, expected_value in expected.items():
        require_equal(gw.get(key) if isinstance(gw, dict) else None,
                      expected_value, "shared_magnetra_gateway." + key)
    # A staged 1042 probe MUST remain isolated from the deployed Worker.
    if gw.get("worker_1042_probe_code_staged") is True:
        # The Git-linked temporary Worker must not deploy any production route.
        temporary_config = ROOT / "worker/probes/wrangler.jsonc"
        require_file(temporary_config)
        if temporary_config.is_file():
            try:
                probe_config = json.loads(temporary_config.read_text(encoding="utf8"))
            except (OSError, ValueError):
                fail("temporary 1042 Worker config must be valid JSON")
            else:
                expected_config = {
                    "name": "magnetra-1042-probe",
                    "main": "tunnel-1042-probe.mjs",
                    "compatibility_date": "2026-10-01",
                    "workers_dev": False,
                    "observability": {"enabled": False},
                    "routes": [{"pattern": "magnetra-probe.alexlab.media",
                                "custom_domain": True}],
                }
                if probe_config != expected_config:
                    fail("temporary Worker must retain exactly one reviewed non-production domain")
        for filename in ("worker/probes/tunnel-1042-probe.mjs",
                         "worker/probes/README.md",
                         "worker/test/tunnel-1042-probe.test.mjs"):
            require_file(ROOT / filename)
        index = ROOT / "worker/src/index.mjs"
        if index.is_file() and "tunnel-1042-probe" in index.read_text(encoding="utf8"):
            fail("temporary 1042 probe must not be imported by production Worker")
        probe = ROOT / "worker/probes/tunnel-1042-probe.mjs"
        if probe.is_file():
            src = probe.read_text(encoding="utf8")
            for fragment in ("https://magnetra-rock64.alexlab.media/healthz",
                             "PASS_UNAUTHENTICATED_401", "CLOUDFLARE_1042",
                             "AbortSignal.timeout(8000)"):
                if fragment not in src:
                    fail("staged 1042 probe contract missing: " + fragment)
            for forbidden in ("MAGNETRA_GATEWAY_TOKEN", "BTDIGG_GATEWAY_TOKEN",
                              "global_fetch_strictly_public", "index.alexlab.media"):
                if forbidden in src:
                    fail("staged 1042 probe must not contain: " + forbidden)
    # Owner-authorized, verified shared route is separate from Worker activation.
    # Neither local nor public smoke proves Worker->Tunnel compatibility.
    if (gw.get("gateway_deployed") is True or
            gw.get("physical_8798_acceptance_passed") is True):
        for needed in ("rock64/install-magnetra-gateway.sh",
                       "rock64/check-magnetra-gateway.py",
                       "rock64/test_magnetra_install.py"):
            require_file(ROOT / needed)
        if gw.get("new_tunnel_installed") is not False or gw.get("worker_activated") is not False:
            fail("shared route acceptance must not imply a new tunnel or Worker activation")
    for old in ("rock64/install-eztv-tunnel.sh",
                "rock64/magnetra-eztv-tunnel.service",
                "rock64/test_eztv_tunnel_install.py"):
        if (ROOT / old).exists():
            fail("obsolete per-indexer EZTV tunnel artifact must be removed: " + old)
    for required in ("docs/SHARED_MAGNETRA_GATEWAY.md",
                     "rock64/check-shared-tunnel.sh",
                     "rock64/test_shared_tunnel_preflight.py"):
        require_file(ROOT / required)

    for required in ("rock64/magnetra_gateway.py", "rock64/magnetra-gateway.service",
                     "rock64/test_magnetra_gateway.py", "worker/src/eztv-rock64.mjs",
                     "worker/test/eztv-rock64.test.mjs"):
        require_file(ROOT / required)
    code = ROOT / "rock64/magnetra_gateway.py"
    if code.is_file():
        hub_source = code.read_text(encoding="utf8")
        for fragment in ('BIND = "127.0.0.1"', 'PORT = 8798',
                         'ROUTES = frozenset({"/v1/eztvx/torrents", "/v1/oxtorrent/html", "/v1/torrent9/html"})',
                         'ProxyHandler({})', 'NoRedirect',
                         'MAGNETRA_GATEWAY_TOKEN', 'MAGNETRA_EZTV_TOKEN'):
            if fragment not in hub_source:
                fail("shared dispatcher security contract missing: " + fragment)
    # HTML recovery remains code-staged; existing 8798 service is not yet updated.
    if gw.get("html_8798_implementation_staged") is True:
        for filename in ("rock64/magnetra_html_egress.py",
                         "rock64/test_html_egress.py",
                         "rock64/upgrade-magnetra-gateway.sh",
                         "worker/src/html-rock64.mjs",
                         "worker/test/html-rock64.test.mjs"):
            require_file(ROOT / filename)
        worker = ROOT / "worker/src/index.mjs"
        if worker.is_file():
            content = worker.read_text(encoding="utf8")
            for required in ("rock64HtmlFetcher", "resolveLegacy(provider,details,sourceFetch)"):
                if required not in content:
                    fail("html recovery Worker integration missing: " + required)
    if gw.get("html_8798_startup_readiness_patch_staged") is True:
        for filename in ("rock64/wait-magnetra-8798.py",
                         "rock64/test_wait_magnetra_8798.py"):
            require_file(ROOT / filename)
        path = ROOT / "rock64/upgrade-magnetra-gateway.sh"
        if path.is_file():
            data = path.read_text(encoding="utf8")
            for expected_call in ('wait-magnetra-8798.py" --post-restart',
                                  'wait-magnetra-8798.py" --rollback',
                                  'check-magnetra-html.py"'):
                if expected_call not in data:
                    fail("8798 readiness/rollback contract missing: " + expected_call)
    docs = (ROOT / "docs/SHARED_MAGNETRA_GATEWAY.md")
    if docs.is_file() and "ONE existing Cloudflare Tunnel" not in docs.read_text(encoding="utf8"):
        fail("shared gateway architecture docs must prohibit per-indexer tunnels")


def check_all_provider_recovery(config: dict) -> None:
    """The common recovery plan never silently activates an untested source."""
    plan = nested(config, "provider_recovery_v1")
    expected = {
        "required_original_indexers": 46,
        "planned_indexers": 46,
        "read_only_plan": True,
        "auto_reroute": False,
        "worker_secret_activation": False,
        "production_deployed": False,
        "source_evidence_required": True,
        "existing_verified_gateway_providers": ["btdigg", "eztvx"],
        "physical_403_no_benefit": ["1337x", "bt4g", "extdotto"],
        "physical_redirect_candidates": ["bitsearch", "oxtorrent", "torrent9"],
        "dated_audit_run": 38373699387,
        "html_source_fix_staged": ["oxtorrent", "torrent9"],
        "physical_search_to_detail_magnet_verified": ["oxtorrent", "torrent9"],
    }
    for name, value in expected.items():
        require_equal(plan.get(name) if isinstance(plan, dict) else None,
                      value, "provider_recovery_v1." + name)
    for filename in ("worker/src/recovery-strategy.mjs",
                     "worker/test/recovery-strategy.test.mjs",
                     "scripts/recovery-plan.mjs"):
        require_file(ROOT / filename)
    source = ROOT / "worker/src/recovery-strategy.mjs"
    if source.is_file():
        data = source.read_text(encoding="utf8")
        for required in ('gatewayEligible:false', 'autoReroute:false',
                         'historicalObservedAt:SOURCE_AUDIT.observedAt',
                         'requiresRealSourceProof:true'):
            if required not in data:
                fail("common recovery safety contract missing: " + required)
    for filename in ("worker/src/index.mjs",):
        f = ROOT / filename
        if f.is_file():
            contents = f.read_text(encoding="utf8")
            for required in ('"/api/recovery-plan"', 'recoveryFor(p.id)'):
                if required not in contents:
                    fail("common 46-provider API contract missing: " + required)


def main() -> int:
    for required in (CONFIG_PATH, STATE_PATH, AGENTS_PATH, ANDROID_GRADLE):
        require_file(required)

    config = load_config()
    if config:
        check_project_identity(config)
        check_cost_policy(config)
        check_required_memory_files(config)
        check_architecture_roots(config)
        check_android_baseline(config)
        check_manual_magnetra_worker_staging(config)
        check_workflow_guards(config)
        check_crons(config)
        check_forbidden_files(config)
        check_secret_content(config)
        check_web_parity_and_companion(config)
        check_btdigg_residential_gateway(config)
        check_eztv_residential_gateway(config)
        check_all_provider_recovery(config)
        check_shared_magnetra_gateway(config)

    if ERRORS:
        print("Project invariant check FAILED:", file=sys.stderr)
        for index, error in enumerate(ERRORS, start=1):
            print(f"  {index}. {error}", file=sys.stderr)
        return 1

    print("Project invariant check PASSED")
    print("Protected: identity, cost policy, Android baseline, CI ordering, cron policy, secrets, cleanup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
