from pathlib import Path

from openpyxl import load_workbook

from douzone_quote_bot.purchase_request.generator import generate_purchase_request


ROOT_DIR = Path(__file__).resolve().parents[1]


def test_purchase_request_sample_creates_xlsx(tmp_path: Path) -> None:
    output = tmp_path / "sample_purchase_request.xlsx"

    result = generate_purchase_request(
        input_path=ROOT_DIR / "samples" / "purchase_request.sample.yaml",
        output_path=output,
    )

    assert result == output
    assert output.exists()
    workbook = load_workbook(output, data_only=False)
    worksheet = workbook.active
    assert worksheet["B3"].value == "가상테스트주식회사"
    assert worksheet["B9"].value == "그룹웨어 사용자"
