#!/usr/bin/env python3
"""
PDF 인감 오버레이 스크립트
- 검은 배경 인감 이미지를 빨간색만 추출하여 반투명 처리
- PDF 지정 페이지의 (인) 위치에 오버레이
"""
import argparse
import io
import sys
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter


def extract_red_seal(image_path, alpha=180):
    """인감 이미지 처리. 이미 투명 처리된 PNG는 그대로 사용, 아니면 빨간색 추출."""
    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)

    # 이미 투명 배경 처리된 이미지인지 판별 (투명 픽셀이 30% 이상)
    transparent_ratio = np.sum(data[:, :, 3] == 0) / (data.shape[0] * data.shape[1])
    if transparent_ratio > 0.3:
        return img  # 이미 처리된 이미지

    # 검은 배경 → 빨간색 추출
    r, g, b = data[:, :, 0].astype(float), data[:, :, 1].astype(float), data[:, :, 2].astype(float)
    redness = r - (g + b) / 2.0
    is_seal = (redness > 15) & (r > 40)

    result = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
    result[is_seal, 0] = np.clip(r[is_seal] * 1.5, 0, 255).astype(np.uint8)
    result[is_seal, 1] = np.clip(g[is_seal] * 0.4, 0, 255).astype(np.uint8)
    result[is_seal, 2] = np.clip(b[is_seal] * 0.4, 0, 255).astype(np.uint8)
    result[is_seal, 3] = alpha

    return Image.fromarray(result)


def overlay_seal_on_pdf(
    pdf_path, output_path, seal_image_path,
    page_num=2, x=493, y=100, size=58, alpha=180
):
    """PDF 특정 페이지에 인감 오버레이"""
    # 1) 인감 이미지 처리
    seal_img = extract_red_seal(seal_image_path, alpha=alpha)
    temp_seal = "/tmp/_seal_transparent.png"
    seal_img.save(temp_seal)

    # 2) 원본 PDF 읽기
    reader = PdfReader(pdf_path)
    target_page = reader.pages[page_num - 1]
    page_w = float(target_page.mediabox.width)
    page_h = float(target_page.mediabox.height)

    # 3) 오버레이 PDF 생성
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_w, page_h))
    c.drawImage(temp_seal, x, y, width=size, height=size, mask='auto')
    c.save()
    packet.seek(0)

    overlay_page = PdfReader(packet).pages[0]

    # 4) 합성 및 저장
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i == page_num - 1:
            page.merge_page(overlay_page)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"완료: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF 인감 오버레이")
    parser.add_argument("pdf", help="원본 PDF 경로")
    parser.add_argument("output", help="출력 PDF 경로")
    parser.add_argument("--seal", required=True, help="인감 이미지 경로")
    parser.add_argument("--page", type=int, default=2, help="대상 페이지 (기본: 2)")
    parser.add_argument("--x", type=float, default=493, help="X 좌표 (기본: 493)")
    parser.add_argument("--y", type=float, default=100, help="Y 좌표 (기본: 100)")
    parser.add_argument("--size", type=float, default=58, help="인감 크기 (기본: 58)")
    parser.add_argument("--alpha", type=int, default=180, help="투명도 0-255 (기본: 180)")
    args = parser.parse_args()

    overlay_seal_on_pdf(
        args.pdf, args.output, args.seal,
        page_num=args.page, x=args.x, y=args.y,
        size=args.size, alpha=args.alpha
    )
