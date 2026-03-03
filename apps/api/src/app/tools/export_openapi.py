from __future__ import annotations

import argparse

from app.main import export_openapi


def main() -> None:
    parser = argparse.ArgumentParser(description="Export FastAPI OpenAPI schema")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()
    export_openapi(args.output)


if __name__ == "__main__":
    main()
