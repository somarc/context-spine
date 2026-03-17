#!/usr/bin/env python3
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


class ArtifactValidationError(ValueError):
    pass


Validator = Callable[[Path], None]


@dataclass(frozen=True)
class GeneratedArtifactSpec:
    path: Path
    content: str
    validator: Validator | None = None


@dataclass(frozen=True)
class PublishedArtifact:
    path: Path
    digest: str


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "candidate"


def _candidate_path(target: Path, run_id: str) -> Path:
    return target.parent / f".{target.name}.{_slug(run_id)}.candidate"


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_nonempty_text(path: Path) -> None:
    if not path.read_text(encoding="utf-8").strip():
        raise ArtifactValidationError(f"Candidate artifact is empty: {path.name}")


def markdown_heading_validator(expected_heading: str) -> Validator:
    def validate(path: Path) -> None:
        validate_nonempty_text(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            if line.rstrip() != expected_heading:
                raise ArtifactValidationError(
                    f"Expected first heading '{expected_heading}' in {path.name}, found '{line.rstrip()}'"
                )
            return
        raise ArtifactValidationError(f"Candidate artifact has no markdown heading: {path.name}")

    return validate


def validate_json_artifact(path: Path) -> None:
    validate_nonempty_text(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactValidationError(f"Invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(payload, (dict, list)):
        raise ArtifactValidationError(
            f"Expected top-level JSON object or array in {path.name}, found {type(payload).__name__}"
        )


def publish_generated_artifacts(
    specs: Iterable[GeneratedArtifactSpec],
    *,
    run_id: str,
) -> list[PublishedArtifact]:
    prepared: list[tuple[Path, Path, str]] = []
    try:
        for spec in specs:
            target = spec.path.expanduser()
            target.parent.mkdir(parents=True, exist_ok=True)
            candidate = _candidate_path(target, run_id)
            candidate.write_text(spec.content, encoding="utf-8")
            prepared.append((target, candidate, sha256_text(spec.content)))
            if spec.validator is not None:
                spec.validator(candidate)

        published: list[PublishedArtifact] = []
        for target, candidate, digest in prepared:
            os.replace(candidate, target)
            published.append(PublishedArtifact(path=target, digest=digest))
        return published
    except Exception:
        for _, candidate, _ in prepared:
            candidate.unlink(missing_ok=True)
        raise
