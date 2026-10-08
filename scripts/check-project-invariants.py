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
    ):
        if required_reference not in agents:
            fail(f"AGENTS.md must reference {required_reference}")


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
        if not default_ids or len(default_ids) != 4:
            fail("the PWA and API must preserve the four explicitly audited default source IDs")
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
        check_workflow_guards(config)
        check_crons(config)
        check_forbidden_files(config)
        check_secret_content(config)
        check_web_parity_and_companion(config)

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
