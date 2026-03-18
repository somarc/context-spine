#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import shutil
from pathlib import Path

from context_config import default_config_path, load_config, resolve_repo_path
from generated_artifact import GeneratedArtifactSpec, markdown_heading_validator, publish_generated_artifacts
from run_state import finish_run, start_run


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine"


def file_age_days(path: Path) -> float | None:
    if not path.exists():
        return None
    stamp = dt.datetime.fromtimestamp(path.stat().st_mtime)
    return (dt.datetime.now() - stamp).total_seconds() / 86400


def iso_age_days(value: str) -> float | None:
    if not value:
        return None
    try:
        stamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=dt.UTC)
    else:
        stamp = stamp.astimezone(dt.UTC)
    return (dt.datetime.now(dt.UTC) - stamp).total_seconds() / 86400


def latest_matching(directory: Path, pattern: str) -> Path | None:
    files = sorted(path for path in directory.glob(pattern) if path.is_file())
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def latest_run_payload(memory_root: Path, command: str) -> dict | None:
    run_root = memory_root / "runs"
    if not run_root.is_dir():
        return None
    latest_payload: dict | None = None
    latest_stamp = -1.0
    for path in run_root.rglob("*.json"):
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("command") != command:
            continue
        if payload.get("status") == "running":
            continue
        try:
            stamp = path.stat().st_mtime
        except OSError:
            continue
        if stamp > latest_stamp:
            latest_stamp = stamp
            latest_payload = payload
    return latest_payload


def verification_step(run_payload: dict | None, step_name: str) -> dict | None:
    if not run_payload:
        return None
    for step in run_payload.get("extra", {}).get("steps", []):
        if step.get("name") == step_name:
            return step
    return None


def score_for_age(age_days: float | None, *, fresh: int, aging: int, stale: int, missing: int = 0) -> int:
    if age_days is None:
        return missing
    if age_days <= 1:
        return fresh
    if age_days <= 3:
        return aging
    return stale


def format_age(age_days: float | None) -> str:
    if age_days is None:
        return "missing"
    return f"{age_days:.1f} day(s) old"


def score_contract(repo_root: Path, memory_root: Path, config_path: Path, config_error: str) -> tuple[int, list[str], list[str]]:
    score = 0
    details: list[str] = []
    recommendations: list[str] = []

    if config_error:
        details.append(f"Explicit config: load failed ({config_error})")
        recommendations.append("Fix `meta/context-spine/context-spine.json` so the runtime contract is explicit and shared.")
    elif config_path.exists():
        score += 10
        details.append(f"Explicit config: present at {config_path}")
    else:
        details.append("Explicit config: missing")
        recommendations.append("Add `meta/context-spine/context-spine.json` so bootstrap, doctor, score, and upgrade use one contract.")

    baseline = latest_matching(memory_root, "spine-notes-*.md")
    if baseline is not None:
        score += 10
        details.append(f"Baseline note: present ({baseline.name})")
    else:
        details.append("Baseline note: missing")
        recommendations.append("Create a baseline `spine-notes-*.md` note so the repo has a stable reading path.")

    bootstrap = Path(__file__).resolve().parent / "bootstrap.sh"
    if bootstrap.exists():
        score += 5
        details.append("Bootstrap hook: present")
    else:
        details.append("Bootstrap hook: missing")
        recommendations.append("Restore `scripts/context-spine/bootstrap.sh` so repo reopening stays standardized.")

    return score, details, recommendations


def score_recovery(memory_root: Path) -> tuple[int, list[str], list[str]]:
    score = 0
    details: list[str] = []
    recommendations: list[str] = []

    session = latest_matching(memory_root / "sessions", "*-session.md")
    session_age = file_age_days(session) if session else None
    session_score = score_for_age(session_age, fresh=10, aging=7, stale=3)
    score += session_score
    details.append(
        f"Latest session: {session.name if session else 'missing'} ({format_age(session_age)}) -> {session_score}/10"
    )
    if session_score < 7:
        recommendations.append("Refresh or create a current session note so restarts recover active intent quickly.")

    hot_memory = memory_root / "hot-memory-index.md"
    hot_age = file_age_days(hot_memory)
    hot_score = score_for_age(hot_age, fresh=10, aging=7, stale=3)
    score += hot_score
    details.append(f"Hot memory: {format_age(hot_age)} -> {hot_score}/10")
    if hot_score < 7:
        recommendations.append("Regenerate hot memory so bootstrap points to a trustworthy working set.")

    state_html = memory_root / "memory-state.html"
    state_age = file_age_days(state_html)
    state_score = score_for_age(state_age, fresh=5, aging=3, stale=1)
    score += state_score
    details.append(f"Visual state surface: {format_age(state_age)} -> {state_score}/5")
    if state_score < 3:
        recommendations.append("Run `npm run context:state` so humans get a current visual memory surface.")

    return score, details, recommendations


def score_proof(memory_root: Path) -> tuple[int, list[str], list[str]]:
    score = 0
    details: list[str] = []
    recommendations: list[str] = []

    doctor_age = file_age_days(memory_root / "doctor-report.md")
    doctor_score = score_for_age(doctor_age, fresh=5, aging=3, stale=1)
    score += doctor_score
    details.append(f"Doctor report: {format_age(doctor_age)} -> {doctor_score}/5")
    if doctor_score < 3:
        recommendations.append("Run `npm run context:doctor` so hygiene and boundary drift are visible.")

    verify_payload = latest_run_payload(memory_root, "context:verify")
    verify_score = 0
    if verify_payload is None:
        details.append("Latest verify run: missing -> 0/20")
        recommendations.append("Run `npm run context:verify` to capture proof across the critical path, not just ad hoc commands.")
    else:
        started = verify_payload.get("started_at", "")
        status = str(verify_payload.get("status", "unknown"))
        verify_age = iso_age_days(started)
        if status == "success":
            verify_score = score_for_age(verify_age, fresh=20, aging=16, stale=10)
        elif status == "warn":
            verify_score = score_for_age(verify_age, fresh=16, aging=12, stale=8)
        else:
            verify_score = score_for_age(verify_age, fresh=6, aging=4, stale=2)
            recommendations.append("Fix the failing required verify steps before treating the spine as fully trustworthy.")
        score += verify_score
        details.append(f"Latest verify run: {status} ({format_age(verify_age)}) -> {verify_score}/20")

    return score, details, recommendations


def score_retrieval(memory_root: Path) -> tuple[int, list[str], list[str]]:
    score = 0
    details: list[str] = []
    recommendations: list[str] = []
    local_index = memory_root / ".qmd" / "index.sqlite"
    verify_payload = latest_run_payload(memory_root, "context:verify")
    lexical_step = verification_step(verify_payload, "retrieval_lexical")
    embed_step = verification_step(verify_payload, "retrieval_embed")

    if not shutil.which("qmd"):
        score = 6
        details.append("QMD runtime: not installed -> 6/15")
        details.append("Lexical index: unavailable")
        details.append("Vector capability: unavailable")
        recommendations.append("Install QMD when you want repo-local search and cross-note retrieval.")
        return score, details, recommendations

    score += 4
    details.append("QMD runtime: available -> 4/4")

    if local_index.exists():
        score += 6
        details.append("Lexical index: present -> 6/6")
    else:
        details.append("Lexical index: missing -> 0/6")
        recommendations.append("Run `npm run context:update` or `npm run context:setup` to build the repo-local lexical index.")

    embed_points = 0
    if embed_step is None:
        embed_points = 3
        details.append("Vector capability: unverified -> 3/5")
    elif embed_step.get("status") == "success":
        embed_points = 5
        details.append("Vector capability: verified -> 5/5")
    else:
        embed_points = 1
        details.append(f"Vector capability: warned ({embed_step.get('summary', 'No summary recorded.')}) -> 1/5")
        recommendations.append("Keep embeddings optional until the local QMD runtime can complete `context:embed` cleanly.")

    if lexical_step is not None and lexical_step.get("status") != "success":
        details.append(f"Lexical probe warning: {lexical_step.get('summary', 'No summary recorded.')}")
        score = min(score, 6)
        recommendations.append("Fix lexical retrieval before treating repo-local search as operational.")

    score += embed_points
    return score, details, recommendations


def score_legibility(repo_root: Path) -> tuple[int, list[str], list[str]]:
    score = 0
    details: list[str] = []
    recommendations: list[str] = []

    adr_count = len(list((repo_root / "docs" / "adr").glob("*.md")))
    runbook_count = len(list((repo_root / "docs" / "runbooks").glob("*.md")))
    diagram_count = len(list((repo_root / ".agent" / "diagrams").glob("*.html")))

    docs_points = 5 if adr_count and runbook_count else 2 if (adr_count or runbook_count) else 0
    diagram_points = 5 if diagram_count else 0
    score += docs_points + diagram_points

    details.append(f"Decision and runbook surfaces: {adr_count} ADR(s), {runbook_count} runbook(s) -> {docs_points}/5")
    details.append(f"Visual explainers: {diagram_count} HTML file(s) -> {diagram_points}/5")

    if docs_points < 5:
        recommendations.append("Keep ADRs and runbooks both present so architecture and operations stay legible.")
    if diagram_points < 5:
        recommendations.append("Add or refresh visual explainers for system shape and operating boundaries.")

    return score, details, recommendations


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def main():
    parser = argparse.ArgumentParser(description="Score Context Spine strength across contract, recovery, proof, retrieval, and legibility.")
    parser.add_argument("--root", default="", help="Override memory root directory")
    parser.add_argument("--out", default="", help="Output scorecard path")
    args = parser.parse_args()

    repo_root = default_repo_root()
    config_path = default_config_path(repo_root)
    config_error = ""
    try:
        config = load_config(repo_root)
    except Exception as exc:
        config = {}
        config_error = str(exc)

    configured_memory_root = default_memory_root(repo_root)
    if not config_error and config:
        configured_memory_root = resolve_repo_path(repo_root, str(config.get("memory_root", configured_memory_root)))

    memory_root = (Path(args.root).expanduser() if args.root else configured_memory_root).resolve()
    run_handle = start_run(
        repo_root,
        memory_root,
        "context:score",
        args=vars(args),
    )

    contract_score, contract_details, contract_recs = score_contract(repo_root, memory_root, config_path, config_error)
    recovery_score, recovery_details, recovery_recs = score_recovery(memory_root)
    proof_score, proof_details, proof_recs = score_proof(memory_root)
    retrieval_score, retrieval_details, retrieval_recs = score_retrieval(memory_root)
    legibility_score, legibility_details, legibility_recs = score_legibility(repo_root)

    total = round(contract_score + recovery_score + proof_score + retrieval_score + legibility_score, 1)
    recommendations = dedupe(contract_recs + recovery_recs + proof_recs + retrieval_recs + legibility_recs)

    lines = [
        "# Memory Scorecard",
        "",
        f"- Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Memory root: {memory_root}",
        "",
        "## Overall Score",
        f"- SSS: {total}/100",
        "",
        "## Score Breakdown",
        f"- Contract clarity: {contract_score}/25",
        f"- Recovery surfaces: {recovery_score}/25",
        f"- Verification proof: {proof_score}/25",
        f"- Retrieval readiness: {retrieval_score}/15",
        f"- Human legibility: {legibility_score}/10",
        "",
        "## Contract Clarity",
        *[f"- {line}" for line in contract_details],
        "",
        "## Recovery Surfaces",
        *[f"- {line}" for line in recovery_details],
        "",
        "## Verification Proof",
        *[f"- {line}" for line in proof_details],
        "",
        "## Retrieval Readiness",
        *[f"- {line}" for line in retrieval_details],
        "",
        "## Human Legibility",
        *[f"- {line}" for line in legibility_details],
        "",
        "## Recommendations",
    ]

    if recommendations:
        lines.extend(f"- {item}" for item in recommendations)
    else:
        lines.append("- No major spine-strength gaps detected.")

    out_path = (Path(args.out).expanduser() if args.out else memory_root / "memory-scorecard.md").resolve()
    try:
        published = publish_generated_artifacts(
            [
                GeneratedArtifactSpec(
                    path=out_path,
                    content="\n".join(lines) + "\n",
                    validator=markdown_heading_validator("# Memory Scorecard"),
                )
            ],
            run_id=run_handle.run_id,
        )
    except Exception as exc:
        finish_run(
            run_handle,
            status="fail",
            summary=f"Failed to publish memory scorecard: {exc}",
            artifacts=[],
            extra={"publication_error": str(exc)},
        )
        print(f"Failed to publish memory scorecard: {exc}")
        return 1

    finish_run(
        run_handle,
        status="success",
        summary=f"Generated memory scorecard with SSS {total}/100.",
        artifacts=[str(item.path) for item in published],
        extra={
            "sss": total,
            "breakdown": {
                "contract_clarity": contract_score,
                "recovery_surfaces": recovery_score,
                "verification_proof": proof_score,
                "retrieval_readiness": retrieval_score,
                "human_legibility": legibility_score,
            },
            "artifact_digests": {str(item.path): item.digest for item in published},
        },
    )
    print(f"Run ID: {run_handle.run_id}")
    print(f"Wrote scorecard to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
