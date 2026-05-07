#!/usr/bin/env python3
"""
더존비즈온 고객사 유지보수 내역서 HWPX 생성기
사용법: python generate_report.py --template <이전달.hwpx> --data <data.json> --output <출력.hwpx>
"""

import argparse
import json
import re
import zipfile
import sys


def esc(text: str) -> str:
    """XML 특수문자 이스케이프"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace('\n', ' ')
            .replace('\r', ''))


def find_tbl_end(xml: str, tbl_start: int) -> int:
    depth, i = 0, tbl_start
    while i < len(xml):
        if xml[i:i+7] == '<hp:tbl':
            depth += 1
        elif xml[i:i+8] == '</hp:tbl':
            depth -= 1
            if depth == 0:
                return i + 9
        i += 1
    raise ValueError("hp:tbl 닫는 태그를 찾지 못했습니다.")


def find_para_end(xml: str, text_pos: int) -> int:
    return xml.find('</hp:p>', text_pos) + len('</hp:p>')


# ── 온라인 문의 표 생성 ──────────────────────────────────
def make_inquiry_table(tbl_id: int, date: str, title: str, question: str, answer: str) -> str:
    def left_cell(label: str, row: int) -> str:
        return (
            f'<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="8">'
            f'<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" '
            f'linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
            f'<hp:p id="0" paraPrIDRef="4" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="12"><hp:t>{label}</hp:t></hp:run><hp:run charPrIDRef="0"/>'
            f'</hp:p></hp:subList>'
            f'<hp:cellAddr colAddr="0" rowAddr="{row}"/><hp:cellSpan colSpan="1" rowSpan="1"/>'
            f'<hp:cellSz width="7000" height="0"/>'
            f'<hp:cellMargin left="400" right="400" top="200" bottom="200"/></hp:tc>'
        )

    def right_cell(value: str, row: int) -> str:
        return (
            f'<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="3">'
            f'<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="TOP" '
            f'linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
            f'<hp:p id="0" paraPrIDRef="3" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="13"><hp:t>{esc(value)}</hp:t></hp:run><hp:run charPrIDRef="0"/>'
            f'</hp:p></hp:subList>'
            f'<hp:cellAddr colAddr="1" rowAddr="{row}"/><hp:cellSpan colSpan="1" rowSpan="1"/>'
            f'<hp:cellSz width="46500" height="0"/>'
            f'<hp:cellMargin left="400" right="400" top="200" bottom="200"/></hp:tc>'
        )

    rows_data = [('등록일자', date), ('제목', title), ('문의내용', question), ('답변내용', answer)]
    trs = ''.join(
        f'<hp:tr>{left_cell(lbl, i)}{right_cell(val, i)}</hp:tr>'
        for i, (lbl, val) in enumerate(rows_data)
    )

    tbl = (
        f'<hp:tbl id="{tbl_id}" zOrder="2" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" '
        f'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" '
        f'rowCnt="4" colCnt="2" cellSpacing="0" borderFillIDRef="2" noAdjust="0">'
        f'<hp:sz width="53500" widthRelTo="ABSOLUTE" height="17884" heightRelTo="ABSOLUTE" protect="0"/>'
        f'<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" '
        f'holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" '
        f'vertOffset="0" horzOffset="0"/>'
        f'<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
        f'<hp:inMargin left="540" right="540" top="0" bottom="0"/>'
        f'{trs}</hp:tbl>'
    )
    return (
        f'<hp:p id="0" paraPrIDRef="9" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="0">{tbl}<hp:t/></hp:run>'
        f'</hp:p>'
    )


# ── 유선상담 데이터행 생성 ─────────────────────────────────
def make_phone_cell(col: int, row: int, text: str) -> str:
    return (
        f'<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="6">'
        f'<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="TOP" '
        f'linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
        f'<hp:p id="0" paraPrIDRef="3" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="13"><hp:t>{esc(text)}</hp:t></hp:run><hp:run charPrIDRef="0"/>'
        f'</hp:p></hp:subList>'
        f'<hp:cellAddr colAddr="{col}" rowAddr="{row}"/><hp:cellSpan colSpan="1" rowSpan="1"/>'
        f'<hp:cellSz width="0" height="0"/>'
        f'<hp:cellMargin left="400" right="400" top="200" bottom="200"/></hp:tc>'
    )


def make_phone_tr(row_idx: int, cols: list) -> str:
    tcs = ''.join(make_phone_cell(ci, row_idx, val) for ci, val in enumerate(cols))
    return f'<hp:tr>{tcs}</hp:tr>'


# ── 메인 생성 함수 ────────────────────────────────────────
def generate(template_path: str, data: dict, output_path: str):
    with zipfile.ZipFile(template_path) as z:
        xml = z.read('Contents/section0.xml').decode('utf-8')

    month_label = data['month']          # 예: "03월"
    year_label  = data.get('year', '2026')
    report_date = data['report_date']    # 예: "2026-04-08 (수)"
    prev_month  = data['prev_month']     # 예: "02월"
    online_list = data['online']         # [{date, title, question, answer}, ...]
    phone_list  = data['phone']          # [{no, date, gubun, content, answer, category}, ...]

    # ── 경계 위치 계산
    def find_pos(marker):
        pos = xml.find(marker)
        if pos == -1:
            raise ValueError(f"마커를 찾을 수 없습니다: '{marker}'")
        return pos

    pos_online   = find_pos('온라인 문의내역')
    pos_phone    = find_pos('유선상담 문의내역')
    pos_extra    = find_pos('추가 AS')

    p_online_end  = find_para_end(xml, pos_online)
    p_phone_start = xml.rfind('<hp:p', 0, pos_phone)
    p_phone_end   = find_para_end(xml, pos_phone)
    phone_tbl_s   = xml.find('<hp:tbl', p_phone_end)
    phone_tbl_e   = find_tbl_end(xml, phone_tbl_s)
    p_extra_start = xml.rfind('<hp:p', 0, pos_extra)

    # ── 앞부분: 월/날짜 텍스트 교체
    part_A = xml[:p_online_end]
    part_A = part_A.replace(f'>{year_label}년 {prev_month}<', f'>{year_label}년 {month_label}<')
    # 작성 일시 교체 (형식이 다를 수 있으므로 regex)
    part_A = re.sub(r'>\d{4}-\d{2}-\d{2} \([가-힣]\)<', f'>{report_date}<', part_A)
    part_A = part_A.replace(
        f'>{year_label}년 Amaranth10 {prev_month} 유지보수 문의 내역<',
        f'>{year_label}년 Amaranth10 {month_label} 유지보수 문의 내역<'
    )

    # ── 온라인 문의 표 생성
    part_B = ''
    for i, item in enumerate(online_list):
        part_B += make_inquiry_table(
            3000000001 + i,
            item['date'], item['title'], item['question'], item['answer']
        )

    # ── 유선상담 단락
    part_C = xml[p_phone_start:p_phone_end]

    # ── 유선상담 표: 헤더행 유지 + 데이터행 교체
    phone_tbl_xml = xml[phone_tbl_s:phone_tbl_e]
    first_tr_end  = phone_tbl_xml.find('</hp:tr>') + len('</hp:tr>')
    header_tr     = phone_tbl_xml[phone_tbl_xml.find('<hp:tr>'):first_tr_end]

    new_data_trs = ''.join(
        make_phone_tr(ri + 1, [
            item['no'], item['date'], item['gubun'],
            item['content'], item['answer'], item['category']
        ])
        for ri, item in enumerate(phone_list)
    )

    total_rows = 1 + len(phone_list)
    new_phone_tbl = re.sub(r'rowCnt="\d+"', f'rowCnt="{total_rows}"', phone_tbl_xml, count=1)
    new_phone_tbl = (
        new_phone_tbl[:phone_tbl_xml.find('<hp:tr>') + (first_tr_end - phone_tbl_xml.find('<hp:tr>'))]
        + new_data_trs
        + '</hp:tbl>'
    )

    # 유선상담 표 wrapper
    phone_tbl_para_s = xml.rfind('<hp:p', 0, phone_tbl_s)
    phone_tbl_para_e = xml.find('</hp:p>', phone_tbl_e) + len('</hp:p>')
    wrapper_pre  = xml[phone_tbl_para_s:phone_tbl_s]
    wrapper_post = xml[phone_tbl_e:phone_tbl_para_e]
    part_D = wrapper_pre + new_phone_tbl + wrapper_post

    # ── 추가 AS ~ 끝
    part_E = xml[p_extra_start:]

    new_xml = part_A + part_B + part_C + part_D + part_E

    # ── HWPX 저장
    with zipfile.ZipFile(template_path) as zin:
        with zipfile.ZipFile(output_path, 'w') as zout:
            for item in zin.infolist():
                if item.filename == 'Contents/section0.xml':
                    zout.writestr(item.filename, new_xml.encode('utf-8'),
                                  compress_type=zipfile.ZIP_DEFLATED)
                elif item.filename == 'mimetype':
                    zout.writestr(item.filename, zin.read(item.filename),
                                  compress_type=zipfile.ZIP_STORED)
                else:
                    zout.writestr(item.filename, zin.read(item.filename),
                                  compress_type=item.compress_type)

    print(f"완료: {output_path}")
    print(f"  온라인 문의: {len(online_list)}건")
    print(f"  유선상담: {len(phone_list)}건")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='유지보수 내역서 HWPX 생성기')
    parser.add_argument('--template', required=True, help='이전 달 HWPX 파일 경로')
    parser.add_argument('--data',     required=True, help='JSON 데이터 파일 경로')
    parser.add_argument('--output',   required=True, help='출력 HWPX 파일 경로')
    args = parser.parse_args()

    with open(args.data, encoding='utf-8') as f:
        data = json.load(f)

    generate(args.template, data, args.output)
