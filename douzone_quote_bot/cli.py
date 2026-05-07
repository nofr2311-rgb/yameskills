from __future__ import annotations

import argparse
from pathlib import Path

from .purchase_request.generator import generate_purchase_request


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="douzone_quote_bot",
        description="Douzone 업무 산출물 자동화 CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    purchase = subparsers.add_parser(
        "purchase-request",
        help="기존고객사 구매신청서 xlsx 생성",
    )
    purchase.add_argument("--input", required=True, help="YAML 또는 JSON 입력 파일")
    purchase.add_argument(
        "--output",
        help="생성할 xlsx 경로. 생략하면 outputs/ 아래에 자동 생성합니다.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "purchase-request":
        output_path = generate_purchase_request(
            input_path=Path(args.input),
            output_path=Path(args.output) if args.output else None,
        )
        print(f"created: {output_path}")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2
