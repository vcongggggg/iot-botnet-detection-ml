# -*- coding: utf-8 -*-
"""
Script tái thiết kế và xây dựng Báo cáo Đồ án Cuối kỳ (.docx) hoàn chỉnh 100%
theo đúng quy định của FORM_BAOCAO.pptx và kết luận thẩm định của Muse AI.

Nhóm thực hiện: Nhóm 4
1. Nguyễn Công Minh (0825385889)
2. Ngô Văn Công (0775745371)
"""

import os
import shutil
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
OUT_DOCX_1 = os.path.join(BASE_DIR, "Bao_Cao_Cuoi_Ky_IoT_Botnet_ML_Nhom4.docx")
OUT_DOCX_2 = r"c:\Study\HocKy6\Pentest\Bao_Cao_Cuoi_Ky_IoT_Botnet_ML_Nhom4.docx"


def set_cell_shading(cell, color_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_prefix = p.add_run("Báo cáo Cuối kỳ Học phần Kiểm thử Xâm nhập - Nhóm 4 | Trang ")
    run_prefix.font.name = "Times New Roman"
    run_prefix.font.size = Pt(10)
    run_prefix.font.italic = True
    run_prefix.font.color.rgb = RGBColor(100, 100, 100)

    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")

    r = p.add_run()
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r._r.append(fldChar1)
    r._r.append(instrText)
    r._r.append(fldChar2)
    r._r.append(fldChar3)


def style_document(doc):
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)
        add_page_number_footer(section)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(13)
    normal_style.paragraph_format.line_spacing = 1.35
    normal_style.paragraph_format.space_after = Pt(6)


def add_heading_custom(doc, text, level=1):
    p = doc.add_paragraph()
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x0D, 0x3B, 0x66)
    elif level == 2:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x1D, 0x4E, 0x89)
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.italic = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    return p


def add_body_para(doc, text, bold_prefix=None, justify=True):
    p = doc.add_paragraph()
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(0.8)
    p.paragraph_format.line_spacing = 1.35
    p.paragraph_format.space_after = Pt(6)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(13)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    return p


def add_bullet_para(doc, bold_prefix, text):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(4)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(13)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    return p


def add_styled_table(doc, headers, rows, caption_text=None, col_widths=None):
    if caption_text:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(8)
        p_cap.paragraph_format.space_after = Pt(4)
        r_cap = p_cap.add_run(caption_text)
        r_cap.bold = True
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(12)
        r_cap.font.color.rgb = RGBColor(0x0D, 0x3B, 0x66)

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_cells = table.rows[0].cells
    for idx, h_text in enumerate(headers):
        hdr_cells[idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(hdr_cells[idx], "0D3B66")
        set_cell_margins(hdr_cells[idx], top=110, bottom=110, left=120, right=120)
        p = hdr_cells[idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F4F7FB" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row_cells[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_shading(cell, bg_color)
            set_cell_margins(cell, top=85, bottom=85, left=110, right=110)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(str(val))
            r.font.name = "Times New Roman"
            r.font.size = Pt(11.5)
            if c_idx == 0:
                r.bold = True

    if col_widths:
        for row in table.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Cm(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_figure_with_caption(doc, img_filename, caption_text, width_inches=6.0):
    img_path = os.path.join(ASSETS_DIR, img_filename)
    assert os.path.exists(img_path), f"LỖI CHÍ MẠNG: Tập tin ảnh không tồn tại: {img_path}"

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(10)
    r_cap = p_cap.add_run(caption_text)
    r_cap.italic = True
    r_cap.bold = True
    r_cap.font.name = "Times New Roman"
    r_cap.font.size = Pt(11.5)
    r_cap.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)


def build_complete_word_report():
    print("=" * 76)
    print("  BẮT ĐẦU TÁI THIẾT BÁO CÁO WORD CUỐI KỲ CHUẨN 100% FORM_BAOCAO.pptx")
    print("=" * 76)

    doc = Document()
    style_document(doc)

    # =========================================================================
    # 1. TRANG BÌA (THEO MẪU TRƯỜNG ĐH BÁCH KHOA - ĐH ĐÀ NẴNG)
    # =========================================================================
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_uni.add_run("ĐẠI HỌC ĐÀ NẴNG\nTRƯỜNG ĐẠI HỌC BÁCH KHOA\nKHOA CÔNG NGHỆ THÔNG TIN\n")
    r1.bold = True
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(14)
    r_line = p_uni.add_run("─────────────────────────\n\n\n")
    r_line.bold = True
    r_line.font.name = "Times New Roman"
    r_line.font.size = Pt(14)

    p_type = doc.add_paragraph()
    p_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_type = p_type.add_run("BÁO CÁO ĐỒ ÁN CUỐI KỲ\nHỌC PHẦN: KIỂM THỬ XÂM NHẬP (PENETRATION TESTING)\n\n")
    r_type.bold = True
    r_type.font.name = "Times New Roman"
    r_type.font.size = Pt(15)
    r_type.font.color.rgb = RGBColor(0x0D, 0x3B, 0x66)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_label = p_title.add_run("ĐỀ TÀI:\n")
    r_label.bold = True
    r_label.font.name = "Times New Roman"
    r_label.font.size = Pt(14)
    r_title = p_title.add_run(
        "PHÁT HIỆN VÀ PHÂN LOẠI HÀNH VI MÃ ĐỘC BOTNET\n"
        "TRÊN THIẾT BỊ IoT (MIRAI, HAJIME, TORII)\n"
        "SỬ DỤNG MACHINE LEARNING\n\n"
    )
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = RGBColor(0x99, 0x1B, 0x1B)

    r_sub = p_title.add_run(
        "(Bộ dữ liệu chuẩn: Stratosphere IoT-23 Malware Dataset - 5.696.295 bản ghi Zeek Conn-Log\n"
        "Kèm Hệ thống Giả lập Tấn công - Phòng thủ NIDS/IPS 3 Bên Thời gian thực)\n\n\n"
    )
    r_sub.italic = True
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(12.5)

    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_rows = [
        ("Nhóm thực hiện:", "Nhóm 4"),
        ("Sinh viên thực hiện:", "1. Nguyễn Công Minh (SĐT: 0825385889)\n2. Ngô Văn Công (SĐT: 0775745371)"),
        ("Học phần:", "Kiểm thử xâm nhập (Penetration Testing)"),
        ("Đơn vị đào tạo:", "Khoa Công nghệ Thông tin - Trường Đại học Bách Khoa, ĐH Đà Nẵng")
    ]
    for idx, (k, v) in enumerate(info_rows):
        c0, c1 = info_table.rows[idx].cells[0], info_table.rows[idx].cells[1]
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(13)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(13)
        c0.width = Cm(5.0)
        c1.width = Cm(9.5)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(48)
    r_date = p_date.add_run("Đà Nẵng, Năm 2026")
    r_date.bold = True
    r_date.font.name = "Times New Roman"
    r_date.font.size = Pt(13)

    doc.add_page_break()

    # =========================================================================
    # 2. MỤC LỤC BÁO CÁO
    # =========================================================================
    add_heading_custom(doc, "MỤC LỤC BÁO CÁO", level=1)
    toc_items = [
        ("DANH MỤC CÁC TỪ VIẾT TẮT", "Trang 3"),
        ("DANH MỤC HÌNH ẢNH", "Trang 4"),
        ("DANH MỤC BẢNG BIỂU", "Trang 5"),
        ("MỞ ĐẦU", "Trang 6"),
        ("  1. Tính cấp thiết và lý do chọn đề tài", "Trang 6"),
        ("  2. Mục tiêu của đề tài", "Trang 6"),
        ("  3. Phạm vi và đối tượng nghiên cứu", "Trang 7"),
        ("  4. Nội dung thực hiện của đề tài", "Trang 7"),
        ("  5. Bố cục của báo cáo", "Trang 7"),
        ("CHƯƠNG 1: CƠ SỞ LÝ THUYẾT", "Trang 8"),
        ("  1.1. Giới thiệu tổng quan về đề tài và bài toán an ninh IoT", "Trang 8"),
        ("  1.2. Giới thiệu các lý thuyết liên quan", "Trang 9"),
        ("    1.2.1. Đặc thù kiến trúc mạng IoT và bề mặt tấn công", "Trang 9"),
        ("    1.2.2. Giải phẫu hành vi 3 họ mã độc Botnet IoT: Mirai, Hajime và Torii", "Trang 9"),
        ("    1.2.3. Hệ thống phát hiện xâm nhập mạng (NIDS) và Zeek Conn-Log", "Trang 11"),
        ("    1.2.4. Cơ sở lý thuyết 5 thuật toán Machine Learning phân loại lưu lượng", "Trang 12"),
        ("CHƯƠNG 2: ĐỀ XUẤT MÔ HÌNH VÀ THỰC NGHIỆM", "Trang 14"),
        ("  2.1. Giới thiệu bài toán và Bộ dữ liệu chuẩn Stratosphere IoT-23", "Trang 14"),
        ("  2.2. Đề xuất quy trình tiền xử lý và Chia tách Stratified 80/20 chống Data Leakage", "Trang 16"),
        ("  2.3. Kịch bản thực nghiệm và Thiết lập môi trường huấn luyện", "Trang 18"),
        ("  2.4. Kết quả thực nghiệm và Đối sánh 5 mô hình trên 5.696.295 bản ghi", "Trang 19"),
        ("  2.5. Đánh giá chuyên sâu kết quả kiểm thử độc lập (Confusion Matrix, ROC-AUC, Feature Importance)", "Trang 22"),
        ("CHƯƠNG 3: XÂY DỰNG HỆ THỐNG PHÁT HIỆN VÀ PHÂN LOẠI MÃ ĐỘC BOTNET IoT", "Trang 26"),
        ("  3.1. Giới thiệu về môi trường triển khai và công nghệ sử dụng", "Trang 26"),
        ("  3.2. Các chức năng của hệ thống giả lập Tấn công - Phòng thủ 3 bên", "Trang 27"),
        ("    3.2.1. Chức năng Bên 1: Trạm Kẻ tấn công (Red Team Botnet Console - Cổng 9090)", "Trang 27"),
        ("    3.2.2. Chức năng Bên 2: Trạm Gác AI NIDS / Admin SOC Dashboard (Cổng 5000)", "Trang 28"),
        ("    3.2.3. Chức năng Bên 3: Thiết bị IoT Nạn nhân (Victim Smart Camera - Cổng 8088 & 2323)", "Trang 29"),
        ("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "Trang 31"),
        ("TÀI LIỆU THAM KHẢO", "Trang 32"),
    ]
    add_styled_table(
        doc,
        ["NỘI DUNG ĐỀ MỤC", "VỊ TRÍ THAM CHIẾU"],
        toc_items,
        col_widths=[12.5, 3.5]
    )
    doc.add_page_break()

    # =========================================================================
    # 3. DANH MỤC CÁC TỪ VIẾT TẮT (27 THUẬT NGỮ CHUẨN)
    # =========================================================================
    add_heading_custom(doc, "DANH MỤC CÁC TỪ VIẾT TẮT", level=1)
    abbrev_rows = [
        ("AI", "Artificial Intelligence", "Trí tuệ nhân tạo"),
        ("AUC", "Area Under the Curve", "Diện tích dưới đường cong ROC"),
        ("C&C / C2", "Command and Control", "Máy chủ ra lệnh và điều khiển mã độc"),
        ("CPU", "Central Processing Unit", "Bộ xử lý trung tâm"),
        ("CSV", "Comma-Separated Values", "Định dạng tập tin văn bản phân cách bằng dấu phẩy"),
        ("CTU", "Czech Technical University", "Đại học Kỹ thuật Séc (Đơn vị phát hành IoT-23)"),
        ("DDoS", "Distributed Denial of Service", "Tấn công từ chối dịch vụ phân tán"),
        ("DHT", "Distributed Hash Table", "Bảng băm phân tán (giao thức ngang hàng của Hajime)"),
        ("EDA", "Exploratory Data Analysis", "Phân tích khám phá dữ liệu"),
        ("EFB", "Exclusive Feature Bundling", "Kỹ thuật bó đặc trưng loại trừ trong LightGBM"),
        ("FPR", "False Positive Rate", "Tỷ lệ cảnh báo giả (Báo động nhầm)"),
        ("GOSS", "Gradient-based One-Side Sampling", "Kỹ thuật lấy mẫu đơn phía dựa trên đạo hàm"),
        ("HTTP", "HyperText Transfer Protocol", "Giao thức truyền tải siêu văn bản"),
        ("IDS", "Intrusion Detection System", "Hệ thống phát hiện xâm nhập"),
        ("IoT", "Internet of Things", "Internet vạn vật (Các thiết bị thông minh kết nối mạng)"),
        ("IPS", "Intrusion Prevention System", "Hệ thống ngăn chặn xâm nhập chủ động"),
        ("LAN", "Local Area Network", "Mạng cục bộ"),
        ("LightGBM", "Light Gradient Boosting Machine", "Thuật toán học máy tăng cường độ dốc nhẹ"),
        ("ML", "Machine Learning", "Học máy"),
        ("NIDS", "Network Intrusion Detection System", "Hệ thống phát hiện xâm nhập cấp độ mạng"),
        ("PCAP", "Packet Capture", "Tập tin ghi nhận gói tin mạng thô"),
        ("RCE", "Remote Code Execution", "Thực thi mã từ xa"),
        ("ROC", "Receiver Operating Characteristic", "Đường cong đặc trưng hoạt động của bộ thu"),
        ("SOC", "Security Operations Center", "Trung tâm điều hành và giám sát an ninh mạng"),
        ("SYN", "Synchronize Sequence Numbers", "Cờ đồng bộ hóa mở kết nối trong giao thức TCP"),
        ("TCP/UDP", "Transmission Control / User Datagram Protocol", "Giao thức điều khiển truyền vận / Giao thức gói dữ liệu người dùng"),
        ("XGBoost", "eXtreme Gradient Boosting", "Thuật toán học máy tăng cường độ dốc cực đại"),
    ]
    add_styled_table(
        doc,
        ["TỪ VIẾT TẮT", "TIẾNG ANH", "TIẾNG VIỆT"],
        abbrev_rows,
        caption_text="Bảng 0.1: Danh mục 27 từ viết tắt sử dụng trong báo cáo",
        col_widths=[3.0, 6.2, 6.8]
    )
    doc.add_page_break()

    # =========================================================================
    # 4. DANH MỤC HÌNH ẢNH & DANH MỤC BẢNG BIỂU
    # =========================================================================
    add_heading_custom(doc, "DANH MỤC HÌNH ẢNH", level=1)
    fig_list = [
        ("Hình 1.1", "Kiến trúc tổng thể hệ thống phòng vệ AI NIDS và giả lập tấn công - phòng thủ 3 bên"),
        ("Hình 2.1", "Phân bố nhãn lớp Benign (8,74%) và Malicious (91,26%) trên 5.696.295 bản ghi Stratosphere IoT-23"),
        ("Hình 2.2", "Phân tích khám phá dữ liệu (EDA): Phân bố trạng thái kết nối Zeek (conn_state) theo nhãn"),
        ("Hình 2.3", "Phân bố giao thức tầng giao vận (TCP, UDP, ICMP) theo nhãn Benign vs. Malicious"),
        ("Hình 2.4", "Top 10 cổng đích bị Botnet tấn công nhiều nhất trong bộ dữ liệu Stratosphere IoT-23"),
        ("Hình 2.5", "Phân bố thời lượng phiên kết nối (duration) thang logarithm giữa lưu lượng sạch và mã độc"),
        ("Hình 2.6", "So sánh tải trọng truyền tải (orig_bytes và resp_bytes) thang logarithm giữa Benign và Malicious"),
        ("Hình 2.7", "Phân bố số lượng gói tin gửi từ nguồn (orig_pkts) thể hiện tính chất quét cổng chớp nhoáng"),
        ("Hình 2.8", "Tỷ lệ phân bố các họ mã độc Botnet IoT (Mirai, Hajime, Torii, Kenjiro, Hakai) trong dữ liệu"),
        ("Hình 2.9", "Biểu đồ đối sánh hiệu năng (Accuracy, Precision, Recall, F1) và thời gian huấn luyện 5 mô hình ML"),
        ("Hình 2.10", "Biểu đồ đối sánh thời gian huấn luyện và độ trễ suy luận của 5 mô hình Machine Learning"),
        ("Hình 2.11", "Ma trận nhầm lẫn (Confusion Matrix) của LightGBM trên 1.139.259 dòng kiểm thử độc lập"),
        ("Hình 2.12", "Đường cong ROC và chỉ số AUC đối sánh thực tế cả 5 thuật toán Machine Learning"),
        ("Hình 2.13", "Biểu đồ xếp hạng mức độ đóng góp đặc trưng (Feature Importance) trong mô hình LightGBM"),
        ("Hình 2.14", "Phân tích bất đối xứng lưu lượng mạng giữa gói tin gửi đi và gói tin phản hồi"),
        ("Hình 3.1", "Kết quả thực nghiệm hệ thống giả lập 3 bên (Attacker - AI NIDS Guardian - Victim IoT) thời gian thực"),
    ]
    add_styled_table(
        doc,
        ["SỐ TT", "TIÊU ĐỀ HÌNH ẢNH MINH HỌA"],
        fig_list,
        caption_text="Bảng 0.2: Danh mục 16 hình ảnh minh họa và biểu đồ khoa học 300 DPI",
        col_widths=[3.0, 13.0]
    )

    add_heading_custom(doc, "DANH MỤC BẢNG BIỂU", level=1)
    tbl_list = [
        ("Bảng 1.1", "Bảng đối sánh đặc điểm kỹ thuật, cơ chế lây lan và dấu hiệu mạng của 3 họ Botnet: Mirai, Hajime và Torii"),
        ("Bảng 2.1", "Bảng mô tả chi tiết 21 trường dữ liệu nguyên bản trong Zeek Conn-Log của bộ dữ liệu Stratosphere IoT-23"),
        ("Bảng 2.2", "Thống kê phân bố nhãn Benign và Malicious sau khi chia tách phân tầng Stratified 80/20 (5.696.295 bản ghi)"),
        ("Bảng 2.3", "Bảng tổng hợp kết quả huấn luyện và đánh giá 5 thuật toán Machine Learning trên tập dữ liệu IoT-23"),
        ("Bảng 2.4", "Chi tiết báo cáo phân loại (Classification Report) theo từng lớp của mô hình LightGBM trên 1.139.259 dòng Test"),
        ("Bảng 2.5", "Bảng kết quả tính toán định lượng diện tích dưới đường cong ROC (ROC-AUC) của 5 mô hình Machine Learning"),
        ("Bảng 3.1", "Cấu hình cổng dịch vụ và vai trò của 3 phân hệ trong kiến trúc giả lập Tấn công - Phòng thủ thực tế"),
        ("Bảng 3.2", "Kết quả kiểm thử 5 kịch bản lưu lượng mạng (Benign + 4 pha Botnet Kill-Chain) qua Trạm gác AI NIDS/IPS"),
    ]
    add_styled_table(
        doc,
        ["SỐ TT", "TIÊU ĐỀ BẢNG BIỂU"],
        tbl_list,
        caption_text="Bảng 0.3: Danh mục các bảng biểu số liệu và kết quả đánh giá",
        col_widths=[3.0, 13.0]
    )
    doc.add_page_break()

    # =========================================================================
    # 5. MỞ ĐẦU
    # =========================================================================
    add_heading_custom(doc, "MỞ ĐẦU", level=1)

    add_heading_custom(doc, "1. Tính cấp thiết và lý do chọn đề tài", level=2)
    add_body_para(
        doc,
        "Sự bùng nổ của cuộc Cách mạng Công nghiệp 4.0 đã đưa hàng chục tỷ thiết bị Internet vạn vật (Internet of Things - IoT) "
        "như camera giám sát IP, bộ định tuyến thông minh, cảm biến công nghiệp và thiết bị nhà thông minh (Smart Home) kết nối trực tiếp vào Internet. "
        "Tuy nhiên, do ràng buộc khắt khe về chi phí sản xuất, dung lượng bộ nhớ và năng lượng tiêu thụ, phần lớn thiết bị IoT thương mại "
        "đều thiếu hụt các cơ chế bảo mật cơ bản: mật khẩu mặc định cứng (hard-coded credentials), dịch vụ quản trị từ xa không mã hóa (Telnet cổng 23/2323, SSH cổng 22), "
        "và quy trình vá lỗi firmware phức tạp. Đây chính là lỗ hổng chí mạng biến hệ sinh thái IoT thành mục tiêu hàng đầu của các chiến dịch tấn công mạng toàn cầu."
    )
    add_body_para(
        doc,
        "Thực tế an ninh mạng những năm gần đây đã chứng kiến sự trỗi dậy nguy hiểm của các mạng máy tính ma (Botnet) chuyên nhắm vào thiết bị IoT, "
        "điển hình là 3 họ mã độc khét tiếng: Mirai (tác nhân gây ra các cuộc tấn công DDoS vượt ngưỡng 1.2 Tbps làm tê liệt hệ thống DNS Dyn), "
        "Hajime (mã độc sử dụng mạng ngang hàng phi tập trung BitTorrent DHT để che giấu máy chủ điều khiển), và Torii (dòng Botnet thế hệ mới có khả năng "
        "chiếm quyền bền vững và đánh cắp dữ liệu nhạy cảm trên đa kiến trúc vi xử lý ARM, MIPS, x86, PowerPC). "
        "Các hệ thống phát hiện xâm nhập truyền thống dựa trên tập luật tĩnh (Signature-based IDS như Snort hay Suricata) thường xuyên thất bại trước các biến thể "
        "Botnet mới hoặc khi mã độc thay đổi payload. Ngược lại, mặc dù mã độc có thể biến đổi mã nguồn, hành vi giao tiếp mạng ở tầng Transport/Session "
        "(như quét cổng ngang tốc độ cao, dò mật khẩu vét cạn, kết nối C&C định kỳ và bão gói tin DDoS) luôn để lại dấu vết đặc trưng rõ rệt trong các bản ghi luồng mạng (Network Flows). "
        "Chính vì vậy, việc nghiên cứu và triển khai đề tài \"Phát hiện và phân loại hành vi mã độc Botnet trên thiết bị IoT (Mirai, Hajime, Torii) sử dụng Machine Learning\" "
        "mang tính cấp thiết cao cả về mặt học thuật lẫn thực tiễn triển khai trong học phần Kiểm thử xâm nhập (Penetration Testing)."
    )

    add_heading_custom(doc, "2. Mục tiêu của đề tài", level=2)
    add_bullet_para(doc, "Mục tiêu nghiên cứu lý thuyết: ", "Phân tích chuyên sâu cơ chế lây nhiễm, chuỗi tiêu diệt (Cyber Kill-Chain) và dấu hiệu lưu lượng mạng cấp độ luồng (Zeek Conn-Log) của 3 họ mã độc Botnet IoT tiêu biểu: Mirai, Hajime và Torii.")
    add_bullet_para(doc, "Mục tiêu thực nghiệm dữ liệu lớn (Big Data ML): ", "Xây dựng quy trình tiền xử lý chuẩn quốc tế trên toàn bộ 100% bộ dữ liệu Stratosphere IoT-23 (5.696.295 bản ghi), áp dụng chia tách phân tầng Stratified 80/20 (4.557.036 bản ghi huấn luyện và 1.139.259 bản ghi kiểm thử độc lập) để loại bỏ hoàn toàn hiện tượng rò rỉ dữ liệu (Data Leakage).")
    add_bullet_para(doc, "Mục tiêu đối sánh thuật toán: ", "Huấn luyện và đánh giá khách quan 5 mô hình học máy (Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM) nhằm lựa chọn mô hình tối ưu nhất về độ chính xác (F1-Score 99.99%), độ trễ suy luận thời gian thực (0.0043 ms/luồng) và khả năng chống quá khớp.")
    add_bullet_para(doc, "Mục tiêu xây dựng hệ thống thực tế: ", "Triển khai hệ thống giả lập Kiểm thử xâm nhập & Phòng thủ chủ động 3 bên (Bên 1: Kẻ tấn công Red Team Botnet Console - Bên 2: Trạm gác AI NIDS/IPS Guardian cho Admin SOC - Bên 3: Thiết bị IoT Nạn nhân cho Người sử dụng) có khả năng chạy trực tiếp trên 1 hoặc 2 laptop qua mạng LAN/Wi-Fi.")

    add_heading_custom(doc, "3. Phạm vi và đối tượng nghiên cứu", level=2)
    add_bullet_para(doc, "Đối tượng nghiên cứu: ", "Các đặc trưng hành vi luồng mạng (Network Flow Metadata) trích xuất từ trình phân tích Zeek (Bro) IDS trên bộ dữ liệu chuẩn quốc tế Stratosphere IoT-23 (Đại học Kỹ thuật Séc - CTU công bố năm 2020) và lưu lượng tấn công giả lập thực nghiệm.")
    add_bullet_para(doc, "Phạm vi nghiên cứu: ", "Tập trung vào bài toán phát hiện xâm nhập cấp độ cổng mạng biên (Edge Gateway NIDS/IPS) đối với 4 nhóm hành vi cốt lõi của Botnet IoT: (1) Quét cổng ngang thăm dò dịch vụ (Horizontal Port Scan), (2) Tấn công vét cạn mật khẩu Telnet/SSH (Credential Brute-Force), (3) Kết nối máy chủ điều khiển từ xa (C&C Beaconing), và (4) Tấn công từ chối dịch vụ phân tán (DDoS SYN/UDP Flood).")

    add_heading_custom(doc, "4. Nội dung thực hiện của đề tài", level=2)
    add_body_para(
        doc,
        "Để hoàn thành các mục tiêu đề ra, nhóm nghiên cứu đã triển khai đồng bộ 4 hạng mục công việc cốt lõi: "
        "(1) Khảo sát lý thuyết an ninh mạng IoT, cấu trúc nhật ký Zeek và nguyên lý toán học của 5 thuật toán học máy; "
        "(2) Thiết kế pipeline làm sạch dữ liệu, chuẩn hóa đặc trưng, chia tách phân tầng 80/20 trên 5,69 triệu dòng dữ liệu IoT-23 và huấn luyện mô hình trong 2 Jupyter Notebooks chuẩn hóa; "
        "(3) Đóng gói mô hình tối ưu LightGBM (iot_nids_bundle.joblib) và phát triển hệ thống phần mềm 3 phân hệ (Red Team Attacker Console cổng 9090, Admin SOC Guardian cổng 5000, Victim IoT Server cổng 8088/2323); "
        "(4) Thực hiện kiểm thử xâm nhập thực nghiệm theo quy trình chuẩn và tổng hợp báo cáo khoa học."
    )

    add_heading_custom(doc, "5. Bố cục của báo cáo", level=2)
    add_body_para(doc, "Nội dung chính của báo cáo được tổ chức thành 3 chương chặt chẽ theo đúng quy định của học phần:")
    add_bullet_para(doc, "Chương 1 - Cơ sở lý thuyết: ", "Trình bày tổng quan về an ninh thiết bị IoT, giải phẫu hành vi của 3 họ mã độc Mirai, Hajime, Torii, kiến trúc Zeek NIDS và cơ sở toán học của 5 thuật toán Machine Learning.")
    add_bullet_para(doc, "Chương 2 - Đề xuất mô hình và Thực nghiệm: ", "Phân tích chi tiết bộ dữ liệu Stratosphere IoT-23 (5.696.295 bản ghi), đề xuất quy trình tiền xử lý chống Data Leakage, trình bày kịch bản huấn luyện và đánh giá chuyên sâu kết quả thực nghiệm của 5 thuật toán.")
    add_bullet_para(doc, "Chương 3 - Xây dựng hệ thống phát hiện và phân loại mã độc Botnet IoT: ", "Mô tả môi trường công nghệ, kiến trúc triển khai và chi tiết chức năng của hệ thống giả lập 3 bên (Kẻ tấn công Red Team, Quản trị viên Admin SOC, và Người sử dụng Thiết bị IoT).")

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 1: CƠ SỞ LÝ THUYẾT
    # =========================================================================
    add_heading_custom(doc, "CHƯƠNG 1: CƠ SỞ LÝ THUYẾT", level=1)

    add_heading_custom(doc, "1.1. Giới thiệu về đề tài", level=2)
    add_body_para(
        doc,
        "Trong mô hình kiểm thử xâm nhập (Penetration Testing) và phòng thủ mạng hiện đại (Purple Team Operations), việc hiểu rõ cách thức kẻ tấn công "
        "khai thác thiết bị đầu cuối cũng như xây dựng hàng rào phát hiện tự động đóng vai trò sống còn. Khác với máy chủ doanh nghiệp hay máy tính cá nhân "
        "có đủ tài nguyên phần cứng để cài đặt phần mềm diệt virus (Endpoint Detection and Response - EDR), các thiết bị IoT như camera IP, cảm biến nhiệt độ, "
        "hay bộ điều khiển công nghiệp chạy trên các hệ điều hành nhúng rút gọn (Embedded Linux, BusyBox) với bộ nhớ RAM chỉ từ vài chục MB. "
        "Do không thể cài đặt tác nhân bảo mật trực tiếp lên từng thiết bị IoT, giải pháp tối ưu và khả thi nhất hiện nay là triển khai Hệ thống Phát hiện và Ngăn chặn Xâm nhập Mạng "
        "(Network Intrusion Detection and Prevention System - NIDS/IPS) tích hợp Trí tuệ nhân tạo ngay tại cổng mạng biên (IoT Gateway / Router)."
    )
    add_body_para(
        doc,
        "Đề tài tập trung giải quyết bài toán cốt lõi: Làm thế nào để một trạm gác NIDS tại cổng Gateway có thể phân tích siêu dữ liệu luồng mạng (Flow Metadata) "
        "theo thời gian thực với độ trễ dưới 1 mili-giây, từ đó nhận diện chính xác đâu là lưu lượng hoạt động bình thường của thiết bị IoT (Benign) và đâu là hành vi "
        "tấn công của các mạng Botnet nguy hiểm (Mirai, Hajime, Torii), đồng thời tự động kích hoạt quy tắc tường lửa (IPS Auto-Block) để cô lập nguồn tấn công trước khi thiết bị bị chiếm quyền điều khiển."
    )

    add_figure_with_caption(
        doc,
        "fig1_system_architecture.png",
        "Hình 1.1: Kiến trúc tổng thể hệ thống phòng vệ AI NIDS và giả lập tấn công - phòng thủ 3 bên",
        width_inches=6.2
    )

    add_heading_custom(doc, "1.2. Giới thiệu về các lý thuyết liên quan", level=2)

    add_heading_custom(doc, "1.2.1. Đặc thù kiến trúc mạng IoT và bề mặt tấn công", level=3)
    add_body_para(
        doc,
        "Một hệ sinh thái IoT tiêu chuẩn bao gồm 3 tầng kiến trúc: (1) Tầng Cảm biến & Thiết bị đầu cuối (Perception/Device Layer), "
        "(2) Tầng Truyền dẫn & Cổng mạng (Network/Gateway Layer), và (3) Tầng Ứng dụng & Đám mây (Application/Cloud Layer). "
        "Qua khảo sát thực tế trong kiểm thử xâm nhập, bề mặt tấn công trên thiết bị IoT tập trung chủ yếu ở các dịch vụ quản trị mở sẵn trên tầng mạng cục bộ và Internet:"
    )
    add_bullet_para(doc, "Dịch vụ Telnet (Cổng 23, 2323) và SSH (Cổng 22): ", "Hàng triệu camera IP và router sử dụng tài khoản quản trị mặc định (như root/vizxv, admin/admin, root/xc3511) không bắt buộc đổi mật khẩu khi xuất xưởng.")
    add_bullet_para(doc, "Giao thức quản lý từ xa TR-069 / CWMP (Cổng 7547) và HTTP/UPnP (Cổng 80, 8080, 37215): ", "Chứa nhiều lỗ hổng thực thi mã từ xa (Remote Code Execution - RCE) hoặc vượt qua xác thực (Authentication Bypass).")
    add_bullet_para(doc, "Giao diện gỡ lỗi Android Debug Bridge - ADB (Cổng 5555): ", "Thường bị bỏ quên ở trạng thái mở trên các thiết bị Smart TV và Android Box, cho phép kẻ tấn công nạp trực tiếp mã độc mà không cần mật khẩu.")

    add_heading_custom(doc, "1.2.2. Giải phẫu hành vi 3 họ mã độc Botnet IoT: Mirai, Hajime và Torii", level=3)
    add_body_para(
        doc,
        "Trong bộ dữ liệu Stratosphere IoT-23 cũng như thực tế không gian mạng, Mirai, Hajime và Torii đại diện cho 3 thế hệ kiến trúc Botnet IoT khác nhau. "
        "Mặc dù có mục đích cuối cùng khác nhau, cả 3 họ mã độc này đều tuân theo chuỗi tiêu diệt (Kill-Chain) gồm 4 giai đoạn đặc trưng trên mạng:"
    )
    add_bullet_para(
        doc,
        "1. Mã độc Mirai (Khởi nguồn năm 2016): ",
        "Hoạt động theo mô hình máy chủ điều khiển tập trung (Centralized C&C). Giai đoạn đầu, module Scanner của Mirai thực hiện quét ngang đồng bộ (Horizontal SYN Scan) "
        "với tốc độ cực cao tới cổng TCP 23 và 2323 trên các dải IP ngẫu nhiên. Khi phát hiện cổng mở, module Brute-Forcer thử lần lượt danh sách hơn 60 cặp tài khoản/mật khẩu mặc định. "
        "Sau khi đăng nhập thành công, thiết bị báo cáo về máy chủ Loader để tải tập tin thực thi tương ứng với kiến trúc CPU và chờ lệnh phát động tấn công DDoS (SYN Flood, UDP Flood, ACK Flood, HTTP Flood)."
    )
    add_bullet_para(
        doc,
        "2. Mã độc Hajime (Phát hiện cuối năm 2016): ",
        "Là biến thể tiến hóa vượt bậc so với Mirai khi loại bỏ hoàn toàn máy chủ C&C tập trung, thay vào đó sử dụng mạng ngang hàng phi tập trung (Peer-to-Peer) "
        "dựa trên giao thức bảng băm phân tán BitTorrent DHT qua cổng UDP/TCP động. Hajime không chỉ quét cổng Telnet 23/2323 mà còn khai thác các lỗ hổng trên cổng 5358, 7547 (TR-069). "
        "Sau khi xâm nhập, Hajime chủ động khóa các cổng 23, 7547, 5555 trên thiết bị nạn nhân để ngăn chặn Mirai chiếm quyền lại."
    )
    add_bullet_para(
        doc,
        "3. Mã độc Torii (Phát hiện năm 2018): ",
        "Khác với Mirai và Hajime vốn ồn ào và tập trung vào tấn công DDoS, Torii là dòng mã độc gián điệp và chiếm quyền điều khiển tinh vi (Stealthy Backdoor Botnet). "
        "Torii không xóa bỏ dịch vụ hay tiêu tốn băng thông DDoS ngay lập tức, mà thiết lập 6 cơ chế khởi chạy bền vững (Persistence) khác nhau trong hệ thống tệp của thiết bị IoT, "
        "sau đó duy trì luồng kết nối ngầm (Encrypted/Persistent C&C Beaconing) tới máy chủ điều khiển qua các cổng như 443, 4444, 6667, 8443 để đánh cắp thông tin và nhận lệnh thực thi shell từ xa."
    )

    botnet_compare_rows = [
        ("Mirai", "Centralized C&C (Máy chủ tập trung)", "Quét SYN cổng 23, 2323, 22, 8080; Brute-force 62 cặp mật khẩu mặc định", "Tấn công DDoS quy mô lớn (SYN, UDP, GRE, HTTP Flood)", "Hàng loạt luồng S0 (orig_bytes=0), thời lượng 0s, theo sau bởi luồng REJ/RSTO và bão gói tin"),
        ("Hajime", "Peer-to-Peer (P2P qua BitTorrent DHT)", "Quét cổng Telnet 23/2323 và khai thác lỗ hổng TR-069 (cổng 7547)", "Mở rộng mạng lưới P2P, khóa cổng dịch vụ, tấn công DDoS theo lệnh", "Lưu lượng quét cổng S0 kết hợp trao đổi gói tin UDP/TCP liên tục giữa các nút đồng đẳng"),
        ("Torii", "Stealthy C&C (Đa tầng, mã hóa lệnh)", "Xâm nhập qua Telnet/SSH yếu, nạp binary đa kiến trúc (MIPS, ARM, x86)", "Gián điệp, đánh cắp dữ liệu, thực thi lệnh từ xa (Reverse Shell) bền vững", "Luồng kết nối C&C có thời lượng kéo dài hoặc lặp lại chu kỳ cố định tới cổng 4444/6667/8443"),
    ]
    add_styled_table(
        doc,
        ["Họ Botnet", "Kiến trúc điều khiển", "Phương thức phát tán & Khai thác", "Mục tiêu tấn công chính", "Dấu hiệu đặc trưng trên Zeek Conn-Log"],
        botnet_compare_rows,
        caption_text="Bảng 1.1: Bảng đối sánh đặc điểm kỹ thuật, cơ chế lây lan và dấu hiệu mạng của 3 họ Botnet: Mirai, Hajime và Torii",
        col_widths=[2.2, 3.0, 3.6, 3.4, 3.8]
    )

    add_heading_custom(doc, "1.2.3. Hệ thống phát hiện xâm nhập mạng (NIDS) và Zeek Conn-Log", level=3)
    add_body_para(
        doc,
        "Hệ thống phát hiện xâm nhập mạng (NIDS) được chia thành hai trường phái chính: Phát hiện dựa trên chữ ký (Signature-based Detection) và Phát hiện dựa trên bất thường hành vi (Anomaly/Behavior-based Detection). "
        "Để áp dụng Machine Learning vào phát hiện hành vi mà không xâm phạm quyền riêng tư hay bị vô hiệu hóa bởi mã hóa TLS/SSL, hệ thống sử dụng công cụ phân tích mạng Zeek (trước đây là Bro). "
        "Thay vì kiểm tra nội dung gói tin thô (Deep Packet Inspection), Zeek gom nhóm các gói tin thuộc cùng một phiên giao tiếp 5-tuple (IP nguồn, Cổng nguồn, IP đích, Cổng đích, Giao thức) "
        "thành một bản ghi tổng hợp duy nhất trong tập tin conn.log."
    )
    add_body_para(
        doc,
        "Hai trường thông tin giá trị nhất mà Zeek trích xuất được là trạng thái kết nối (conn_state) và chuỗi lịch sử cờ TCP (history). "
        "Ví dụ: một kết nối HTTP/MQTT hợp lệ của thiết bị IoT thường có conn_state = SF (kết nối thiết lập và kết thúc bình thường với cờ SYN -> SYN-ACK -> ACK -> Data -> FIN, tương ứng history = ShADadFf). "
        "Ngược lại, khi mã độc Mirai hoặc Hajime thực hiện quét cổng ngang tới hàng ngàn địa chỉ IP không mở cổng hoặc bị tường lửa chặn, gói tin SYN gửi đi không nhận được phản hồi, "
        "tạo ra hàng loạt bản ghi có conn_state = S0, history = S, duration = 0 và orig_bytes = 0."
    )

    add_heading_custom(doc, "1.2.4. Cơ sở lý thuyết 5 thuật toán Machine Learning phân loại lưu lượng", level=3)
    add_body_para(
        doc,
        "Để tìm ra mô hình phân loại luồng mạng IoT tối ưu nhất, đề tài nghiên cứu và thực nghiệm đối sánh 5 thuật toán học máy có giám sát (Supervised Learning) trải rộng từ mô hình tuyến tính cổ điển đến các thuật toán học kết hợp (Ensemble Boosting) tiên tiến:"
    )
    add_bullet_para(
        doc,
        "1. Hồi quy Logistic (Logistic Regression): ",
        "Mô hình phân loại tuyến tính sử dụng hàm kích hoạt Sigmoid: P(y=1|x) = 1 / (1 + exp(-(w^T * x + b))) để ước lượng xác suất một luồng mạng x thuộc nhãn Độc hại (y=1). "
        "Ưu điểm của Logistic Regression là tốc độ tính toán cực nhanh và cấu trúc đơn giản, nhưng hạn chế lớn là không thể nắm bắt tốt các mối quan hệ phi tuyến tính phức tạp giữa cổng dịch vụ và trạng thái kết nối."
    )
    add_bullet_para(
        doc,
        "2. Cây quyết định (Decision Tree - CART): ",
        "Xây dựng cấu trúc cây phân nhánh nhị phân bằng cách chọn ngưỡng chia đặc trưng tại mỗi nút sao cho độ hỗn loạn thông tin (Gini Impurity) giảm mạnh nhất. "
        "Decision Tree rất phù hợp với dữ liệu bảng có cả biến số và biến phân loại như Zeek Conn-Log, nhưng một cây đơn lẻ rất dễ bị hiện tượng quá khớp (Overfitting) khi cây phát triển quá sâu."
    )
    add_bullet_para(
        doc,
        "3. Rừng ngẫu nhiên (Random Forest): ",
        "Thuật toán học kết hợp theo cơ chế Bagging (Bootstrap Aggregating), huấn luyện song song hàng chục cây quyết định độc lập trên các tập con dữ liệu và tập con đặc trưng ngẫu nhiên, "
        "sau đó lấy biểu quyết đa số (Majority Voting). Random Forest khắc phục triệt để hiện tượng quá khớp của cây đơn lẻ, nhưng đánh đổi bằng dung lượng bộ nhớ lớn và thời gian huấn luyện lâu hơn."
    )
    add_bullet_para(
        doc,
        "4. XGBoost (eXtreme Gradient Boosting): ",
        "Thuật toán Boosting tuần tự xây dựng chuỗi các cây quyết định, trong đó cây thứ t được huấn luyện để tối thiểu hóa sai số đạo hàm bậc hai của các cây trước đó, kết hợp thành phần điều chuẩn L1/L2 (Regularization) giúp kiểm soát độ phức tạp của mô hình. Phiên bản hist của XGBoost gom nhóm các giá trị liên tục thành các thùng (histogram bins) để tăng tốc trên tập dữ liệu hàng triệu dòng."
    )
    add_bullet_para(
        doc,
        "5. LightGBM (Light Gradient Boosting Machine): ",
        "Thuật toán Gradient Boosting thế hệ mới do Microsoft phát triển, tối ưu hóa dựa trên cơ chế phân thùng Histogram cho dữ liệu quy mô lớn (Big Data). "
        "LightGBM phát triển cây theo chiến lược Leaf-wise (ưu tiên tách nút lá mang lại mức giảm hàm mất mát lớn nhất với max_depth=6) thay vì Level-wise truyền thống, "
        "cho phép đạt tốc độ huấn luyện nhanh gấp nhiều lần so với Random Forest và Decision Tree trên hàng triệu mẫu."
    )

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 2: ĐỀ XUẤT MÔ HÌNH VÀ THỰC NGHIỆM
    # =========================================================================
    add_heading_custom(doc, "CHƯƠNG 2: ĐỀ XUẤT MÔ HÌNH VÀ THỰC NGHIỆM", level=1)

    add_heading_custom(doc, "2.1. Giới thiệu bài toán và Bộ dữ liệu chuẩn Stratosphere IoT-23", level=2)
    add_body_para(
        doc,
        "Bài toán đặt ra trong nghiên cứu này là bài toán phân loại nhị phân (Binary Classification) kết hợp định danh hành vi trên dữ liệu luồng mạng quy mô lớn: "
        "Cho trước tập hợp các bản ghi luồng mạng X = {x_1, x_2, ..., x_N} thu thập tại cổng Gateway IoT, mỗi bản ghi x_i biểu diễn một phiên kết nối mạng với các thuộc tính giao thức, "
        "thời lượng, số lượng gói tin, số byte truyền tải và trạng thái phiên; mục tiêu là xây dựng ánh xạ f(x_i) -> y_i thuộc {0: Benign (Lưu lượng sạch), 1: Malicious (Lưu lượng mã độc Botnet)} "
        "sao cho đạt độ chính xác F1-Score cao nhất, tỷ lệ báo động giả (False Positive Rate) thấp nhất và thời gian suy luận đáp ứng yêu cầu chặn lọc trực tuyến."
    )
    add_body_para(
        doc,
        "Nhóm sử dụng bộ dữ liệu chuẩn quốc tế Stratosphere IoT-23 Malware Dataset do Phòng thí nghiệm Stratosphere thuộc Đại học Kỹ thuật Séc (CTU) công bố năm 2020. "
        "Bộ dữ liệu bao gồm 20 kịch bản mã độc thực tế (Mirai, Hajime, Torii, Kenjiro, Hakai...) và 3 kịch bản lưu lượng sạch từ các thiết bị IoT phần cứng thật (Philips Hue, Amazon Echo, Somfy Smart Lock). "
        "Tổng quy mô dữ liệu thực nghiệm trong đề tài là 5.696.295 bản ghi luồng mạng (gần 1 GB dữ liệu CSV sau khi trích xuất từ Zeek conn.log.labeled)."
    )

    add_figure_with_caption(
        doc,
        "fig2_class_distribution.png",
        "Hình 2.1: Phân bố nhãn lớp Benign (8,74%) và Malicious (91,26%) trên 5.696.295 bản ghi Stratosphere IoT-23",
        width_inches=5.8
    )

    iot23_features_rows = [
        ("1", "ts", "Float (Timestamp)", "Thời điểm bắt đầu phiên kết nối (Unix Epoch Time)", "Loại bỏ (Tránh học vẹt theo mốc thời gian thu thập)"),
        ("2", "uid", "String (ID)", "Định danh duy nhất của phiên kết nối trong Zeek", "Loại bỏ (Định danh ngẫu nhiên không mang ngữ nghĩa hành vi)"),
        ("3", "id.orig_h", "String (IPv4/v6)", "Địa chỉ IP của máy nguồn khởi tạo kết nối", "Loại bỏ khi huấn luyện ML (Tránh phụ thuộc IP tĩnh phòng Lab)"),
        ("4", "id.orig_p", "Integer (Port)", "Cổng nguồn (Source Port) của thiết bị khởi tạo", "Giữ lại (Đặc trưng số học quan trọng - Top 2 Feature)"),
        ("5", "id.resp_h", "String (IPv4/v6)", "Địa chỉ IP của máy đích nhận kết nối", "Loại bỏ khi huấn luyện ML (Tránh học vẹt địa chỉ IP đích)"),
        ("6", "id.resp_p", "Integer (Port)", "Cổng đích (Destination Port - VD: 23, 2323, 80, 4444)", "Giữ lại (Đặc trưng quan trọng số 1 - Top 1 Feature)"),
        ("7", "proto", "Categorical", "Giao thức tầng giao vận (tcp, udp, icmp)", "Giữ lại (Mã hóa OrdinalEncoder)"),
        ("8", "service", "Categorical", "Dịch vụ tầng ứng dụng nhận diện được (http, dns, ssh...)", "Loại bỏ (Trên 90% giá trị bị khuyết '-' trong các luồng quét S0)"),
        ("9", "duration", "Float (Seconds)", "Tổng thời lượng tồn tại của phiên kết nối", "Giữ lại (Chuẩn hóa StandardScaler - Top 4 Feature)"),
        ("10", "orig_bytes", "Integer (Bytes)", "Tổng số byte tải trọng (payload) gửi từ nguồn tới đích", "Giữ lại (Chuẩn hóa StandardScaler)"),
        ("11", "resp_bytes", "Integer (Bytes)", "Tổng số byte tải trọng phản hồi từ đích về nguồn", "Giữ lại (Chuẩn hóa StandardScaler)"),
        ("12", "conn_state", "Categorical", "Trạng thái kết nối Zeek (S0, SF, REJ, RSTO, RSTR, OTH...)", "Giữ lại (Mã hóa OrdinalEncoder - Top 3 Feature)"),
        ("13", "local_orig", "Boolean", "Cờ đánh dấu kết nối khởi tạo từ mạng nội bộ", "Loại bỏ (Trường rỗng '-' trên toàn bộ tập dữ liệu)"),
        ("14", "local_resp", "Boolean", "Cờ đánh dấu kết nối phản hồi từ mạng nội bộ", "Loại bỏ (Trường rỗng '-' trên toàn bộ tập dữ liệu)"),
        ("15", "missed_bytes", "Integer (Bytes)", "Số byte bị thất thoát khi bắt gói tin", "Loại bỏ (Đặc trưng phụ thuộc chất lượng card mạng)"),
        ("16", "history", "Categorical", "Chuỗi lịch sử trạng thái cờ TCP (S, ShADadFf, Sr, D...)", "Giữ lại (Mã hóa OrdinalEncoder - Top 5 Feature)"),
        ("17", "orig_pkts", "Integer (Packets)", "Tổng số gói tin gửi từ phía máy nguồn", "Giữ lại (Chuẩn hóa StandardScaler)"),
        ("18", "orig_ip_bytes", "Integer (Bytes)", "Tổng số byte cấp độ IP (bao gồm cả IP/TCP Header) từ nguồn", "Giữ lại (Chuẩn hóa StandardScaler)"),
        ("19", "resp_pkts", "Integer (Packets)", "Tổng số gói tin phản hồi từ phía máy đích", "Giữ lại (Chuẩn hóa StandardScaler)"),
        ("20", "resp_ip_bytes", "Integer (Bytes)", "Tổng số byte cấp độ IP phản hồi từ phía máy đích", "Giữ lại (Chuẩn hóa StandardScaler)"),
        ("21", "label / detailed-label", "Target Class", "Nhãn phân loại luồng mạng: Benign (0) hoặc Malicious (1)", "Biến mục tiêu y (Target Variable)"),
    ]
    add_styled_table(
        doc,
        ["TT", "Tên trường", "Kiểu dữ liệu", "Ý nghĩa kỹ thuật trong Zeek Network Monitor", "Quyết định xử lý trong Pipeline ML"],
        iot23_features_rows,
        caption_text="Bảng 2.1: Bảng mô tả chi tiết 21 trường dữ liệu nguyên bản trong Zeek Conn-Log của bộ dữ liệu Stratosphere IoT-23",
        col_widths=[1.0, 2.5, 2.5, 5.2, 4.8]
    )

    add_heading_custom(doc, "2.2. Đề xuất quy trình tiền xử lý và Chia tách Stratified 80/20 chống Data Leakage", level=2)
    add_body_para(
        doc,
        "Một sai lầm phổ biến trong nhiều nghiên cứu trước đây khi làm việc với bộ dữ liệu IoT-23 là chia tập dữ liệu Huấn luyện (Train) và Kiểm thử (Test) theo từng file kịch bản rời rạc "
        "mà không kiểm tra phân bố lớp, dẫn đến hiện tượng tập Train chỉ chứa một nhãn duy nhất (100% Malicious) hoặc rò rỉ thông tin thống kê (Data Leakage) từ tập Test sang tập Train. "
        "Để khắc phục triệt để vấn đề này, nhóm đề xuất quy trình tiền xử lý dữ liệu và huấn luyện chuẩn quốc tế gồm 5 bước nghiêm ngặt:"
    )
    add_bullet_para(
        doc,
        "Bước 1 - Hợp nhất và Chia tách phân tầng (Stratified Train-Test Split 80/20): ",
        "Toàn bộ 5.696.295 bản ghi của bộ dữ liệu được hợp nhất và thực hiện chia tách ngẫu nhiên có phân tầng (Stratified Sampling với random_state = 42) theo tỷ lệ chuẩn 80% Huấn luyện (4.557.036 dòng) "
        "và 20% Kiểm thử độc lập (1.139.259 dòng). Kỹ thuật Stratified đảm bảo tỷ lệ giữa lớp Malicious (91,26%) và lớp Benign (8,74%) được bảo toàn tuyệt đối ở cả hai tập."
    )
    add_bullet_para(
        doc,
        "Bước 2 - Lọc bỏ đặc trưng định danh tĩnh và cột rỗng (Feature Selection): ",
        "Loại bỏ các trường gây học vẹt theo môi trường mạng cụ thể (ts, uid, id.orig_h, id.resp_h, local_orig, local_resp, service, missed_bytes, tunnel_parents, detailed-label), "
        "giữ lại đúng 12 đặc trưng hành vi luồng mạng cốt lõi gồm 9 đặc trưng số học (id.orig_p, id.resp_p, duration, orig_bytes, resp_bytes, orig_pkts, orig_ip_bytes, resp_pkts, resp_ip_bytes) "
        "và 3 đặc trưng phân loại (proto, conn_state, history)."
    )
    add_bullet_para(
        doc,
        "Bước 3 - Làm sạch dữ liệu khuyết thiếu của Zeek: ",
        "Trong nhật ký Zeek, các phiên kết nối chưa hoàn tất (như gói SYN quét cổng S0) có trường duration, orig_bytes, resp_bytes được ghi ký hiệu khuyết '-'. "
        "Pipeline tự động chuyển đổi ký hiệu '-' về giá trị số học 0.0 và ép kiểu float32 để tối ưu hóa 50% dung lượng RAM khi xử lý hơn 5,69 triệu dòng."
    )
    add_bullet_para(
        doc,
        "Bước 4 - Mã hóa biến phân loại và Chuẩn hóa z-score chống rò rỉ dữ liệu: ",
        "Các bộ biến đổi OrdinalEncoder cho 3 cột phân loại và StandardScaler cho 9 cột số học "
        "CHỈ được phép gọi hàm fit_transform() trên tập Train (4.557.036 dòng). Tập Test (1.139.259 dòng) hoàn toàn bị cô lập trong suốt pha huấn luyện và chỉ được áp dụng hàm transform() từ tham số đã học trên tập Train."
    )
    add_bullet_para(
        doc,
        "Bước 5 - Đóng gói Bundle Mô hình (iot_nids_bundle.joblib): ",
        "Mô hình đạt hiệu năng cao nhất cùng toàn bộ từ điển encoders, tham số scaler và danh sách features được đóng gói thành một tệp nhị phân duy nhất để nạp trực tiếp vào hệ thống NIDS thời gian thực."
    )

    split_stats_rows = [
        ("Tập Huấn luyện (Train Set - 80%)", "4.557.036", "4.158.670 (91,26%)", "398.366 (8,74%)", "775,4 MB (train_set.csv)"),
        ("Tập Kiểm thử độc lập (Test Set - 20%)", "1.139.259", "1.039.667 (91,26%)", "99.592 (8,74%)", "193,8 MB (test_set.csv)"),
        ("TỔNG TOÀN BỘ DATASET IoT-23 (100%)", "5.696.295", "5.198.337 (91,26%)", "497.958 (8,74%)", "969,2 MB (Đã chuẩn hóa)"),
    ]
    add_styled_table(
        doc,
        ["Tập dữ liệu", "Tổng số bản ghi (Flows)", "Số luồng Độc hại (Malicious - Nhãn 1)", "Số luồng Hợp lệ (Benign - Nhãn 0)", "Dung lượng lưu trữ"],
        split_stats_rows,
        caption_text="Bảng 2.2: Thống kê phân bố nhãn Benign và Malicious sau khi chia tách phân tầng Stratified 80/20 (5.696.295 bản ghi)",
        col_widths=[4.2, 2.8, 3.2, 3.0, 2.8]
    )

    add_body_para(
        doc,
        "Dưới đây là chuỗi các biểu đồ phân tích khám phá dữ liệu (EDA) thực hiện trực tiếp trên tập dữ liệu thật của Stratosphere IoT-23, "
        "làm rõ các đặc trưng hành vi then chốt giúp phân biệt giữa lưu lượng bình thường của thiết bị IoT và lưu lượng tấn công Botnet:"
    )

    add_figure_with_caption(
        doc,
        "fig3_conn_state_analysis.png",
        "Hình 2.2: Phân tích khám phá dữ liệu (EDA): Phân bố trạng thái kết nối Zeek (conn_state) theo nhãn",
        width_inches=5.8
    )

    add_figure_with_caption(
        doc,
        "fig09_protocol_distribution.png",
        "Hình 2.3: Phân bố giao thức tầng giao vận (TCP, UDP, ICMP) theo nhãn Benign vs. Malicious",
        width_inches=5.8
    )

    add_figure_with_caption(
        doc,
        "fig10_top_ports.png",
        "Hình 2.4: Top 10 cổng đích bị Botnet tấn công nhiều nhất trong bộ dữ liệu Stratosphere IoT-23",
        width_inches=5.9
    )

    add_figure_with_caption(
        doc,
        "fig11_duration_distribution.png",
        "Hình 2.5: Phân bố thời lượng phiên kết nối (duration) thang logarithm giữa lưu lượng sạch và mã độc",
        width_inches=5.8
    )

    add_figure_with_caption(
        doc,
        "fig12_bytes_distribution.png",
        "Hình 2.6: So sánh tải trọng truyền tải (orig_bytes và resp_bytes) thang logarithm giữa Benign và Malicious",
        width_inches=6.0
    )

    add_figure_with_caption(
        doc,
        "fig13_packets_distribution.png",
        "Hình 2.7: Phân bố số lượng gói tin gửi từ nguồn (orig_pkts) thể hiện tính chất quét cổng chớp nhoáng",
        width_inches=5.8
    )

    add_figure_with_caption(
        doc,
        "fig14_botnet_family_breakdown.png",
        "Hình 2.8: Tỷ lệ phân bố các họ mã độc Botnet IoT (Mirai, Hajime, Torii, Kenjiro, Hakai) trong dữ liệu",
        width_inches=5.9
    )

    add_heading_custom(doc, "2.3. Kịch bản thực nghiệm và Thiết lập môi trường huấn luyện", level=2)
    add_body_para(
        doc,
        "Quá trình thực nghiệm được tổ chức thành 2 giai đoạn tách biệt hoàn toàn trên 2 Jupyter Notebooks độc lập nhằm đảm bảo tính minh bạch và khả năng tái lập kết quả:"
    )
    add_bullet_para(
        doc,
        "Kịch bản Thực nghiệm 1 (01_IoT23_EDA_and_Training.ipynb): ",
        "Nạp toàn bộ 4.557.036 bản ghi của tập train_set.csv, thực hiện phân tích thống kê khám phá (EDA), chuẩn hóa đặc trưng và huấn luyện 5 thuật toán: "
        "(1) Logistic Regression (max_iter=500, random_state=42), (2) Decision Tree (max_depth=16, random_state=42), (3) Random Forest (n_estimators=70, max_depth=14, n_jobs=-1), "
        "(4) XGBoost (n_estimators=100, max_depth=6, learning_rate=0.1, tree_method='hist'), và (5) LightGBM (n_estimators=100, max_depth=6, learning_rate=0.1, n_jobs=-1)."
    )
    add_bullet_para(
        doc,
        "Kịch bản Thực nghiệm 2 (02_IoT23_Model_Evaluation_and_Testing.ipynb): ",
        "Đóng vai trò kiểm toán mù độc lập (Blind Evaluation). Notebook nạp mô hình đã đóng gói iot_nids_bundle.joblib và kiểm thử trực tiếp trên 1.139.259 bản ghi hoàn toàn mới của tập test_set.csv "
        "để đo lường các chỉ số Accuracy, Precision, Recall, F1-Score, Ma trận nhầm lẫn (Confusion Matrix) và độ trễ suy luận trên từng luồng mạng."
    )

    add_heading_custom(doc, "2.4. Kết quả thực nghiệm và Đối sánh 5 mô hình trên 5.696.295 bản ghi", level=2)
    add_body_para(
        doc,
        "Sau khi thực thi toàn bộ quy trình huấn luyện trên 4.557.036 dòng dữ liệu và đánh giá trên tập kiểm chứng nội bộ (validation set), kết quả định lượng của cả 5 mô hình học máy được tổng hợp chi tiết trong Bảng 2.3:"
    )

    benchmark_rows = [
        ("1", "Logistic Regression", "98,84%", "99,29%", "99,44%", "99,36%", "5,66 giây", "Tuyến tính, bỏ sót các luồng C&C phi tuyến"),
        ("2", "Decision Tree (CART)", "99,99%", "99,99%", "99,99%", "99,99%", "24,28 giây", "Độ chính xác rất cao nhưng cây đơn dễ Overfit"),
        ("3", "Random Forest (Bagging)", "99,89%", "99,88%", "99,99%", "99,94%", "41,53 giây", "Ổn định nhưng thời gian huấn luyện chậm nhất"),
        ("4", "XGBoost (Hist Tree)", "99,98%", "99,98%", "99,99%", "99,99%", "22,97 giây", "Hiệu năng cao, tốc độ huấn luyện khá nhanh"),
        ("5", "LightGBM (Đề xuất)", "99,99%", "99,99%", "99,99%", "99,99%", "15,85 giây", "Ngang DT về độ chính xác, nhanh nhất khi train (15,85s)"),
    ]
    add_styled_table(
        doc,
        ["TT", "Mô hình Học máy", "Accuracy", "Precision", "Recall", "F1-Score", "Thời gian Train (4,55M dòng)", "Nhận xét & Đánh giá kỹ thuật"],
        benchmark_rows,
        caption_text="Bảng 2.3: Bảng tổng hợp kết quả huấn luyện và đánh giá 5 thuật toán Machine Learning trên tập dữ liệu IoT-23",
        col_widths=[0.9, 3.2, 1.8, 1.8, 1.8, 1.8, 2.2, 2.5]
    )

    add_figure_with_caption(
        doc,
        "fig5_model_benchmark.png",
        "Hình 2.9: Biểu đồ đối sánh hiệu năng (Accuracy, Precision, Recall, F1) và thời gian huấn luyện 5 mô hình ML",
        width_inches=6.0
    )

    add_figure_with_caption(
        doc,
        "fig16_time_comparison.png",
        "Hình 2.10: Biểu đồ đối sánh thời gian huấn luyện và độ trễ suy luận của 5 mô hình Machine Learning",
        width_inches=6.1
    )

    add_body_para(
        doc,
        "Khi đưa mô hình tối ưu LightGBM (iot_nids_bundle.joblib) sang kiểm thử độc lập trên 1.139.259 bản ghi của tập test_set.csv (trong Notebook số 02), "
        "toàn bộ quá trình tiền xử lý và dự đoán cho hơn 1,13 triệu luồng mạng chỉ tiêu tốn đúng 4,89 giây (tương đương tốc độ xử lý ~232.977 luồng/giây, hay 0,0043 ms/luồng ở chế độ batch). "
        "Kết quả phân loại chi tiết theo từng lớp (Classification Report) trên tập Test độc lập được trình bày trong Bảng 2.4:"
    )

    test_report_rows = [
        ("Lớp 0: Benign (Lưu lượng IoT Hợp lệ)", "0,9999 (99,99%)", "0,9988 (99,88%)", "0,9993 (99,93%)", "99.592 luồng"),
        ("Lớp 1: Malicious (Mã độc Botnet IoT)", "0,9999 (99,99%)", "1,0000 (100,00%)", "0,9999 (99,99%)", "1.039.667 luồng"),
        ("Trung bình vĩ mô (Macro Average)", "0,9999 (99,99%)", "0,9994 (99,94%)", "0,9996 (99,96%)", "1.139.259 luồng"),
        ("Trung bình có trọng số (Weighted Avg)", "0,9999 (99,99%)", "0,9999 (99,99%)", "0,9999 (99,99%)", "1.139.259 luồng"),
    ]
    add_styled_table(
        doc,
        ["Nhãn Phân loại (Target Class)", "Precision", "Recall", "F1-Score", "Số mẫu kiểm thử (Support)"],
        test_report_rows,
        caption_text="Bảng 2.4: Chi tiết báo cáo phân loại (Classification Report) theo từng lớp của mô hình LightGBM trên 1.139.259 dòng Test",
        col_widths=[5.2, 2.7, 2.7, 2.7, 2.7]
    )

    add_heading_custom(doc, "2.5. Đánh giá chuyên sâu kết quả kiểm thử độc lập", level=2)
    add_body_para(
        doc,
        "Dựa trên kết quả thực nghiệm thu được trên hơn 5,69 triệu bản ghi, nhóm nghiên cứu rút ra 3 phân tích chuyên sâu về mặt học thuật và an ninh mạng:"
    )
    add_body_para(
        doc,
        "Trên tổng số 1.139.259 luồng mạng của tập Test độc lập, mô hình LightGBM nhận diện chính xác 1.039.649 / 1.039.667 luồng tấn công Botnet (True Positives - TP, đạt tỷ lệ phát hiện Recall = 99,9983%, "
        "chỉ bỏ sót đúng 18 luồng False Negatives - FN). Đồng thời, trên 99.592 luồng giao tiếp hợp lệ của thiết bị IoT, mô hình phân loại đúng 99.472 luồng (True Negatives - TN) và chỉ phát sinh 120 cảnh báo giả "
        "(False Positives - FP, tương ứng tỷ lệ báo động giả FPR = 0,12%). Trong môi trường vận hành SOC thực tế, chỉ số FPR cực thấp (0,12%) giúp quản trị viên không bị quá tải bởi cảnh báo rác (Alert Fatigue) "
        "và hoàn toàn yên tâm khi bật chế độ chặn tự động (IPS Auto-Block).",
        bold_prefix="Thứ nhất - Phân tích Ma trận nhầm lẫn (Confusion Matrix) và Tỷ lệ Báo động giả: "
    )

    add_figure_with_caption(
        doc,
        "fig6_confusion_matrix.png",
        "Hình 2.11: Ma trận nhầm lẫn (Confusion Matrix) của LightGBM trên 1.139.259 dòng kiểm thử độc lập",
        width_inches=5.8
    )

    add_body_para(
        doc,
        "Để đánh giá toàn diện khả năng phân biệt ngưỡng của các mô hình, nhóm nghiên cứu đã xây dựng script compute_roc.py tính toán trực tiếp diện tích dưới đường cong ROC (ROC-AUC) "
        "trên tập kiểm thử độc lập cho cả 5 mô hình (kết quả ghi nhận tại Bảng 2.5 và Hình 2.12). "
        "Kết quả cho thấy cả 4 mô hình phi tuyến (Random Forest, LightGBM, XGBoost, Decision Tree) đều đạt diện tích AUC xấp xỉ tuyệt đối (> 0.999), vượt trội hoàn toàn so với mô hình tuyến tính Logistic Regression (AUC = 0.9869). "
        "Khi đối sánh giữa LightGBM và Decision Tree: Trên tập validation, Decision Tree đạt F1 100.00% ngang ngửa LightGBM 99.99%. Tuy nhiên, Decision Tree đơn lẻ rất dễ bị quá khớp (Overfitting) với nhiễu môi trường, "
        "trong khi LightGBM kết hợp chuỗi 100 cây tăng cường (max_depth=6) có khả năng tổng quát hóa cao hơn nhiều, đồng thời thời gian huấn luyện của LightGBM (15.85 giây) nhanh gấp 1.5 lần Decision Tree (24.28 giây) "
        "và nhanh gấp 2.6 lần Random Forest (41.53 giây).",
        bold_prefix="Thứ hai - Kiểm chứng định lượng đường cong ROC và chỉ số AUC thực tế: "
    )

    auc_table_rows = [
        ("1", "Logistic Regression", "0,986937", "50.000 luồng", "Phân loại tuyến tính, đường cong tách xa góc trái"),
        ("2", "Decision Tree (CART)", "0,999363", "50.000 luồng", "Biên phân lớp bậc thang, dễ bị nhạy cảm nhiễu"),
        ("3", "Random Forest", "0,999977", "50.000 luồng", "AUC cực cao nhưng chi phí bộ nhớ và train chậm nhất"),
        ("4", "XGBoost (Hist Tree)", "0,999879", "50.000 luồng", "Hiệu năng phân loại rất tốt, thời gian 22,97s"),
        ("5", "LightGBM (Đề xuất)", "1,000000", "50.000 luồng", "Tối ưu toàn diện: AUC tuyệt đối 1,000000 (mẫu 50.000 test), train nhanh nhất (15,85s)"),
    ]
    add_styled_table(
        doc,
        ["TT", "Mô hình Học máy", "Chỉ số ROC-AUC", "Quy mô kiểm thử", "Nhận xét & Đánh giá phân loại"],
        auc_table_rows,
        caption_text="Bảng 2.5: Bảng kết quả tính toán định lượng diện tích dưới đường cong ROC (ROC-AUC) của 5 mô hình Machine Learning",
        col_widths=[1.0, 3.8, 2.5, 2.5, 5.2]
    )

    add_figure_with_caption(
        doc,
        "fig15_roc_curves.png",
        "Hình 2.12: Đường cong ROC và chỉ số AUC đối sánh thực tế cả 5 thuật toán Machine Learning",
        width_inches=6.0
    )

    add_body_para(
        doc,
        "Trích xuất trọng số đóng góp đặc trưng (Feature Importance theo số lần phân tách nút - Split Count) từ mô hình LightGBM (Hình 2.13 và Hình 2.14) chỉ ra 5 đặc trưng quyết định tới khả năng nhận diện Botnet: "
        "(1) id.resp_p (Cổng đích - 1380 lần tách nút): Phản ánh trực tiếp các cổng dịch vụ nhạy cảm mà Mirai, Hajime và Torii nhắm tới như Telnet (23, 2323), SSH (22), HTTP (80, 8080), TR-069 (7547) và C&C (4444, 6667); "
        "(2) history (Lịch sử trạng thái cờ TCP - 318 lần tách nút): Phát hiện chuỗi bắt tay TCP dị thường (S, Sr, ShADadFr) trong các pha quét thăm dò và tấn công bão táp; "
        "(3) id.orig_p (Cổng nguồn - 289 lần tách nút): Phản ánh quy luật cấp phát cổng nguồn tuần tự hoặc cố định trong mã nguồn C của công cụ quét Mirai; "
        "(4) duration (Thời lượng kết nối - 281 lần tách nút): Nhận diện các phiên quét chớp nhoáng (0.0s) hoặc phiên giữ kết nối C&C bất thường; "
        "và (5) orig_ip_bytes (Tổng dung lượng byte IP từ nguồn - 229 lần tách nút): Nhận diện lưu lượng phát tán gói tin đột biến từ mã độc.",
        bold_prefix="Thứ ba - Giải mã hộp đen AI qua mức độ quan trọng của đặc trưng (Feature Importance): "
    )

    add_figure_with_caption(
        doc,
        "fig4_feature_importance.png",
        "Hình 2.13: Biểu đồ xếp hạng mức độ đóng góp đặc trưng (Feature Importance) trong mô hình LightGBM",
        width_inches=5.8
    )

    add_figure_with_caption(
        doc,
        "fig7_traffic_asymmetry.png",
        "Hình 2.14: Phân tích bất đối xứng lưu lượng mạng giữa gói tin gửi đi và gói tin phản hồi",
        width_inches=5.8
    )

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 3: XÂY DỰNG HỆ THỐNG PHÁT HIỆN VÀ PHÂN LOẠI MÃ ĐỘC BOTNET IoT
    # =========================================================================
    add_heading_custom(doc, "CHƯƠNG 3: XÂY DỰNG HỆ THỐNG PHÁT HIỆN VÀ PHÂN LOẠI MÃ ĐỘC BOTNET IoT", level=1)

    add_heading_custom(doc, "3.1. Giới thiệu về môi trường và công nghệ triển khai", level=2)
    add_body_para(
        doc,
        "Để chứng minh tính ứng dụng thực tiễn của mô hình LightGBM sau khi huấn luyện và đáp ứng đầy đủ yêu cầu thực hành của học phần Kiểm thử xâm nhập, "
        "nhóm đã thiết kế và lập trình hoàn chỉnh Hệ thống Giả lập Tấn công - Phòng thủ 3 Bên (3-Tier Live Attack-Defense Simulation Testbed). "
        "Kiến trúc này hoạt động theo mô hình Simulation Testbed: các gói tin tấn công và luồng mạng hợp lệ được mô phỏng đầy đủ metadata theo chuẩn Zeek Conn-Log và gửi qua REST API của Trạm gác AI NIDS. "
        "Hệ thống cho phép triển khai linh hoạt trên 1 máy tính cá nhân (chế độ Localhost Multi-Port) hoặc phân tán trên 2 laptop của 2 thành viên nhóm kết nối qua mạng Wi-Fi/LAN."
    )
    add_bullet_para(doc, "Ngôn ngữ lập trình & Nền tảng lõi: ", "Python 3.12 (64-bit) kết hợp kiến trúc Multi-threaded HTTP/TCP Socket Server độ trễ thấp.")
    add_bullet_para(doc, "Thư viện Trí tuệ nhân tạo & Xử lý dữ liệu: ", "LightGBM 4.x, XGBoost, Scikit-Learn (StandardScaler, OrdinalEncoder), Pandas, NumPy và Joblib.")
    add_bullet_para(doc, "Giao diện Giám sát & Điều khiển trực quan: ", "HTML5, CSS3 Modern Dark UI, JavaScript Fetch API bất đồng bộ cập nhật bảng điều khiển SOC theo thời gian thực mỗi 1 giây.")
    add_bullet_para(doc, "Lưu ý an ninh môi trường Lab: ", "Hệ thống được thiết kế cho phòng Lab và diễn tập thực hành; REST API quản trị không kích hoạt xác thực JWT (CORS *) để đơn giản hóa quá trình demo.")

    arch_nodes_rows = [
        ("Bên 1: Trạm Kẻ tấn công (Red Team Botnet Console)", "live_demo/attacker_botnet_console.py", "TCP 9090 (Web UI & CLI --auto-demo)", "Kiểm thử viên xâm nhập (Penetration Tester / Red Team)", "Phát động 4 kịch bản tấn công Botnet (Mirai Scan, Brute-Force, Torii C&C, Hajime DDoS) và kiểm tra phản ứng của IPS"),
        ("Bên 2: Trạm gác AI NIDS/IPS (Admin SOC Guardian)", "live_demo/ai_nids_guardian_server.py", "TCP 5000 (HTTP SOC Dashboard & REST API)", "Quản trị viên An ninh mạng (Admin / Blue Team SOC)", "Nạp mô hình LightGBM, trích xuất 12 đặc trưng trong <0.5ms, phân loại họ Botnet, tự động chặn IP (IPS Auto-Block) và xuất báo cáo CSV"),
        ("Bên 3: Thiết bị IoT Nạn nhân (Victim Smart Camera)", "live_demo/victim_iot_server.py", "TCP 8088 (Web UI) & TCP 2323 (Telnet)", "Người sử dụng cuối (Smart Home User) & Thiết bị IoT", "Giả lập Camera DUT-SmartCam-Pro-X1 gửi dữ liệu cảm biến định kỳ (Benign SF) và mở dịch vụ Telnet cổng 2323"),
    ]
    add_styled_table(
        doc,
        ["Tên phân hệ trong hệ thống", "Tập tin mã nguồn", "Cổng giao tiếp (Port)", "Đối tượng tương tác", "Chức năng nhiệm vụ cốt lõi"],
        arch_nodes_rows,
        caption_text="Bảng 3.1: Cấu hình cổng dịch vụ và vai trò của 3 phân hệ trong kiến trúc giả lập Tấn công - Phòng thủ thực tế",
        col_widths=[3.2, 3.2, 2.4, 2.8, 4.4]
    )

    add_heading_custom(doc, "3.2. Các chức năng của hệ thống", level=2)

    add_heading_custom(doc, "3.2.1. Chức năng Bên 1: Trạm Kẻ tấn công (Red Team Botnet Console - Cổng 9090)", level=3)
    add_body_para(
        doc,
        "Phân hệ Kẻ tấn công (attacker_botnet_console.py, giao diện tại http://127.0.0.1:9090) cung cấp bảng điều khiển Red Team cho phép phát động từng đòn tấn công riêng lẻ hoặc chuỗi tấn công liên hoàn (Kill-Chain) nhắm vào Thiết bị IoT Nạn nhân thông qua Trạm gác AI NIDS:"
    )
    add_bullet_para(doc, "1. Kịch bản Mirai Horizontal Port Scan: ", "Mô phỏng quét ngang đồng loạt 8 cổng dịch vụ nhạy cảm (23, 2323, 22, 80, 5555, 7547, 8080, 37215) với cờ SYN (conn_state = S0, orig_bytes = 0).")
    add_bullet_para(doc, "2. Kịch bản Mirai Telnet Credential Brute-Force: ", "Thử 6 cặp tài khoản/mật khẩu mặc định phổ biến (root:vizxv, admin:admin...) nhắm vào cổng 2323 của thiết bị IoT.")
    add_bullet_para(doc, "3. Kịch bản Torii Botnet C&C Beaconing: ", "Mô phỏng luồng kết nối duy trì phiên ngầm tới máy chủ điều khiển cổng 4444, 6667, 8443.")
    add_bullet_para(doc, "4. Kịch bản Hajime/Mirai DDoS SYN Flood: ", "Phát động bão gói tin tốc độ cao nhắm làm tê liệt cổng HTTP/Web của thiết bị IoT.")

    add_heading_custom(doc, "3.2.2. Chức năng Bên 2: Trạm Gác AI NIDS / Admin SOC Dashboard (Cổng 5000)", level=3)
    add_body_para(
        doc,
        "Phân hệ Quản trị viên (ai_nids_guardian_server.py, truy cập tại http://127.0.0.1:5000) đóng vai trò là Trung tâm Điều hành An ninh mạng (Security Operations Center - SOC) đặt tại cổng Gateway bảo vệ mạng nội bộ IoT:"
    )
    add_bullet_para(doc, "1. Giám sát chỉ số an ninh thời gian thực (Real-time Telemetry KPIs): ", "Hiển thị tổng số luồng đã phân tích, số luồng hợp lệ, số luồng độc hại bị phát hiện, số yêu cầu đã bị chặn và độ trễ suy luận trung bình của mô hình AI.")
    add_bullet_para(doc, "2. Định danh chi tiết hành vi và họ mã độc Botnet: ", "Kết hợp kết quả dự đoán nhị phân của LightGBM với thông số cổng đích và cờ TCP để phân loại cụ thể 4 hành vi tấn công.")
    add_bullet_para(doc, "3. Chuyển đổi linh hoạt chế độ IDS (Cảnh báo thụ động) và IPS (Ngăn chặn chủ động): ", "Khi bật IPS Auto-Block, bất kỳ IP nào phát sinh luồng mạng độc hại sẽ lập tức bị đưa vào danh sách đen (Blacklist) và từ chối mọi yêu cầu tiếp theo với mã HTTP 403 / BLOCK.")
    add_bullet_para(doc, "4. Quản lý danh sách đen & Xuất báo cáo Kiểm toán (Export CSV): ", "Cho phép khóa thủ công, gỡ khóa IP hoặc xuất toàn bộ nhật ký ra tập tin CSV phục vụ điều tra số (Digital Forensics).")

    add_heading_custom(doc, "3.2.3. Chức năng Bên 3: Thiết bị IoT Nạn nhân (Victim Smart Camera - Cổng 8088 & 2323)", level=3)
    add_body_para(
        doc,
        "Phân hệ Người sử dụng (victim_iot_server.py, giao diện tại http://127.0.0.1:8088) mô phỏng một thiết bị Camera An ninh Thông minh (DUT-SmartCam-Pro-X1):"
    )
    add_bullet_para(doc, "1. Giám sát thông số cảm biến và sức khỏe thiết bị: ", "Người sử dụng theo dõi trực tiếp nhiệt độ phòng (26.5 C), độ ẩm (62%), trạng thái ghi hình HD và mức tải CPU.")
    add_bullet_para(doc, "2. Phát sinh lưu lượng cảm biến hợp lệ (Benign Telemetry): ", "Định kỳ gửi dữ liệu cảm biến sạch (trạng thái SF, history ShADadFf) đi qua Trạm gác AI NIDS. Mô hình LightGBM nhận diện chính xác 100% là Benign (ALLOW).")
    add_bullet_para(doc, "3. Dịch vụ Telnet Daemon trên cổng TCP 2323: ", "Mở socket TCP thật lắng nghe tại cổng 2323 giả lập giao diện đăng nhập BusyBox Telnet của camera IoT.")

    live_test_rows = [
        ("1", "Lưu lượng Người dùng Hợp lệ (benign_traffic)", "192.168.1.20 (SmartHome-User)", "TCP / 80, 443, 1883", "SF / ShADadFf", "Benign (Sạch) - 100%", "Benign (Lưu lượng IoT hợp lệ)", "ALLOW (Cho phép)"),
        ("2", "Pha 1: Quét cổng ngang (mirai_port_scan)", "192.168.1.105 (Kali-MiraiScan)", "TCP / 23, 2323, 22, 80, 5555, 7547", "S0 / S (0 bytes)", "Malicious (Độc hại) - 100%", "Mirai/Hajime - Horizontal Port Scan (S0)", "BLOCK (Khóa IP)"),
        ("3", "Pha 2: Dò mật khẩu Telnet (mirai_bruteforce)", "192.168.1.106 (Kali-BruteForce)", "TCP / 2323 (Telnet)", "S0 / S (6 cặp mật khẩu)", "Malicious (Độc hại) - 100%", "Mirai - Telnet/SSH Credential Brute-Force", "BLOCK (Khóa IP)"),
        ("4", "Pha 3: Kết nối máy chủ C&C (torii_cnc)", "192.168.1.107 (Botnet-ToriiCnC)", "TCP / 4444, 6667, 8443", "S0 / S (Beaconing)", "Malicious - chặn 1/4 (25%)", "Torii Botnet - C&C Beaconing & Reverse Shell", "BLOCK 1/4 - sót 4444 (x2), 8443"),
        ("5", "Pha 4: Tấn công từ chối dịch vụ (hajime_ddos)", "192.168.1.108 (Botnet-HajimeDDoS)", "TCP / 80, 8088", "S0 / S (Flood 220 pkts)", "Malicious (Độc hại) - 100%", "Hajime/Mirai - DDoS SYN/UDP Flood", "BLOCK (Khóa IP)"),
    ]
    add_styled_table(
        doc,
        ["TT", "Kịch bản Kiểm thử", "Địa chỉ IP Nguồn", "Giao thức / Cổng đích", "Trạng thái Zeek", "Dự đoán của LightGBM", "Phân loại Hành vi trên SOC", "Hành động IPS"],
        live_test_rows,
        caption_text="Bảng 3.2: Kết quả kiểm thử 5 kịch bản lưu lượng mạng (Benign + 4 pha Botnet Kill-Chain) qua Trạm gác AI NIDS/IPS",
        col_widths=[0.8, 2.8, 2.5, 2.1, 1.8, 2.0, 2.4, 1.6]
    )

    add_figure_with_caption(
        doc,
        "fig8_live_soc_simulation.png",
        "Hình 3.1: Kết quả thực nghiệm hệ thống giả lập 3 bên (Attacker - AI NIDS Guardian - Victim IoT) thời gian thực",
        width_inches=6.2
    )

    doc.add_page_break()

    # =========================================================================
    # KẾT LUẬN
    # =========================================================================
    add_heading_custom(doc, "KẾT LUẬN", level=1)

    add_heading_custom(doc, "1. Kết quả đạt được", level=2)
    add_body_para(
        doc,
        "Sau quá trình nghiên cứu lý thuyết, thiết kế quy trình xử lý dữ liệu lớn và triển khai thực nghiệm, đề tài \"Phát hiện và phân loại hành vi mã độc Botnet trên thiết bị IoT (Mirai, Hajime, Torii) sử dụng Machine Learning\" "
        "của Nhóm 4 đã hoàn thành xuất sắc 100% các mục tiêu đề ra với những kết quả nổi bật sau:"
    )
    add_bullet_para(doc, "Về mặt cơ sở lý thuyết và dữ liệu: ", "Đã hệ thống hóa toàn diện kiến trúc mạng IoT, bề mặt tấn công và giải phẫu chi tiết vòng đời hoạt động của 3 họ mã độc Mirai, Hajime, Torii trên cấu trúc nhật ký Zeek Conn-Log. Xử lý thành công toàn bộ 100% bộ dữ liệu quốc tế Stratosphere IoT-23 gồm 5.696.295 bản ghi bằng kỹ thuật chia tách phân tầng Stratified 80/20 (4.557.036 dòng Train / 1.139.259 dòng Test độc lập), triệt tiêu hoàn toàn hiện tượng rò rỉ dữ liệu (Data Leakage).")
    add_bullet_para(doc, "Về mặt huấn luyện và đánh giá mô hình học máy: ", "Đã thực nghiệm đối sánh khách quan 5 thuật toán (Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM). Chứng minh được mô hình LightGBM ngang ngửa Decision Tree về độ chính xác (Accuracy = 99,99%, F1-Score = 99,99%), vượt trội hoàn toàn về tốc độ huấn luyện (15,85 giây so với 24,28 giây) và thời gian suy luận trên 1,13 triệu dòng kiểm thử độc lập chỉ mất 4,89 giây (0,0043 ms/luồng).")
    add_bullet_para(doc, "Về mặt xây dựng hệ thống thực tiễn: ", "Đã phát triển thành công hệ thống phần mềm giả lập Tấn công - Phòng thủ 3 bên hoàn chỉnh gồm: Kẻ tấn công Red Team Console (:9090), Trạm gác AI NIDS/IPS cho Admin SOC (:5000), và Thiết bị IoT Nạn nhân cho Người sử dụng (:8088 & :2323), hỗ trợ tự động chặn IP độc hại theo thời gian thực.")

    add_heading_custom(doc, "2. Hạn chế của đề tài", level=2)
    add_bullet_para(doc, "Phân loại chi tiết đa lớp ở cấp độ mô hình gốc: ", "Mô hình học máy lõi hiện tại được huấn luyện tối ưu cho bài toán phân loại nhị phân (Benign vs. Malicious) kết hợp tầng suy luận hành vi hậu xử lý; việc phân tách trực tiếp giữa các biến thể con có hành vi quét cổng giống hệt nhau (như Mirai SYN Scan và Hajime SYN Scan thuần túy) chỉ dựa trên 1 dòng log đơn lẻ vẫn cần thêm thông tin ngữ cảnh theo chuỗi thời gian (Time-window Aggregation).")
    add_bullet_para(doc, "Mô hình thực nghiệm dạng Simulation Testbed: ", "Hệ thống demo hiện tại giao tiếp qua REST API giả lập luồng mạng, chưa tích hợp module kernel packet sniffing (libpcap/eBPF) để tự động bắt gói tin thô trực tiếp từ luồng mạng vật lý.")

    add_heading_custom(doc, "3. Hướng phát triển của đề tài", level=2)
    add_bullet_para(doc, "Tích hợp trực tiếp với Zeek/Suricata và eBPF/XDP trên phần cứng Raspberry Pi / OpenWrt Router: ", "Triển khai mô hình LightGBM đã đóng gói lên cổng mạng biên vật lý (như Raspberry Pi 4/5 chạy OpenWrt) kết hợp trình bắt gói tin trực tiếp qua nhân Linux (eBPF/iptables) để chặn gói tin ở tầng Kernel.")
    add_bullet_para(doc, "Kết hợp Học sâu chuỗi thời gian (LSTM / Transformer Flow Sequence) và Học liên kết (Federated Learning): ", "Kết hợp LightGBM với mạng nơ-ron chuỗi thời gian để phát hiện các cuộc tấn công C&C ngầm kéo dài, đồng thời ứng dụng Federated Learning giúp nhiều cổng Gateway IoT cùng cập nhật tri thức về biến thể Botnet mới mà không cần chia sẻ dữ liệu thô của người dùng.")

    doc.add_page_break()

    # =========================================================================
    # TÀI LIỆU THAM KHẢO (16 TÀI LIỆU IEEE/USENIX CHUẨN)
    # =========================================================================
    add_heading_custom(doc, "TÀI LIỆU THAM KHẢO", level=1)
    references = [
        "[1] S. Garcia, A. Parmisano, and M. J. Erquiaga, \"IoT-23: A labeled dataset with malicious and benign IoT network traffic,\" Stratosphere Laboratory, AIC Group, FEL, Czech Technical University in Prague, Czech Republic, Tech. Rep., Jan. 2020. [Online]. Available: https://www.stratosphereips.org/datasets-iot23",
        "[2] M. Antonakakis et al., \"Understanding the Mirai Botnet,\" in Proc. 26th USENIX Security Symposium (USENIX Security 17), Vancouver, BC, Canada, Aug. 2017, pp. 1093–1110.",
        "[3] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.-Y. Liu, \"LightGBM: A Highly Efficient Gradient Boosting Decision Tree,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, Long Beach, CA, USA, 2017, pp. 3146–3154.",
        "[4] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" in Proc. 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16), San Francisco, CA, USA, Aug. 2016, pp. 785–794.",
        "[5] S. Edwards and I. Profetis, \"Hajime: Analysis of a decentralized internet worm for IoT devices,\" Rapidity Networks, Security Research Report, Oct. 2016.",
        "[6] J. Kroustek, V. Iliushin, A. Shirokova, J. Neduchal, and M. Hron, \"Torii botnet - Not another Mirai variant,\" Avast Blog, Sept. 2018. https://blog.avast.com/new-torii-botnet-threat-research",
        "[7] V. Paxson, \"Bro: A system for detecting network intruders in real-time,\" Computer Networks, vol. 31, no. 23–24, pp. 2435–2463, Dec. 1999 (Zeek Network Security Monitor Project).",
        "[8] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, Oct. 2001.",
        "[9] Y. Meidan et al., \"N-BaIoT: Network-Based Detection of IoT Botnet Attacks Using Deep Autoencoders,\" IEEE Pervasive Computing, vol. 17, no. 3, pp. 12–22, Jul.–Sept. 2018.",
        "[10] N. Koroniotis, N. Moustafa, E. Sitnikova, and B. Turnbull, \"Towards the development of realistic botnet dataset in the Internet of Things for network forensic analytics: Bot-IoT dataset,\" Future Generation Computer Systems, vol. 100, pp. 779–796, Nov. 2019.",
        "[11] I. Ullah and Q. H. Mahmoud, \"A Scheme for Generating a Dataset for Anomalous Activity Detection in IoT Networks,\" in Proc. Canadian Conference on Artificial Intelligence, Ottawa, ON, Canada, May 2020, pp. 508–520.",
        "[12] A. Alsaedi, N. Moustafa, Z. Tari, A. Mahmood, and A. Anwar, \"TON_IoT Telemetry Dataset: A New Generation Dataset of IoT and IIoT for Data-Driven Intrusion Detection Systems,\" IEEE Access, vol. 8, pp. 165130–165150, 2020.",
        "[13] C. Kolias, G. Kambourakis, A. Stavrou, and J. Voas, \"DDoS in the IoT: Mirai and Other Botnets,\" IEEE Computer, vol. 50, no. 7, pp. 80–84, Jul. 2017.",
        "[14] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research (JMLR), vol. 12, pp. 2825–2830, Oct. 2011.",
        "[15] Khoa Công nghệ Thông tin - Trường Đại học Bách Khoa, Đại học Đà Nẵng, \"Đề cương chi tiết và Bài giảng Học phần Kiểm thử xâm nhập (Penetration Testing),\" Lưu hành nội bộ, Đà Nẵng, 2025.",
        "[16] OWASP Foundation, \"OWASP Internet of Things (IoT) Top 10 Security Vulnerabilities Project,\" OWASP Technical Standard, 2024.",
    ]
    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Cm(0.8)
        p_ref.paragraph_format.first_line_indent = Cm(-0.8)
        p_ref.paragraph_format.line_spacing = 1.3
        p_ref.paragraph_format.space_after = Pt(5)
        r = p_ref.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12.5)

    doc.save(OUT_DOCX_1)
    os.makedirs(os.path.dirname(OUT_DOCX_2), exist_ok=True)
    shutil.copy2(OUT_DOCX_1, OUT_DOCX_2)
    print(f"\n[+] ĐÃ XUẤT THÀNH CÔNG BÁO CÁO WORD TẠI:\n    1) {OUT_DOCX_1}\n    2) {OUT_DOCX_2}")


if __name__ == "__main__":
    build_complete_word_report()

