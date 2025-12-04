"""
Simple CLI entry point for the CRM backup helper.

This is intentionally naive and insecure for static analysis experiments.
"""

import argparse

from . import backup, config_loader, api_client, secrets


def main() -> None:
    parser = argparse.ArgumentParser(description="CRM backup and export helper (DEMO ONLY)")
    parser.add_argument("--mode", required=True, help="backup | config | api | eval")
    parser.add_argument("--path", help="Path used by some modes")
    parser.add_argument("--base-url", help="Base URL for CRM API")
    parser.add_argument("--customer-id", help="Customer id for CRM API")
    parser.add_argument("--expr", help="Python expression to evaluate in eval mode")

    args = parser.parse_args()

    if args.mode == "backup":
        if not args.path:
            raise SystemExit("--path is required for backup mode")
        backup.backup_crm_data(args.path)

    elif args.mode == "config":
        if not args.path:
            raise SystemExit("--path is required for config mode")
        cfg = config_loader.load_yaml_config(args.path)
        print("Loaded config keys:", list(cfg.keys()))

    elif args.mode == "api":
        if not args.base_url or not args.customer_id:
            raise SystemExit("--base-url and --customer-id are required for api mode")
        data = api_client.fetch_customer_record(args.base_url, args.customer_id)
        print("Customer:", data.get("name"))

    elif args.mode == "eval":
        # DELIBERATE VULNERABILITY: eval on user input.
        if not args.expr:
            raise SystemExit("--expr is required for eval mode")
        result = eval(args.expr)
        print("Eval result:", result)

    else:
        raise SystemExit(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    main()
