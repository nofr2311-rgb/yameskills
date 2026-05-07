#!/usr/bin/env python3
"""
HWPX Generator v4 — 실제 한글 양식 기반 문서 생성기

핵심 전략: 한컴오피스 한글에서 만든 실제 양식의 뼈대(header.xml, version.xml,
settings.xml 등 메타 파일)를 그대로 보존하고, section0.xml만 새로 작성한다.
이 방식이 순수 XML 생성보다 호환성이 압도적으로 높다.

사용법:
    python generate_hwpx.py --template report-summary --output result.hwpx
    python generate_hwpx.py --template report-summary --output result.hwpx --json content.json

양식 목록:
    report-full     보고서 기본 양식 (다중 페이지)
    report-summary  보고서 요약 양식 (1페이지)
"""

import zipfile
import json
import sys
import os
from lxml import etree


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")

TEMPLATES = {
    "report-full": os.path.join(ASSETS_DIR, "report-full.hwpx"),
    "report-summary": os.path.join(ASSETS_DIR, "report-summary.hwpx"),
}

# 전체 네임스페이스 선언 (실제 한글 파일에서 추출)
NS_DECL = (
    'xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
    'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" '
    'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
    'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
    'xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" '
    'xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" '
    'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:opf="http://www.idpf.org/2007/opf/" '
    'xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" '
    'xmlns:epub="http://www.idpf.org/2007/ops" '
    'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"'
)


def _escape_xml(text):
    """XML 특수문자 이스케이프."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def extract_secpr(template_path):
    """양식에서 secPr과 colPr을 추출한다."""
    with zipfile.ZipFile(template_path, 'r') as zf:
        sec_data = zf.read("Contents/section0.xml")

    root = etree.fromstring(sec_data)
    first_p = root[0]
    first_run = first_p[0]

    hp_ns = "http://www.hancom.co.kr/hwpml/2011/paragraph"
    secPr = first_run.find(f'{{{hp_ns}}}secPr')
    ctrl = first_run.find(f'{{{hp_ns}}}ctrl')

    secPr_str = etree.tostring(secPr, encoding='unicode') if secPr is not None else ""
    ctrl_str = etree.tostring(ctrl, encoding='unicode') if ctrl is not None else ""

    return secPr_str, ctrl_str


class SectionBuilder:
    """section0.xml을 구성하는 빌더."""

    def __init__(self, secPr_str, ctrl_str):
        self._parts = []
        self._id_counter = 1000000001
        self._tbl_counter = 1000000090
        self._cell_counter = 1000000500

        # 첫 문단: secPr + colPr (필수)
        pid = self._next_id()
        self._parts.append(
            f'  <hp:p id="{pid}" paraPrIDRef="0" styleIDRef="0" '
            f'pageBreak="0" columnBreak="0" merged="0">\n'
            f'    <hp:run charPrIDRef="0">\n'
            f'      {secPr_str}\n'
            f'      {ctrl_str}\n'
            f'    </hp:run>\n'
            f'    <hp:run charPrIDRef="0"><hp:t/></hp:run>\n'
            f'  </hp:p>'
        )

    def _next_id(self):
        pid = self._id_counter
        self._id_counter += 1
        return str(pid)

    def _next_cell_id(self):
        cid = self._cell_counter
        self._cell_counter += 1
        return str(cid)

    def add_paragraph(self, text, charPrIDRef="0", paraPrIDRef="0", styleIDRef="0"):
        """일반 문단 추가."""
        pid = self._next_id()
        escaped = _escape_xml(text)
        self._parts.append(
            f'  <hp:p id="{pid}" paraPrIDRef="{paraPrIDRef}" styleIDRef="{styleIDRef}" '
            f'pageBreak="0" columnBreak="0" merged="0">\n'
            f'    <hp:run charPrIDRef="{charPrIDRef}"><hp:t>{escaped}</hp:t></hp:run>\n'
            f'  </hp:p>'
        )

    def add_empty(self, paraPrIDRef="0"):
        """빈 줄."""
        pid = self._next_id()
        self._parts.append(
            f'  <hp:p id="{pid}" paraPrIDRef="{paraPrIDRef}" styleIDRef="0" '
            f'pageBreak="0" columnBreak="0" merged="0">\n'
            f'    <hp:run charPrIDRef="0"><hp:t/></hp:run>\n'
            f'  </hp:p>'
        )

    def add_heading(self, text, charPrIDRef="7", paraPrIDRef="25", styleIDRef="1"):
        """제목/소제목 문단."""
        self.add_paragraph(text, charPrIDRef=charPrIDRef,
                          paraPrIDRef=paraPrIDRef, styleIDRef=styleIDRef)

    def add_body(self, text, charPrIDRef="14", paraPrIDRef="26", styleIDRef="2"):
        """본문 문단 (들여쓰기)."""
        self.add_paragraph(text, charPrIDRef=charPrIDRef,
                          paraPrIDRef=paraPrIDRef, styleIDRef=styleIDRef)

    def add_table(self, rows, col_widths=None,
                  header_charPr="9", header_paraPr="21", header_borderFill="4",
                  body_charPr="0", body_paraPr="22", body_borderFill="3",
                  table_borderFill="3", row_height=2400):
        """
        표 추가.

        rows: list of list of str. 첫 행이 헤더.
        col_widths: 열 너비 리스트 (합계=48188). None이면 균등 분할.
        """
        ncols = max(len(r) for r in rows)
        nrows = len(rows)

        if col_widths is None:
            base = 48188 // ncols
            col_widths = [base] * ncols
            col_widths[-1] = 48188 - base * (ncols - 1)

        total_height = row_height * nrows
        tbl_id = self._tbl_counter
        self._tbl_counter += 1
        pid = self._next_id()

        parts = []
        parts.append(
            f'  <hp:p id="{pid}" paraPrIDRef="0" styleIDRef="0" '
            f'pageBreak="0" columnBreak="0" merged="0">\n'
            f'    <hp:run charPrIDRef="0">\n'
            f'      <hp:tbl id="{tbl_id}" zOrder="0" numberingType="TABLE" '
            f'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
            f'dropcapstyle="None" pageBreak="CELL" repeatHeader="1" '
            f'rowCnt="{nrows}" colCnt="{ncols}" cellSpacing="0" '
            f'borderFillIDRef="{table_borderFill}" noAdjust="0">\n'
            f'        <hp:sz width="48188" widthRelTo="ABSOLUTE" '
            f'height="{total_height}" heightRelTo="ABSOLUTE" protect="0"/>\n'
            f'        <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" '
            f'allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" '
            f'vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>\n'
            f'        <hp:outMargin left="0" right="0" top="0" bottom="0"/>\n'
            f'        <hp:inMargin left="0" right="0" top="0" bottom="0"/>'
        )

        for ri, row in enumerate(rows):
            is_header = (ri == 0)
            cpr = header_charPr if is_header else body_charPr
            ppr = header_paraPr if is_header else body_paraPr
            bfr = header_borderFill if is_header else body_borderFill

            padded = list(row) + [""] * (ncols - len(row))
            parts.append('        <hp:tr>')
            for ci, cell_text in enumerate(padded):
                cell_id = self._next_cell_id()
                escaped = _escape_xml(cell_text)
                parts.append(
                    f'          <hp:tc name="" header="0" hasMargin="0" protect="0" '
                    f'editable="0" dirty="0" borderFillIDRef="{bfr}">\n'
                    f'            <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" '
                    f'vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" '
                    f'textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">\n'
                    f'              <hp:p id="{cell_id}" paraPrIDRef="{ppr}" styleIDRef="0" '
                    f'pageBreak="0" columnBreak="0" merged="0">\n'
                    f'                <hp:run charPrIDRef="{cpr}"><hp:t>{escaped}</hp:t></hp:run>\n'
                    f'              </hp:p>\n'
                    f'            </hp:subList>\n'
                    f'            <hp:cellAddr colAddr="{ci}" rowAddr="{ri}"/>\n'
                    f'            <hp:cellSpan colSpan="1" rowSpan="1"/>\n'
                    f'            <hp:cellSz width="{col_widths[ci]}" height="{row_height}"/>\n'
                    f'            <hp:cellMargin left="141" right="141" top="0" bottom="0"/>\n'
                    f'          </hp:tc>'
                )
            parts.append('        </hp:tr>')

        parts.append('      </hp:tbl>\n      <hp:t/>\n    </hp:run>\n  </hp:p>')
        self._parts.append("\n".join(parts))

    def build(self):
        """최종 section0.xml 문자열 생성."""
        header = (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
            f'<hs:sec {NS_DECL}>'
        )
        footer = '</hs:sec>'
        body = "\n".join(self._parts)
        return f"{header}\n{body}\n{footer}"


def generate_hwpx(template_path, content_elements, output_path):
    """
    HWPX 문서 생성.

    template_path: 양식 파일 경로
    content_elements: 내용 정의 리스트
        [
            {"type": "heading", "text": "제목"},
            {"type": "body", "text": "본문"},
            {"type": "empty"},
            {"type": "paragraph", "text": "텍스트", "charPr": "0", "paraPr": "0"},
            {"type": "table", "rows": [["A","B"],["1","2"]], "col_widths": [24094,24094]},
        ]
    output_path: 출력 파일 경로
    """
    # 1) secPr 추출
    secPr_str, ctrl_str = extract_secpr(template_path)

    # 2) section0.xml 빌드
    builder = SectionBuilder(secPr_str, ctrl_str)

    for elem in content_elements:
        etype = elem.get("type", "paragraph")
        if etype == "heading":
            builder.add_heading(
                elem["text"],
                charPrIDRef=elem.get("charPr", "7"),
                paraPrIDRef=elem.get("paraPr", "25"),
                styleIDRef=elem.get("styleID", "1"),
            )
        elif etype == "body":
            builder.add_body(
                elem["text"],
                charPrIDRef=elem.get("charPr", "14"),
                paraPrIDRef=elem.get("paraPr", "26"),
                styleIDRef=elem.get("styleID", "2"),
            )
        elif etype == "paragraph":
            builder.add_paragraph(
                elem["text"],
                charPrIDRef=elem.get("charPr", "0"),
                paraPrIDRef=elem.get("paraPr", "0"),
                styleIDRef=elem.get("styleID", "0"),
            )
        elif etype == "empty":
            builder.add_empty(paraPrIDRef=elem.get("paraPr", "0"))
        elif etype == "table":
            builder.add_table(
                elem["rows"],
                col_widths=elem.get("col_widths"),
                header_charPr=elem.get("header_charPr", "9"),
                body_charPr=elem.get("body_charPr", "0"),
                row_height=elem.get("row_height", 2400),
            )

    new_section = builder.build()

    # 3) ZIP 패키징: 양식에서 모든 파일 복사, section0.xml만 교체
    with zipfile.ZipFile(template_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w') as zout:
            for item in zin.infolist():
                if item.filename == "Contents/section0.xml":
                    zout.writestr(item.filename, new_section.encode('utf-8'),
                                 compress_type=zipfile.ZIP_DEFLATED)
                elif item.filename == "mimetype":
                    zout.writestr(item.filename, zin.read(item.filename),
                                 compress_type=zipfile.ZIP_STORED)
                elif item.filename.endswith('.png'):
                    zout.writestr(item.filename, zin.read(item.filename),
                                 compress_type=item.compress_type)
                else:
                    zout.writestr(item.filename, zin.read(item.filename),
                                 compress_type=zipfile.ZIP_DEFLATED)

    return output_path


def zip_replace(src_path, dst_path, replacements):
    """HWPX ZIP 내 모든 XML에서 텍스트 치환 (표 내부 포함)."""
    tmp = dst_path + ".tmp"
    with zipfile.ZipFile(src_path, "r") as zin:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("Contents/") and item.filename.endswith(".xml"):
                    text = data.decode("utf-8")
                    for old, new in replacements.items():
                        text = text.replace(old, new)
                    data = text.encode("utf-8")
                ct = zipfile.ZIP_STORED if item.filename == "mimetype" else zipfile.ZIP_DEFLATED
                zout.writestr(item, data, compress_type=ct)
    if os.path.exists(dst_path):
        os.remove(dst_path)
    os.rename(tmp, dst_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HWPX 문서 생성기")
    parser.add_argument("--template", default="report-summary",
                       choices=list(TEMPLATES.keys()),
                       help="사용할 양식 (기본: report-summary)")
    parser.add_argument("--template-path",
                       help="커스텀 양식 파일 경로 (--template 대신 사용)")
    parser.add_argument("--output", required=True,
                       help="출력 파일 경로")
    parser.add_argument("--json",
                       help="내용 정의 JSON 파일 경로")
    parser.add_argument("--demo", action="store_true",
                       help="데모 문서 생성")
    args = parser.parse_args()

    template = args.template_path or TEMPLATES.get(args.template)
    if not template or not os.path.exists(template):
        print(f"[오류] 양식 파일을 찾을 수 없습니다: {template}")
        sys.exit(1)

    if args.json:
        with open(args.json, 'r', encoding='utf-8') as f:
            content = json.load(f)
    elif args.demo:
        content = [
            {"type": "paragraph", "text": "ERP 도입 제안서",
             "charPr": "16", "paraPr": "21"},
            {"type": "empty"},
            {"type": "paragraph", "text": "더존비즈온 기술영업팀 | 2026. 3. 17.",
             "charPr": "8", "paraPr": "20"},
            {"type": "empty"},
            {"type": "heading", "text": "1. 솔루션 개요"},
            {"type": "empty"},
            {"type": "table", "rows": [
                ["항목", "내용", "비고"],
                ["솔루션명", "Amaranth 10", "클라우드/온프레미스"],
                ["구축기간", "약 3개월", "커스터마이징 별도"],
                ["주요 모듈", "재무/인사/구매/생산", "선택 가능"],
                ["기대효과", "업무 효율화 30%↑", "도입 후 6개월 기준"],
            ]},
            {"type": "empty"},
            {"type": "heading", "text": "2. 도입 기대효과"},
            {"type": "body", "text": "가. 업무 프로세스 표준화를 통한 운영 효율성 향상"},
            {"type": "body", "text": "나. 실시간 데이터 기반 의사결정 체계 구축"},
            {"type": "body", "text": "다. 부서 간 정보 단절 해소 및 협업 강화"},
            {"type": "body", "text": "라. 법규 준수 및 감사 대응력 강화"},
            {"type": "empty"},
            {"type": "heading", "text": "3. 추진 일정"},
            {"type": "body", "text": "가. 1단계(1개월) : 현행 분석 및 요구사항 정의"},
            {"type": "body", "text": "나. 2단계(1개월) : 시스템 설계 및 커스터마이징"},
            {"type": "body", "text": "다. 3단계(1개월) : 테스트, 교육, 안정화 및 Go-Live"},
        ]
    else:
        print("--json 또는 --demo 옵션을 사용하세요.")
        sys.exit(1)

    result = generate_hwpx(template, content, args.output)
    print(f"✅ 생성 완료: {result}")
    print(f"   크기: {os.path.getsize(result)} bytes")
