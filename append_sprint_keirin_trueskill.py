from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import warnings
from types import ModuleType

SCRIPT_DIR = Path(__file__).resolve().parent


def _silence_zipfile_deallocator_noise() -> None:
    """Suppress noisy 'I/O operation on closed file' warnings from ZipFile.__del__."""

    warnings.filterwarnings("ignore", category=ResourceWarning)

    def _ignore_unraisable(unraisable):  # type: ignore[no-untyped-def]
        exc = unraisable.exc_value
        if isinstance(exc, ValueError) and "closed file" in str(exc):
            return
        sys.__unraisablehook__(unraisable)

    sys.unraisablehook = _ignore_unraisable


_silence_zipfile_deallocator_noise()


def _load_local_module(module_name: str, file_name: str) -> ModuleType:
    module_path = SCRIPT_DIR / file_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

keirin = _load_local_module("keirin_trueskill_append", "keirin_trueskill_append.py")
sprint = _load_local_module("sprint_trueskill_append", "sprint_trueskill_append.py")


def main() -> None:
    base = Path(__file__).resolve().parent / "pages"
    workbook_targets = [
        ("Mens", base / "MensRaceResults.xlsm", sprint.MENS_SPRINT_BETA, sprint.MENS_SPRINT_TAU),
        ("Womens", base / "WomensRaceResults.xlsm", sprint.WOMENS_SPRINT_BETA, sprint.WOMENS_SPRINT_TAU),
    ]

    for label, workbook_path, sprint_beta, sprint_tau in workbook_targets:
        if not workbook_path.exists():
            print(f"{label}: skipped missing workbook -> {workbook_path}")
            continue

        try:
            sprint_added, sprint_skipped = sprint.process_workbook(
                workbook_path,
                beta=sprint_beta,
                tau=sprint_tau,
            )
            print(
                f"{label} Sprint: appended {sprint_added}, skipped {sprint_skipped} row(s) in Sprint_Trueskill"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"{label} Sprint: failed -> {exc}")

        try:
            keirin_added, keirin_skipped = keirin.process_workbook(
                workbook_path,
                input_sheet="Keirin",
                output_sheet="Keirin_Trueskill",
                color_scale_exclude=("Strength_of_Field",) if label == "Mens" else (),
            )
            print(
                f"{label} Keirin: appended {keirin_added}, skipped {keirin_skipped} in Keirin_Trueskill"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"{label} Keirin: failed -> {exc}")


if __name__ == "__main__":
    main()