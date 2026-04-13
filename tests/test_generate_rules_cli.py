from pathlib import Path

from src.generate_rules import main


def test_main_supports_custom_log_dir_and_output_dir(tmp_path: Path) -> None:
    log_dir = tmp_path / "input_logs"
    output_dir = tmp_path / "custom_rules"
    tests_dir = tmp_path / "custom_tests"
    log_dir.mkdir()

    (log_dir / "sample.json").write_text(
        '[{"timestamp":"2026-04-10T09:00:00Z","level":"INFO","message":"ok","event":"start","trace_id":"t1"}]',
        encoding="utf-8",
    )

    main(
        [
            "--log-dir",
            str(log_dir),
            "--output-dir",
            str(output_dir),
            "--tests-dir",
            str(tests_dir),
        ]
    )

    assert (output_dir / "generated_tdd_rules.json").exists()
    assert (output_dir / "detected_issues.json").exists()
    assert (output_dir / "remediation_plan.json").exists()
    assert (tests_dir / "test_issue_remediation_generated.py").exists()


def test_main_supports_single_log_file_input(tmp_path: Path) -> None:
    log_file = tmp_path / "sample.json"
    output_dir = tmp_path / "custom_rules"
    tests_dir = tmp_path / "custom_tests"

    log_file.write_text(
        '[{"timestamp":"2026-04-10T09:00:00Z","level":"INFO","message":"ok","event":"start","trace_id":"t1"}]',
        encoding="utf-8",
    )

    main(
        [
            "--log-dir",
            str(log_file),
            "--output-dir",
            str(output_dir),
            "--tests-dir",
            str(tests_dir),
        ]
    )

    assert (output_dir / "generated_tdd_rules.json").exists()
    assert (output_dir / "detected_issues.json").exists()
    assert (output_dir / "remediation_plan.json").exists()
    assert (tests_dir / "test_issue_remediation_generated.py").exists()
