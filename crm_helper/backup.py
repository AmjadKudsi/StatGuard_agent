import os
import subprocess


def backup_crm_data(export_dir: str) -> None:
    """
    Naive backup function that uses tar via the shell.

    This is intentionally unsafe: it concatenates a user provided path into a
    shell command string with shell=True.
    """
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # In a real tool this might be a directory with CSV exports.
    source_dir = "/var/tmp/crm_exports"

    # DELIBERATE VULNERABILITY: user-controlled export_dir used in shell command.
    cmd = f"tar -czf {export_dir}/crm_backup.tgz {source_dir}"
    subprocess.call(cmd, shell=True)  # Bandit should flag this (B602/B605).
