# -*- coding: utf-8 -*-
"""
Script xây dựng lại toàn bộ Slide Thuyết Trình Bảo Vệ Đồ Án Cuối Kỳ (Nhóm 4)
Đề tài: Phát hiện và phân loại hành vi mã độc Botnet trên thiết bị IoT sử dụng Machine Learning
Tập dữ liệu: Stratosphere IoT-23 (5.696.295 dòng)

Quy chuẩn kỹ thuật:
- Tỷ lệ 16:9 Widescreen (13.333" x 7.5").
- Bảng màu thống nhất: Midnight Navy (#0A192F), Primary Blue (#0284C7), Slate Gray (#0F172A), Crisp White (#FFFFFF).
- Header banner đồng bộ, category badge, slide counter, footer nhóm.
- Tối đa ~6 bullet points/slide, không quá tải chữ.
- 1 Callout Takeaway card nổi bật ở cuối mỗi slide.
- Nhúng hình ảnh lớn 300 DPI trên các slide biểu đồ (Slide 5, 6, 7, 8, 9, 10, 11).
- Số liệu chuẩn hóa 100% khớp với Báo cáo Word và kết quả audit.
"""

import os
import sys
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- CẤU HÌNH ĐƯỜNG DẪN & MÀU SẮC ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
ASSETS_DIR = os.path.join(PROJECT_DIR, "report_assets")
OUTPUT_PPTX = os.path.join(PROJECT_DIR, "Slide_Thuyet_Trinh_IoT_Botnet_ML_Nhom4.pptx")
COPY_PPTX = os.path.abspath(os.path.join(PROJECT_DIR, "..", "Pentest", "Slide_Thuyet_Trinh_IoT_Botnet_ML_Nhom4.pptx"))

# Palette
C_NAVY_DARK   = RGBColor(10, 25, 47)      # #0A192F - Midnight Navy
C_NAVY_LIGHT  = RGBColor(13, 59, 102)     # #0D3B66 - Deep Navy Blue
C_ACCENT_BLUE = RGBColor(2, 132, 199)     # #0284C7 - Electric Sky Blue
C_ACCENT_CYAN = RGBColor(56, 189, 248)    # #38BDF8 - Bright Cyan
C_BG_LIGHT    = RGBColor(248, 250, 252)   # #F8FAFC - Off-white canvas
C_WHITE       = RGBColor(255, 255, 255)   # #FFFFFF
C_TEXT_DARK   = RGBColor(15, 23, 42)      # #0F172A - Slate Dark
C_TEXT_MUTED  = RGBColor(71, 85, 105)     # #475569 - Slate Medium
C_BORDER      = RGBColor(203, 213, 225)   # #CBD5E1 - Border Gray
C_TAKEAWAY_BG = RGBColor(240, 249, 255)   # #F0F9FF - Soft Blue Pill
C_GREEN       = RGBColor(16, 185, 129)    # #10B981 - Success Green
C_RED         = RGBColor(239, 68, 68)     # #EF4444 - Alert Red

FONT_HEADING = "Arial"
FONT_BODY = "Arial"

def set_shape_border(shape, color, width=Pt(1)):
    """Thiết lập viền cho shape"""
    shape.line.color.rgb = color
    shape.line.width = width

def add_header(slide, chapter_tag, title_text, right_tag="Học phần Kiểm thử Xâm nhập"):
    """Header banner chuẩn cho các slide nội dung (Slide 2 - 13)"""
    # Background banner
    banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.18))
    banner.fill.solid()
    banner.fill.fore_color.rgb = C_NAVY_DARK
    banner.line.color.rgb = C_ACCENT_BLUE
    banner.line.width = Pt(1.5)

    # Accent color strip at bottom of banner
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.04))
    strip.fill.solid()
    strip.fill.fore_color.rgb = C_ACCENT_BLUE
    strip.line.fill.background()

    # Category Badge
    badge_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.12), Inches(8.0), Inches(0.28))
    tf_b = badge_box.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = chapter_tag.upper()
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(10.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_ACCENT_CYAN

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.38), Inches(8.5), Inches(0.72))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(17.5)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE

    # Right Tag (School / Subject)
    right_box = slide.shapes.add_textbox(Inches(9.2), Inches(0.22), Inches(3.5), Inches(0.7))
    tf_r = right_box.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.text = right_tag
    p_r.font.name = FONT_BODY
    p_r.font.size = Pt(11)
    p_r.font.bold = True
    p_r.font.color.rgb = RGBColor(186, 230, 253)

    p_r2 = tf_r.add_paragraph()
    p_r2.alignment = PP_ALIGN.RIGHT
    p_r2.text = "ĐH Bách Khoa - ĐH Đà Nẵng"
    p_r2.font.name = FONT_BODY
    p_r2.font.size = Pt(9.5)
    p_r2.font.color.rgb = RGBColor(148, 163, 184)

def add_footer(slide, slide_num, total_slides=14):
    """Footer bar chuẩn đồng bộ cho tất cả các slide"""
    # Top divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(7.02), Inches(12.133), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = C_BORDER
    line.line.fill.background()

    # Left text: University & Faculty
    fb_left = slide.shapes.add_textbox(Inches(0.6), Inches(7.08), Inches(4.5), Inches(0.35))
    tf_l = fb_left.text_frame
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = 0
    p_l = tf_l.paragraphs[0]
    p_l.text = "Trường ĐH Bách Khoa - ĐH Đà Nẵng | Khoa CNTT"
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(9)
    p_l.font.color.rgb = C_TEXT_MUTED

    # Center text: Group info
    fb_mid = slide.shapes.add_textbox(Inches(4.8), Inches(7.08), Inches(5.0), Inches(0.35))
    tf_m = fb_mid.text_frame
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = 0
    p_m = tf_m.paragraphs[0]
    p_m.alignment = PP_ALIGN.CENTER
    p_m.text = "Nhóm 4: Nguyễn Công Minh (0825385889) & Ngô Văn Công (0775745371)"
    p_m.font.name = FONT_BODY
    p_m.font.size = Pt(9)
    p_m.font.color.rgb = C_TEXT_MUTED

    # Right text: Slide number
    fb_right = slide.shapes.add_textbox(Inches(10.5), Inches(7.08), Inches(2.233), Inches(0.35))
    tf_r = fb_right.text_frame
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.text = f"Slide {slide_num}/{total_slides}"
    p_r.font.name = FONT_HEADING
    p_r.font.size = Pt(9.5)
    p_r.font.bold = True
    p_r.font.color.rgb = C_NAVY_DARK

def add_takeaway_card(slide, takeaway_text, left=Inches(0.6), top=Inches(6.05), width=Inches(12.133), height=Inches(0.85)):
    """Card tóm tắt cốt lõi (Takeaway) ở cuối slide"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = C_TAKEAWAY_BG
    set_shape_border(card, C_ACCENT_BLUE, Pt(1.5))

    tb = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.10), width - Inches(0.36), height - Inches(0.20))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "📌 ĐIỂM CỐT LÕI: "
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    # Add text in same paragraph or run
    run = p.add_run()
    run.text = takeaway_text
    run.font.name = FONT_BODY
    run.font.size = Pt(10.5)
    run.font.bold = False
    run.font.color.rgb = C_TEXT_DARK

def add_card(slide, left, top, width, height, title=None, bg_color=C_WHITE, border_color=C_BORDER):
    """Tạo khối card container để chứa nội dung hoặc hình ảnh"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    set_shape_border(card, border_color, Pt(1))

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.12), width - Inches(0.36), Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK
    return card

def add_bullet_points(slide, left, top, width, height, points, font_size=Pt(10.5), space_after=Pt(5)):
    """Thêm danh sách gạch đầu dòng có định dạng keyword in đậm"""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    for i, pt_data in enumerate(points):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = space_after
        p.line_spacing = 1.15

        # Format: (keyword, normal_text, optional_color)
        if isinstance(pt_data, tuple):
            kw, text = pt_data[0], pt_data[1]
            c_kw = pt_data[2] if len(pt_data) > 2 else C_NAVY_DARK

            r1 = p.add_run()
            r1.text = "▪ " + kw + ": "
            r1.font.name = FONT_HEADING
            r1.font.size = font_size
            r1.font.bold = True
            r1.font.color.rgb = c_kw

            r2 = p.add_run()
            r2.text = text
            r2.font.name = FONT_BODY
            r2.font.size = font_size
            r2.font.bold = False
            r2.font.color.rgb = C_TEXT_DARK
        else:
            r = p.add_run()
            r.text = "▪ " + str(pt_data)
            r.font.name = FONT_BODY
            r.font.size = font_size
            r.font.color.rgb = C_TEXT_DARK

def safe_add_image(slide, image_filename, left, top, width, height):
    """Nhúng ảnh an toàn kèm khung viền chuẩn"""
    img_path = os.path.join(ASSETS_DIR, image_filename)
    if os.path.exists(img_path):
        # Card backing
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        set_shape_border(card, C_BORDER, Pt(1))

        # Picture inside card (with small 0.05in padding)
        pad = Inches(0.06)
        slide.shapes.add_picture(img_path, left + pad, top + pad, width - 2 * pad, height - 2 * pad)
        return True
    else:
        print(f"[!] WARNING: Không tìm thấy ảnh {img_path}")
        return False


def build_presentation():
    print("[*] Bắt đầu khởi tạo Presentation 16:9 Widescreen...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    # =========================================================================
    # SLIDE 1: TRANG BÌA (MIDNIGHT NAVY EXECUTIVE)
    # =========================================================================
    print("[*] Đang xây dựng Slide 1: Trang Bìa...")
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY_DARK
    bg1.line.fill.background()

    # Header Top Bar in Dark
    h1 = s1.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.5))
    tf_h1 = h1.text_frame
    tf_h1.word_wrap = True
    p = tf_h1.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "ĐẠI HỌC ĐÀ NẴNG — TRƯỜNG ĐẠI HỌC BÁCH KHOA — KHOA CÔNG NGHỆ THÔNG TIN"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_CYAN

    p_sub = tf_h1.add_paragraph()
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.text = "BÁO CÁO ĐỒ ÁN CUỐI KỲ HỌC PHẦN: KIỂM THỬ XÂM NHẬP (PENETRATION TESTING)"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(10)
    p_sub.font.color.rgb = RGBColor(148, 163, 184)

    # Main Project Title
    t1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(1.6))
    tf_t1 = t1.text_frame
    tf_t1.word_wrap = True
    p_t = tf_t1.paragraphs[0]
    p_t.alignment = PP_ALIGN.CENTER
    p_t.text = "PHÁT HIỆN VÀ PHÂN LOẠI HÀNH VI MÃ ĐỘC BOTNET\nTRÊN THIẾT BỊ IoT (MIRAI, HAJIME, TORII)\nSỬ DỤNG MACHINE LEARNING"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(23)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE

    # Tagline / Subtitle
    t_tag = s1.shapes.add_textbox(Inches(1.0), Inches(3.1), Inches(11.333), Inches(0.5))
    tf_tag = t_tag.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.alignment = PP_ALIGN.CENTER
    p_tag.text = "Khai phá toàn diện bộ dữ liệu chuẩn Stratosphere IoT-23 (5.696.295 Flows)  |  Đóng gói Hệ thống Thực nghiệm NIDS/IPS 3 Bên"
    p_tag.font.name = FONT_BODY
    p_tag.font.size = Pt(11.5)
    p_tag.font.color.rgb = RGBColor(186, 230, 253)

    # 4 KPI Highlight Cards
    kpi_data = [
        ("5.696.295", "Tổng số dòng IoT-23", "Stratified Split 80/20 chuẩn"),
        ("5 Thuật Toán ML", "Đánh giá đa chiều", "LR, DT, RF, XGB, LightGBM"),
        ("99,99% F1-Score", "LightGBM NIDS Lõi", "Kiểm định trên 1,14M dòng Test"),
        ("Hệ Thống 3 Bên", "Demo thực chiến trực tiếp", "Attacker -> SOC -> Victim IoT")
    ]
    card_w = Inches(2.78)
    card_h = Inches(1.4)
    start_x = Inches(0.8)
    gap = Inches(0.2)
    top_y = Inches(3.85)

    for i, (val, label, sub) in enumerate(kpi_data):
        x = start_x + i * (card_w + gap)
        c_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, card_w, card_h)
        c_shape.fill.solid()
        c_shape.fill.fore_color.rgb = C_NAVY_LIGHT
        set_shape_border(c_shape, C_ACCENT_BLUE, Pt(1.5))

        tb = s1.shapes.add_textbox(x + Inches(0.1), top_y + Inches(0.12), card_w - Inches(0.2), card_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = val
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(15.5)
        p1.font.bold = True
        p1.font.color.rgb = C_ACCENT_CYAN

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = label
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_WHITE

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        p3.text = sub
        p3.font.name = FONT_BODY
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = RGBColor(148, 163, 184)

    # Student Info Banner (Bottom)
    st_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.65), Inches(10.933), Inches(1.15))
    st_shape.fill.solid()
    st_shape.fill.fore_color.rgb = RGBColor(15, 23, 42)
    set_shape_border(st_shape, C_BORDER, Pt(1))

    st_tb = s1.shapes.add_textbox(Inches(1.4), Inches(5.75), Inches(10.533), Inches(0.95))
    st_tf = st_tb.text_frame
    st_tf.word_wrap = True

    p_g = st_tf.paragraphs[0]
    p_g.alignment = PP_ALIGN.CENTER
    p_g.text = "NHÓM THỰC HIỆN: NHÓM 4 — CHUYÊN NGÀNH AN TOÀN THÔNG TIN"
    p_g.font.name = FONT_HEADING
    p_g.font.size = Pt(11)
    p_g.font.bold = True
    p_g.font.color.rgb = C_ACCENT_CYAN

    p_mem = st_tf.add_paragraph()
    p_mem.alignment = PP_ALIGN.CENTER
    p_mem.text = "1. Nguyễn Công Minh (SĐT: 0825385889)      |      2. Ngô Văn Công (SĐT: 0775745371)"
    p_mem.font.name = FONT_HEADING
    p_mem.font.size = Pt(12)
    p_mem.font.bold = True
    p_mem.font.color.rgb = C_WHITE

    p_gv = st_tf.add_paragraph()
    p_gv.alignment = PP_ALIGN.CENTER
    p_gv.text = "Giảng viên phụ trách học phần: Bộ môn An Toàn Thông Tin — Khoa Công Nghệ Thông Tin"
    p_gv.font.name = FONT_BODY
    p_gv.font.size = Pt(9.5)
    p_gv.font.color.rgb = RGBColor(148, 163, 184)

    # =========================================================================
    # SLIDE 2: MỞ ĐẦU (TÍNH CẤP THIẾT, MỤC TIÊU & BỐ CỤC)
    # =========================================================================
    print("[*] Đang xây dựng Slide 2: Mở Đầu...")
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "MỞ ĐẦU", "TÍNH CẤP THIẾT, MỤC TIÊU VÀ BỐ CỤC ĐỀ TÀI")
    add_footer(s2, 2)

    # Left Card: Tính cấp thiết
    add_card(s2, Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55), "1. Tính cấp thiết & Lý do chọn đề tài")
    pts_s2_left = [
        ("Bề mặt tấn công IoT khổng lồ", "Hàng tỷ Camera IP, Router chạy Linux nhúng mở cổng Telnet/SSH với mật khẩu mặc định yếu."),
        ("Hiểm họa Botnet thế hệ mới", "Mirai (DDoS Terabit), Hajime (P2P không C&C cố định), Torii (gián điệp đa tầng, persistence cao)."),
        ("IDS truyền thống lỗi thời", "Hệ thống dựa trên chữ ký tĩnh (Snort/Suricata) bất lực trước biến thể mã độc mới và mã hóa payload."),
        ("Tiếp cận Flow-based Machine Learning", "Phân loại hành vi luồng mạng (Zeek Conn-Log) tại Gateway cho phép phát hiện sớm với độ trễ thấp."),
        ("Tính thực tiễn cao cho Pentest", "Kết hợp trọn vẹn tấn công Red Team (giả lập botnet) và phòng thủ Blue Team (AI NIDS/IPS).")
    ]
    add_bullet_points(s2, Inches(0.8), Inches(1.85), Inches(5.5), Inches(3.9), pts_s2_left, font_size=Pt(10.5), space_after=Pt(6))

    # Right Card: Mục tiêu & Bố cục 3 Chương
    add_card(s2, Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55), "2. Mục tiêu nghiên cứu & Bố cục Báo cáo")
    pts_s2_right = [
        ("Chương 1 - Cơ sở lý thuyết", "Giải phẫu kiến trúc IoT, chu trình lây nhiễm của Mirai, Hajime, Torii, định dạng Zeek Log & 5 mô hình ML."),
        ("Chương 2 - Đề xuất mô hình & Thực nghiệm", "Xử lý trọn vẹn 5,69 triệu dòng IoT-23, chia 80/20 Stratified, huấn luyện và đánh giá đối chuẩn 5 mô hình ML."),
        ("Chương 3 - Hệ thống thực nghiệm NIDS 3 bên", "Đóng gói model LightGBM vào hệ thống 3 bên: Attacker Console (:9090), Guardian SOC (:5000), Victim IoT (:8088)."),
        ("Kiểm thử thực chiến 5 kịch bản", "Xác thực khả năng nhận diện quét cổng, brute-force, C&C beaconing và DDoS với độ trễ suy luận < 0,5 ms/luồng."),
        ("Kết luận & Định hướng mở rộng", "Tổng kết kết quả thực nghiệm, đánh giá ranh giới mô hình và định hướng tích hợp eBPF/XDP vào nhân Linux.")
    ]
    add_bullet_points(s2, Inches(7.0), Inches(1.85), Inches(5.5), Inches(3.9), pts_s2_right, font_size=Pt(10.5), space_after=Pt(6))

    add_takeaway_card(s2, "Đề tài giải quyết toàn diện bài toán phòng ngự Botnet IoT bằng cách kết hợp thực nghiệm học máy quy mô lớn (5,69 triệu dòng) với hệ thống mô phỏng 3 bên thời gian thực, đáp ứng chuẩn mực khắt khe của học phần Kiểm thử Xâm nhập.")

    # =========================================================================
    # SLIDE 3: CHƯƠNG 1 (GIẢI PHẪU 3 HỌ BOTNET IoT)
    # =========================================================================
    print("[*] Đang xây dựng Slide 3: Giải phẫu 3 họ Botnet...")
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "CHƯƠNG 1 | CƠ SỞ LÝ THUYẾT", "GIẢI PHẪU HÀNH VI 3 HỌ MÃ ĐỘC BOTNET IoT: MIRAI, HAJIME, TORII")
    add_footer(s3, 3)

    card_w3 = Inches(3.88)
    # Col 1: Mirai
    add_card(s3, Inches(0.6), Inches(1.35), card_w3, Inches(4.55), "1. MIRAI BOTNET (DDoS Quy mô lớn)")
    pts_mirai = [
        ("Kiến trúc", "Máy chủ C&C tập trung kết hợp máy chủ Loader phân phối payload."),
        ("Cơ chế lây lan", "Quét ngang cổng TCP 23/2323 với tốc độ cao; brute-force danh sách 62 mật khẩu mặc định cứng."),
        ("Mục tiêu tấn công", "Huy động mạng botnet phát động DDoS quy mô Terabit (SYN Flood, UDP Flood, ACK Flood, HTTP Flood)."),
        ("Dấu hiệu Zeek Log", "Hàng loạt luồng có trạng thái conn_state = S0, orig_bytes = 0, duration = 0 và history = S.")
    ]
    add_bullet_points(s3, Inches(0.75), Inches(1.85), card_w3 - Inches(0.3), Inches(3.9), pts_mirai, font_size=Pt(10), space_after=Pt(6))

    # Col 2: Hajime
    add_card(s3, Inches(4.72), Inches(1.35), card_w3, Inches(4.55), "2. HAJIME BOTNET (Mạng P2P Tinh vi)")
    pts_hajime = [
        ("Kiến trúc", "Phi tập trung ngang hàng (Peer-to-Peer) dựa trên bảng băm phân tán BitTorrent DHT, không máy chủ C&C."),
        ("Cơ chế lây lan", "Quét Telnet (23/2323) kết hợp khai thác lỗ hổng TR-069 (cổng 7547) và SOAP/UPnP (5555)."),
        ("Hành vi đặc thù", "Sau khi chiếm quyền, Hajime tự đóng cổng 23, 7547, 5555 để ngăn chặn Mirai xâm nhập."),
        ("Dấu hiệu Zeek Log", "Lưu lượng quét SYN kết hợp các gói tin UDP đồng bộ DHT liên tục ở các cổng ngẫu nhiên.")
    ]
    add_bullet_points(s3, Inches(4.87), Inches(1.85), card_w3 - Inches(0.3), Inches(3.9), pts_hajime, font_size=Pt(10), space_after=Pt(6))

    # Col 3: Torii
    add_card(s3, Inches(8.84), Inches(1.35), card_w3, Inches(4.55), "3. TORII BOTNET (APT Gián Điệp Bền Vững)")
    pts_torii = [
        ("Kiến trúc", "C&C đa tầng, thiết kế module hóa hỗ trợ đa nền tảng CPU (ARM, MIPS, x86, PowerPC, SuperH)."),
        ("Cơ chế lây lan", "Xâm nhập qua Telnet/SSH, cài đặt 6 cơ chế lưu trú (Persistence) để sống sót sau khi khởi động lại."),
        ("Mục tiêu tấn công", "Thu thập thông tin thiết bị, đánh cắp dữ liệu nhạy cảm và duy trì Reverse Shell bí mật."),
        ("Dấu hiệu Zeek Log", "Các luồng kết nối C&C beaconing định kỳ, lưu lượng 2 chiều cân đối, duration kéo dài.")
    ]
    add_bullet_points(s3, Inches(8.99), Inches(1.85), card_w3 - Inches(0.3), Inches(3.9), pts_torii, font_size=Pt(10), space_after=Pt(6))

    add_takeaway_card(s3, "Cả 3 họ Botnet đều để lại dấu ấn hành vi đặc trưng trên Zeek Conn-Log (Mirai thiên về S0 bão táp, Hajime dùng P2P DHT, Torii dùng C&C beaconing chu kỳ), cho phép Machine Learning phân loại chính xác mà không phụ thuộc payload mã hóa.")

    # =========================================================================
    # SLIDE 4: CHƯƠNG 1 (KIẾN TRÚC AI NIDS & 5 THUẬT TOÁN ML)
    # =========================================================================
    print("[*] Đang xây dựng Slide 4: Kiến trúc AI NIDS & 5 ML...")
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "CHƯƠNG 1 | CƠ SỞ LÝ THUYẾT", "KIẾN TRÚC PHÒNG VỆ AI NIDS & NGUYÊN LÝ 5 THUẬT TOÁN HỌC MÁY")
    add_footer(s4, 4)

    # Left: Pipeline kiến trúc NIDS
    add_card(s4, Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55), "Quy trình phân tích luồng NIDS tại Gateway")
    pts_nids_arch = [
        ("Tầng thu thập gói tin", "Trích xuất lưu lượng mạng thô (PCAP) tại cổng Gateway thiết bị IoT."),
        ("Tầng phân tích luồng Zeek", "Tạo bản ghi Zeek Conn-Log theo 5-tuple (src_ip, src_p, dst_ip, dst_p, proto)."),
        ("Tầng trích xuất đặc trưng", "Chuẩn hóa 12 đặc trưng hành vi (loại bỏ hoàn toàn IP/UID chống học vẹt topology mạng)."),
        ("Động cơ suy luận AI (Inference)", "Mô hình Machine Learning phân loại nhị phân (0: Benign, 1: Malicious) trong thời gian < 0,5 ms."),
        ("Tầng phản ứng IPS tự động", "Tự động kích hoạt Dynamic IP Drop List và gửi cảnh báo thời gian thực về SOC.")
    ]
    add_bullet_points(s4, Inches(0.8), Inches(1.85), Inches(5.5), Inches(3.9), pts_nids_arch, font_size=Pt(10.5), space_after=Pt(6))

    # Right: Cơ sở 5 thuật toán
    add_card(s4, Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55), "Cơ sở lý thuyết 5 thuật toán đối sánh")
    pts_5ml = [
        ("1. Logistic Regression", "Mô hình phân lớp tuyến tính dùng hàm Sigmoid; tính toán nhanh nhưng kém hiệu quả trước biên quyết định phi tuyến phức tạp."),
        ("2. Decision Tree (Cây quyết định)", "Phân nhánh dữ liệu theo chỉ số Gini/Entropy; trực quan, tốc độ xử lý nhanh nhưng dễ bị quá khớp (overfitting)."),
        ("3. Random Forest (Rừng ngẫu nhiên)", "Kỹ thuật Bagging kết hợp nhiều cây quyết định; giảm phương sai hiệu quả nhưng thời gian huấn luyện tăng mạnh trên tập dữ liệu lớn."),
        ("4. XGBoost (Extreme Gradient Boosting)", "Tối ưu hóa Gradient Boosting qua khai triển Taylor bậc 2; kiểm soát overfitting tốt nhưng tiêu tốn bộ nhớ RAM lớn."),
        ("5. LightGBM (Lõi đề xuất)", "Sử dụng Histogram binning và kỹ thuật Leaf-wise; huấn luyện siêu nhanh và tối ưu tuyệt đối cho dữ liệu dạng bảng lớn.")
    ]
    add_bullet_points(s4, Inches(7.0), Inches(1.85), Inches(5.5), Inches(3.9), pts_5ml, font_size=Pt(10), space_after=Pt(5))

    add_takeaway_card(s4, "Hệ thống AI NIDS phân tích lưu lượng ở cấp độ luồng mạng (Flow-level), cho phép nhận diện các đòn tấn công Botnet với chi phí tính toán cực thấp, thích hợp triển khai tại biên trên thiết bị Gateway IoT.")

    # =========================================================================
    # SLIDE 5: CHƯƠNG 2 (TẬP DỮ LIỆU STRATOSPHERE IOT-23 & 12 ĐẶC TRƯNG)
    # =========================================================================
    print("[*] Đang xây dựng Slide 5: Dataset IoT-23 & 12 đặc trưng...")
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "CHƯƠNG 2 | THỰC NGHIỆM & KẾT QUẢ", "BỘ DỮ LIỆU STRATOSPHERE IoT-23 & KHÔNG GIAN 12 ĐẶC TRƯNG")
    add_footer(s5, 5)

    # Left: Chi tiết bộ dữ liệu & 12 đặc trưng
    add_card(s5, Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55), "Quy mô Bộ dữ liệu & 12 Đặc trưng Chuẩn hóa")
    pts_s5_left = [
        ("Tổng quy mô 100% dữ liệu", "5.696.295 bản ghi Zeek Conn-Log (5.198.337 Malicious - 91,26% và 497.958 Benign - 8,74%)."),
        ("Phân chia Stratified Split 80/20", "Train Set: 4.557.036 dòng | Test Set: 1.139.259 dòng (giữ nguyên tỷ lệ nhãn, random_state=42)."),
        ("9 Đặc trưng số (Numeric)", "id.resp_p, duration, orig_bytes, resp_bytes, orig_pkts, resp_pkts, orig_ip_bytes, resp_ip_bytes, id.orig_p (chuẩn hóa StandardScaler)."),
        ("3 Đặc trưng định danh (Categorical)", "proto, conn_state, history (mã hóa One-Hot Encoding độc lập trên Train)."),
        ("Triệt tiêu Data Leakage 100%", "Loại bỏ hoàn toàn IP nguồn/đích, UID thiết bị và trường service (chống học vẹt topology mạng).")
    ]
    add_bullet_points(s5, Inches(0.8), Inches(1.85), Inches(5.5), Inches(3.9), pts_s5_left, font_size=Pt(10), space_after=Pt(6))

    # Right: Nhúng ảnh phân bố nhãn fig2_class_distribution.png
    safe_add_image(s5, "fig2_class_distribution.png", Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55))

    add_takeaway_card(s5, "Việc áp dụng Stratified Split 80/20 trên toàn bộ 5,69 triệu dòng và loại bỏ triệt để các trường định danh (IP, UID, service) đảm bảo mô hình học được bản chất hành vi mạng của Botnet, triệt tiêu 100% nguy cơ Data Leakage.")

    # =========================================================================
    # SLIDE 6: CHƯƠNG 2 (EDA PHÂN TÍCH KHÁM PHÁ DỮ LIỆU - 2 HÌNH)
    # =========================================================================
    print("[*] Đang xây dựng Slide 6: EDA Khám Phá Dữ Liệu (2 Hình)...")
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "CHƯƠNG 2 | THỰC NGHIỆM & KẾT QUẢ", "PHÂN TÍCH KHÁM PHÁ DỮ LIỆU (EDA) TRÊN ZEEK CONN-LOG")
    add_footer(s6, 6)

    # 2 hình lớn cạnh nhau: fig3_conn_state_analysis.png & fig10_top_ports.png
    img_w6 = Inches(5.9)
    img_h6 = Inches(4.55)
    safe_add_image(s6, "fig3_conn_state_analysis.png", Inches(0.6), Inches(1.35), img_w6, img_h6)
    safe_add_image(s6, "fig10_top_ports.png", Inches(6.8), Inches(1.35), img_w6, img_h6)

    add_takeaway_card(s6, "Trạng thái conn_state = S0 chiếm hơn 91% lưu lượng độc hại (do quét cổng/SYN flood không nhận phản hồi), nhưng S0 cũng chiếm 65,5% lưu lượng sạch (kết nối timeout); do đó mô hình không thể học vẹt một mình S0 mà phải kết hợp chặt chẽ với cổng đích (Telnet: 23/2323, HTTP: 80/8080) và độ dài byte.")

    # =========================================================================
    # SLIDE 7: CHƯƠNG 2 (ĐỐI SÁNH 5 MÔ HÌNH HỌC MÁY & CHỌN LIGHTGBM)
    # =========================================================================
    print("[*] Đang xây dựng Slide 7: Benchmark 5 mô hình ML...")
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "CHƯƠNG 2 | THỰC NGHIỆM & KẾT QUẢ", "KẾT QUẢ THỰC NGHIỆM ĐỐI SÁNH 5 MÔ HÌNH & LÝ DO CHỌN LIGHTGBM")
    add_footer(s7, 7)

    # Left: Hình fig5_model_benchmark.png
    safe_add_image(s7, "fig5_model_benchmark.png", Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55))

    # Right: Bảng đối sánh và lý do chọn LightGBM
    add_card(s7, Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55), "Đối sánh thực nghiệm trên Validation Set (683.556 dòng)")

    # Tạo bảng nhỏ trong card bên phải
    tb_shape = s7.shapes.add_table(6, 4, Inches(7.0), Inches(1.85), Inches(5.533), Inches(1.6))
    table = tb_shape.table
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(1.2)
    table.columns[2].width = Inches(1.2)
    table.columns[3].width = Inches(1.333)

    headers = ["Mô hình", "Accuracy", "F1-Score", "Thời gian"]
    row_data = [
        ("Logistic Reg.", "98,32%", "99,08%", "28,67 s"),
        ("Decision Tree", "99,99%", "100,00%", "55,12 s"),
        ("Random Forest", "99,90%", "99,95%", "71,61 s"),
        ("XGBoost", "99,90%", "99,95%", "31,46 s"),
        ("LightGBM (Chọn)", "99,99%", "99,99%", "19,83 s")
    ]

    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        for p in cell.text_frame.paragraphs:
            p.font.name = FONT_HEADING
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE
            p.alignment = PP_ALIGN.CENTER

    for r, row in enumerate(row_data, 1):
        is_lgbm = (r == 5)
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(224, 242, 254) if is_lgbm else (C_WHITE if r % 2 == 1 else C_BG_LIGHT)
            for p in cell.text_frame.paragraphs:
                p.font.name = FONT_BODY
                p.font.size = Pt(9)
                p.font.bold = is_lgbm
                p.font.color.rgb = C_NAVY_DARK if is_lgbm else C_TEXT_DARK
                p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER

    # Bullet points lý do chọn LightGBM phía dưới bảng
    pts_why_lgbm = [
        ("Tốc độ huấn luyện số 1", "Chỉ 19,83 giây trên 4,55 triệu dòng (nhanh gấp 2,8 lần Decision Tree và 3,6 lần Random Forest)."),
        ("Ngang ngửa DT về độ chính xác", "Cả Decision Tree và LightGBM đều đạt 99,99% Accuracy trên tập validation."),
        ("Ngừa quá khớp (Overfitting)", "Tập hợp 100 cây boosting giúp LightGBM có tính khái quát hóa cao, không học vẹt như một cây quyết định đơn lẻ.")
    ]
    add_bullet_points(s7, Inches(7.0), Inches(3.6), Inches(5.533), Inches(2.1), pts_why_lgbm, font_size=Pt(9.5), space_after=Pt(4))

    add_takeaway_card(s7, "Tiêu chí chọn LightGBM không chỉ là độ chính xác (Decision Tree cũng đạt 99,99%), mà LightGBM vượt trội hoàn toàn về tốc độ huấn luyện (19,83s so với 55,12s của DT) và kiến trúc 100 boosting trees giúp mô hình bền vững trước biến động mạng, không bị quá khớp.")

    # =========================================================================
    # SLIDE 8: CHƯƠNG 2 (MA TRẬN NHẦM LẪN & ROC TRÊN 1.14M TEST - 2 HÌNH)
    # =========================================================================
    print("[*] Đang xây dựng Slide 8: Ma trận nhầm lẫn & ROC Test Set (2 Hình)...")
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "CHƯƠNG 2 | THỰC NGHIỆM & KẾT QUẢ", "ĐÁNH GIÁ TRÊN 1.139.259 DÒNG TEST: MA TRẬN NHẦM LẪN & ĐƯỜNG CONG ROC")
    add_footer(s8, 8)

    # 2 hình lớn: fig6_confusion_matrix.png & fig15_roc_curves.png
    safe_add_image(s8, "fig6_confusion_matrix.png", Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55))
    safe_add_image(s8, "fig15_roc_curves.png", Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55))

    add_takeaway_card(s8, "Trên 1.139.259 luồng Test độc lập hoàn toàn, LightGBM đạt TP = 1.039.649 (Recall 99,9983%, chỉ sót 18 luồng) và FPR = 0,12% (120/99.592 luồng sạch). Chỉ số AUC thực nghiệm tính bằng mã nguồn scripts/compute_roc.py đạt 0,999981 (LightGBM) và 0,999990 (RF), độ trễ suy luận batch chỉ 0,0043 ms/luồng.")

    # =========================================================================
    # SLIDE 9: CHƯƠNG 2 (FEATURE IMPORTANCE & TRAFFIC ASYMMETRY - 2 HÌNH)
    # =========================================================================
    print("[*] Đang xây dựng Slide 9: Feature Importance & Asymmetry (2 Hình)...")
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "CHƯƠNG 2 | THỰC NGHIỆM & KẾT QUẢ", "PHÂN TÍCH ĐÓNG GÓP ĐẶC TRƯNG & TÍNH BẤT ĐỐI XỨNG LƯU LƯỢNG")
    add_footer(s9, 9)

    # 2 hình lớn: fig4_feature_importance.png & fig7_traffic_asymmetry.png
    safe_add_image(s9, "fig4_feature_importance.png", Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55))
    safe_add_image(s9, "fig7_traffic_asymmetry.png", Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55))

    add_takeaway_card(s9, "Cổng đích (id.resp_p với 756 lần tách) và dung lượng byte (orig_bytes 512, resp_bytes 420) là các đặc trưng quan trọng nhất. Tấn công Botnet có tính bất đối xứng cực đoan: gửi nhiều gói tin thăm dò nhưng resp_bytes = 0 do thiết bị nạn nhân từ chối hoặc không kịp phản hồi.")

    # =========================================================================
    # SLIDE 10: CHƯƠNG 3 (HỆ THỐNG GIẢ LẬP TẤN CÔNG - PHÒNG THỦ 3 BÊN)
    # =========================================================================
    print("[*] Đang xây dựng Slide 10: Hệ thống giả lập 3 bên (fig1)...")
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "CHƯƠNG 3 | DEMO THỰC CHIẾN", "HỆ THỐNG GIẢ LẬP TẤN CÔNG - PHÒNG THỦ 3 BÊN THỜI GIAN THỰC")
    add_footer(s10, 10)

    # Left: Hình fig1_system_architecture.png
    safe_add_image(s10, "fig1_system_architecture.png", Inches(0.6), Inches(1.35), Inches(6.2), Inches(4.55))

    # Right: Chi tiết 3 Bên trong mô hình
    add_card(s10, Inches(7.0), Inches(1.35), Inches(5.733), Inches(4.55), "Cấu trúc 3 Thực thể Mô phỏng Hoàn chỉnh")
    pts_s10 = [
        ("Bên 1: Red Team Botnet (:9090)", "Module attacker_botnet_console.py đóng vai kẻ tấn công, phát động 5 kịch bản: Mirai Scan, Telnet Brute-force, Torii C&C, Hajime Flood, DoS."),
        ("Bên 2: AI NIDS Guardian Server (:5000)", "Module ai_nids_guardian_server.py đóng vai trò Trạm gác SOC Gateway, tích hợp model LightGBM 12 đặc trưng, phân tích luồng và ra quyết định ALLOW / BLOCK."),
        ("Bên 3: Victim IoT Server (:8088 / :2323)", "Module victim_iot_server.py giả lập thiết bị Camera IP / Router mở cổng Web (:8088) và daemon Telnet (:2323), tạo luồng sạch và chịu tải tấn công."),
        ("Cơ chế IPS Auto-Block", "Khi bật Auto-Block, Guardian tự động đưa IP tấn công vào Blacklist và chặn đứng ngay tại Gateway (HTTP 403)."),
        ("Lưu ý kỹ thuật rõ ràng", "Hệ thống demo là Testbed giả lập qua REST API flow payload; hướng phát triển thực tế sẽ tích hợp Zeek/libpcap capture gói tin mạng thô.")
    ]
    add_bullet_points(s10, Inches(7.2), Inches(1.85), Inches(5.333), Inches(3.9), pts_s10, font_size=Pt(9.5), space_after=Pt(5))

    add_takeaway_card(s10, "Hệ thống giả lập 3 bên hiện thực hóa hoàn chỉnh vòng lặp Attack-Defense trong bài toán Pentest, chứng minh tính khả thi của việc nhúng mô hình LightGBM vào hệ thống Gateway để phát hiện và ngăn chặn mã độc Botnet tự động.")

    # =========================================================================
    # SLIDE 11: CHƯƠNG 3 (KẾT QUẢ KIỂM THỬ 5 KỊCH BẢN TRÊN LIVE SOC)
    # =========================================================================
    print("[*] Đang xây dựng Slide 11: Live SOC Simulation (fig8)...")
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "CHƯƠNG 3 | DEMO THỰC CHIẾN", "KẾT QUẢ KIỂM THỬ THỰC CHIẾN 5 KỊCH BẢN TRÊN DASHBOARD SOC")
    add_footer(s11, 11)

    # Left: Hình fig8_live_soc_simulation.png
    safe_add_image(s11, "fig8_live_soc_simulation.png", Inches(0.6), Inches(1.35), Inches(6.4), Inches(4.55))

    # Right: Kết quả 5 kịch bản thử nghiệm
    add_card(s11, Inches(7.2), Inches(1.35), Inches(5.533), Inches(4.55), "Nhật ký Kiểm thử 5 Kịch bản (32 Luồng)")
    pts_s11 = [
        ("1. Lưu lượng Hợp lệ (Normal)", "4 luồng cảm biến MQTT (1883) & Web HTTP (80) -> AI: Benign (99,8%) -> Hành động: ALLOW."),
        ("2. Mirai Horizontal Port Scan", "8 luồng SYN tới các cổng 23, 2323, 80, 5555... (S0) -> AI: Malicious (99,9%) -> Hành động: BLOCK."),
        ("3. Telnet Brute-force Dictionary", "6 luồng thử mật khẩu (root:vizxv, admin:admin) cổng 2323 -> AI: Malicious -> Thêm IP vào Blacklist."),
        ("4. Torii Multi-stage C&C Beaconing", "6 luồng kết nối máy chủ điều khiển cổng 4444, 6667 -> AI: Malicious -> Cảnh báo Critical."),
        ("5. SYN Flood DDoS Tấn công Nạn nhân", "8 luồng bão gói tin gây quá tải -> AI: Malicious (99,9%) -> Kích hoạt ngắt kết nối lập tức."),
        ("Hiệu năng thực tế", "100% luồng độc hại bị chặn (0 False Negatives), độ trễ phản hồi API trung bình < 0,5 ms/luồng.")
    ]
    add_bullet_points(s11, Inches(7.4), Inches(1.85), Inches(5.133), Inches(3.9), pts_s11, font_size=Pt(9.2), space_after=Pt(4))

    add_takeaway_card(s11, "Toàn bộ 32 luồng trong 5 kịch bản thử nghiệm được mô hình AI NIDS phân loại chính xác 100%, tự động kích hoạt luật tường lửa khóa IP tấn công, giữ an toàn tuyệt đối cho thiết bị IoT nạn nhân.")

    # =========================================================================
    # SLIDE 12: CHƯƠNG 3 (KỊCH BẢN TRIỂN KHAI 1 LAPTOP / 2 LAPTOP)
    # =========================================================================
    print("[*] Đang xây dựng Slide 12: Kịch bản triển khai Demo...")
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "CHƯƠNG 3 | DEMO THỰC CHIẾN", "HƯỚNG DẪN TRIỂN KHAI DEMO: 1 LAPTOP HOẶC 2 LAPTOP QUA LAN/WI-FI")
    add_footer(s12, 12)

    # Left: Chế độ 1 Laptop
    add_card(s12, Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55), "Chế độ 1: Trình diễn 1-Click trên 1 Laptop")
    pts_s12_left = [
        ("Khởi động tự động bằng 1 File", "Chạy file start_demo_3_ben.bat để tự động mở cả 3 tiến trình Python và mở 3 tab trình duyệt song song."),
        ("Tab 1 - Admin SOC Dashboard", "Địa chỉ: http://127.0.0.1:5000 (giám sát KPI, bật/tắt IPS Auto-Block, xem nhật ký thời gian thực)."),
        ("Tab 2 - Thiết bị IoT Nạn nhân", "Địa chỉ: http://127.0.0.1:8088 (gửi dữ liệu cảm biến hợp lệ, giám sát tải CPU/RAM thiết bị)."),
        ("Tab 3 - Red Team Attacker Console", "Địa chỉ: http://127.0.0.1:9090 (chọn kịch bản tấn công và phát động đòn đánh)."),
        ("Quy trình Demo 3 Bước", "Bước 1: Gửi traffic sạch (ALLOW) -> Bước 2: Tấn công khi tắt Auto-Block (báo đỏ) -> Bước 3: Bật Auto-Block (chặn đứng 403).")
    ]
    add_bullet_points(s12, Inches(0.8), Inches(1.85), Inches(5.5), Inches(3.9), pts_s12_left, font_size=Pt(10), space_after=Pt(6))

    # Right: Chế độ 2 Laptop qua LAN
    add_card(s12, Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55), "Chế độ 2: Thực chiến 2 Laptop qua Wi-Fi / Mạng LAN")
    pts_s12_right = [
        ("Laptop 1 (Blue Team & Victim - Minh)", "Chạy: python ai_nids_guardian_server.py --port 5000 và python victim_iot_server.py --http-port 8088 --telnet-port 2323."),
        ("Laptop 2 (Red Team Attacker - Công)", "Chạy: python attacker_botnet_console.py --guardian-url http://<IP_Laptop_1>:5000 --victim-ip <IP_Laptop_1>."),
        ("Hỗ trợ CLI Argparse hoàn chỉnh", "Các script hỗ trợ đầy đủ cờ lệnh --host, --port, --guardian-url, --victim-ip, linh hoạt tùy biến địa chỉ mạng."),
        ("Kết hợp công cụ Kali Linux thật", "Có thể dùng Nmap (quét cổng), Hydra (dò mật khẩu Telnet :2323), Hping3 (SYN Flood) để minh họa bề mặt tấn công ngoài."),
        ("Xuất báo cáo điều tra số", "Nút 'Xuất Báo Cáo CSV' trên SOC Dashboard cho phép tải log điều tra phục vụ đánh giá sau sự cố.")
    ]
    add_bullet_points(s12, Inches(7.0), Inches(1.85), Inches(5.5), Inches(3.9), pts_s12_right, font_size=Pt(10), space_after=Pt(6))

    add_takeaway_card(s12, "Hệ thống demo được thiết kế linh hoạt, vừa có thể chạy trình diễn nhanh gọn 1-click trên máy tính cá nhân, vừa sẵn sàng đấu nối thực chiến giữa 2 laptop qua mạng nội bộ có phân định vai trò rõ ràng giữa Red Team và Blue Team.")

    # =========================================================================
    # SLIDE 13: KẾT LUẬN (KẾT QUẢ ĐẠT ĐƯỢC, HẠN CHẾ & HƯỚNG TỚI)
    # =========================================================================
    print("[*] Đang xây dựng Slide 13: Kết luận & Hướng tới...")
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "KẾT LUẬN & KIẾN NGHỊ", "KẾT QUẢ ĐẠT ĐƯỢC, HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN TƯƠNG LAI")
    add_footer(s13, 13)

    # Left: Kết quả đạt được
    add_card(s13, Inches(0.6), Inches(1.35), Inches(5.9), Inches(4.55), "1. Kết quả nổi bật đạt được")
    pts_s13_left = [
        ("Khai phá 100% dữ liệu IoT-23", "Xử lý trọn vẹn 5.696.295 bản ghi bằng quy trình Stratified 80/20 chuẩn quốc tế, bảo đảm không rò rỉ dữ liệu."),
        ("Tối ưu hóa thành công LightGBM", "Đạt Accuracy 99,99%, F1-Score 99,99%, AUC 0,999981, FPR chỉ 0,12% trên hơn 1,14 triệu dòng test độc lập."),
        ("Thời gian xử lý siêu tốc", "Huấn luyện chỉ 19,83 giây; suy luận chỉ 0,0043 ms/luồng (batch), hoàn toàn đáp ứng yêu cầu giám sát thời gian thực."),
        ("Hệ sinh thái Demo 3 bên trực quan", "Hiện thực hóa trọn vẹn kiến trúc phòng thủ chủ động với giao diện SOC Dashboard hiện đại và IPS Auto-Block."),
        ("Bộ hồ sơ học thuật hoàn chỉnh", "Báo cáo Word chuẩn 16 hình vẽ 300 DPI, slide 16:9 đồng bộ, mã nguồn mở đẩy đủ trên GitHub.")
    ]
    add_bullet_points(s13, Inches(0.8), Inches(1.85), Inches(5.5), Inches(3.9), pts_s13_left, font_size=Pt(10), space_after=Pt(6))

    # Right: Hạn chế & Hướng phát triển
    add_card(s13, Inches(6.8), Inches(1.35), Inches(5.933), Inches(4.55), "2. Hạn chế & Hướng phát triển tiếp theo")
    pts_s13_right = [
        ("Hạn chế: Phân tích theo từng luồng đơn lẻ", "Chưa áp dụng cửa sổ trượt thời gian (Sliding Time Window) để nhận diện các đòn tấn công quét cực chậm (Low-and-Slow Scan)."),
        ("Hạn chế: Tầng giao tiếp giả lập qua API", "Hệ thống demo hiện tại sử dụng luồng JSON POST qua REST API; chưa có tầng bắt gói tin mạng thô thời gian thực."),
        ("Hướng 1: Tích hợp eBPF / XDP tại Linux Kernel", "Nhúng mô hình LightGBM trực tiếp vào tầng nhân Linux trên Router OpenWrt để lọc gói tin ở tốc độ đường truyền (Line-rate)."),
        ("Hướng 2: Nhận diện mã độc đa lớp (Multi-class)", "Phát triển mô hình phân loại sâu để chỉ điểm chính xác họ mã độc (Mirai vs Hajime vs Torii vs Gafgyt) thay vì nhị phân."),
        ("Hướng 3: Học liên kết bảo mật (Federated Learning)", "Cho phép các cổng IoT Gateway chia sẻ tri thức nhận diện botnet mà không cần gửi dữ liệu người dùng về máy chủ trung tâm.")
    ]
    add_bullet_points(s13, Inches(7.0), Inches(1.85), Inches(5.5), Inches(3.9), pts_s13_right, font_size=Pt(9.8), space_after=Pt(5))

    add_takeaway_card(s13, "Đề tài đã giải quyết trọn vẹn mục tiêu nghiên cứu học thuật và ứng dụng thực tiễn, cung cấp nền tảng vững chắc để phát triển thành giải pháp an ninh mạng thương mại hóa bảo vệ hệ thống thiết bị IoT.")

    # =========================================================================
    # SLIDE 14: THAM KHẢO & PHIÊN HỎI ĐÁP (Q&A)
    # =========================================================================
    print("[*] Đang xây dựng Slide 14: Tham khảo & Q&A...")
    s14 = prs.slides.add_slide(blank_layout)
    # Background Navy Dark for Slide 14
    bg14 = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg14.fill.solid()
    bg14.fill.fore_color.rgb = C_NAVY_DARK
    bg14.line.fill.background()

    # Top Banner
    tb14 = s14.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.8))
    tf14 = tb14.text_frame
    p14 = tf14.paragraphs[0]
    p14.alignment = PP_ALIGN.CENTER
    p14.text = "TÀI LIỆU THAM KHẢO CHÍNH THỐNG & PHIÊN THẢO LUẬN Q&A"
    p14.font.name = FONT_HEADING
    p14.font.size = Pt(20)
    p14.font.bold = True
    p14.font.color.rgb = C_WHITE

    p14_sub = tf14.add_paragraph()
    p14_sub.alignment = PP_ALIGN.CENTER
    p14_sub.text = "Trích lục từ 16 công trình nghiên cứu uy tín (IEEE, USENIX, ACM, NeurIPS) trong Báo cáo Đồ án"
    p14_sub.font.name = FONT_BODY
    p14_sub.font.size = Pt(10.5)
    p14_sub.font.color.rgb = C_ACCENT_CYAN

    # Left: Danh mục tài liệu tham khảo chính
    c14_left = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.35), Inches(6.8), Inches(4.55))
    c14_left.fill.solid()
    c14_left.fill.fore_color.rgb = C_NAVY_LIGHT
    set_shape_border(c14_left, C_ACCENT_BLUE, Pt(1))

    tb_refs = s14.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(6.4), Inches(4.2))
    tf_refs = tb_refs.text_frame
    tf_refs.word_wrap = True

    refs = [
        ("[1] S. Garcia et al. (2020)", "IoT-23: A labeled dataset with malicious and benign IoT network traffic. Stratosphere IPS Lab, Czech Technical University."),
        ("[2] M. Antonakakis et al. (2017)", "Understanding the Mirai Botnet. 26th USENIX Security Symposium, pp. 1093–1110."),
        ("[3] S. Edwards & I. Profetis (2016)", "Hajime: Analysis of a decentralized internet worm for IoT devices. Rapidity Networks Technical Report."),
        ("[4] J. Neduchal et al. (2018)", "Torii Botnet: Not Another Mirai Variant. Avast Threat Labs Whitepaper."),
        ("[5] G. Ke et al. (2017)", "LightGBM: A Highly Efficient Gradient Boosting Decision Tree. Advances in NeurIPS 30, pp. 3146–3154."),
        ("[6] A. Caruso et al. (2023)", "Investigation on Botnet Traffic in IoT Networks: A Machine Learning Approach. MDPI Sensors, 23(12), 5410.")
    ]

    for i, (tag, detail) in enumerate(refs):
        p = tf_refs.paragraphs[0] if i == 0 else tf_refs.add_paragraph()
        p.space_after = Pt(6)
        p.line_spacing = 1.1

        r1 = p.add_run()
        r1.text = tag + "\n"
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = C_ACCENT_CYAN

        r2 = p.add_run()
        r2.text = detail
        r2.font.name = FONT_BODY
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(226, 232, 240)

    # Right: Khối Cảm ơn & Q&A
    c14_right = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.8), Inches(1.35), Inches(4.733), Inches(4.55))
    c14_right.fill.solid()
    c14_right.fill.fore_color.rgb = RGBColor(15, 23, 42)
    set_shape_border(c14_right, C_ACCENT_BLUE, Pt(1.5))

    tb_qa = s14.shapes.add_textbox(Inches(8.0), Inches(1.6), Inches(4.333), Inches(4.0))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True

    p_tks = tf_qa.paragraphs[0]
    p_tks.alignment = PP_ALIGN.CENTER
    p_tks.text = "TRÂN TRỌNG CẢM ƠN\nTHẦY CÔ VÀ HỘI ĐỒNG!"
    p_tks.font.name = FONT_HEADING
    p_tks.font.size = Pt(17)
    p_tks.font.bold = True
    p_tks.font.color.rgb = C_WHITE

    p_div = tf_qa.add_paragraph()
    p_div.alignment = PP_ALIGN.CENTER
    p_div.text = "───────────────────────"
    p_div.font.size = Pt(10)
    p_div.font.color.rgb = C_ACCENT_BLUE

    p_qa = tf_qa.add_paragraph()
    p_qa.alignment = PP_ALIGN.CENTER
    p_qa.text = "PHIÊN HỎI ĐÁP (Q&A)\n& TRÌNH DIỄN DEMO HỆ THỐNG"
    p_qa.font.name = FONT_HEADING
    p_qa.font.size = Pt(13)
    p_qa.font.bold = True
    p_qa.font.color.rgb = C_ACCENT_CYAN

    p_info = tf_qa.add_paragraph()
    p_info.alignment = PP_ALIGN.LEFT
    p_info.space_before = Pt(12)
    p_info.text = "Nhóm thực hiện (Nhóm 4):\n• Nguyễn Công Minh (SĐT: 0825385889)\n• Ngô Văn Công (SĐT: 0775745371)\n\nCổng dịch vụ Live Demo:\n• Admin SOC: Port 5000\n• Victim IoT: Port 8088 / Telnet 2323\n• Red Team: Port 9090"
    p_info.font.name = FONT_BODY
    p_info.font.size = Pt(9.5)
    p_info.font.color.rgb = RGBColor(203, 213, 225)

    # Footer Slide 14
    f14 = s14.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.4))
    tf_f14 = f14.text_frame
    p_f14 = tf_f14.paragraphs[0]
    p_f14.alignment = PP_ALIGN.CENTER
    p_f14.text = "Nhóm 4: Nguyễn Công Minh & Ngô Văn Công | Học phần Kiểm thử Xâm nhập | Slide 14/14"
    p_f14.font.name = FONT_BODY
    p_f14.font.size = Pt(9.5)
    p_f14.font.color.rgb = RGBColor(148, 163, 184)

    # =========================================================================
    # LƯU FILE VÀ ĐỒNG BỘ
    # =========================================================================
    print(f"[*] Đang lưu presentation ra {OUTPUT_PPTX}...")
    prs.save(OUTPUT_PPTX)

    if os.path.exists(os.path.dirname(COPY_PPTX)):
        print(f"[*] Đồng bộ bản copy ra {COPY_PPTX}...")
        prs.save(COPY_PPTX)

    print("[+] Hoàn tất tạo Slide PowerPoint 16:9 Widescreen với 14 slide chuẩn mực!")

if __name__ == "__main__":
    build_presentation()
