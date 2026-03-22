from src.utils.fixed_admission_faq import get_fixed_admission_faq


RECTOR_NAME = "Tr\u1ea7n V\u0103n Tu\u1ea5n"
RECTOR_TITLE = "Hi\u1ec7u tr\u01b0\u1edfng"
RECTOR_NOTE = "B\u00ed th\u01b0 \u0110\u1ea3ng \u1ee7y"
ORG_SOURCE = "C\u01a1 c\u1ea5u t\u1ed5 ch\u1ee9c b\u1ed9 m\u00e1y Nh\u00e0 tr\u01b0\u1eddng"
QUOTA_INTRO = (
    "Th\u00f4ng tin d\u01b0\u1edbi \u0111\u00e2y t\u00f3m l\u01b0\u1ee3c ch\u1ec9 ti\u00eau "
    "tuy\u1ec3n sinh n\u0103m 2026"
)
EXAM_CODE_INTRO = (
    "B\u00e0i thi \u0111\u00e1nh gi\u00e1 c\u1ee7a B\u1ed9 C\u00f4ng an n\u0103m 2026 "
    "g\u1ed3m 4 m\u00e3 b\u00e0i thi"
)
EXAM_STRUCTURE_INTRO = (
    "N\u1ebfu b\u1ea1n mu\u1ed1n h\u00ecnh dung nhanh \u0111\u1ec1 thi n\u0103m 2026"
)
METHODS_INTRO = (
    "kh\u1ed1i tr\u01b0\u1eddng C\u00f4ng an nh\u00e2n d\u00e2n \u00e1p d\u1ee5ng 3 "
    "ph\u01b0\u01a1ng th\u1ee9c tuy\u1ec3n sinh ch\u00ednh"
)
OVERVIEW_SOURCE = "Thong tin nhan dien chinh thuc cua Truong Dai hoc An ninh Nhan dan"


def test_quota_question_returns_fixed_answer_with_intro_and_follow_ups():
    faq = get_fixed_admission_faq(
        "Chi tieu tuyen sinh vao Truong Dai hoc An Ninh Nhan Dan?"
    )

    assert faq is not None
    assert QUOTA_INTRO in faq["answer"]
    assert "220" in faq["answer"]
    assert "A00, A01, C03, D01, X02, X03, X04" in faq["answer"]
    assert "CA1, CA2, CA3, CA4" in faq["answer"]
    assert "| Tr" in faq["answer"]
    assert "PT2, PT3 Nam" in faq["answer"]
    assert "PT2, PT3 N" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3


def test_school_overview_query_returns_t04_and_ans_without_t01_confusion():
    faq = get_fixed_admission_faq("Thong tin ve Truong Dai hoc An ninh Nhan dan")

    assert faq is not None
    assert "T04" in faq["answer"]
    assert "ANS" in faq["answer"]
    assert "T01 / ANH" in faq["answer"]
    assert OVERVIEW_SOURCE in faq["sources"]


def test_school_code_query_returns_fixed_overview_answer():
    faq = get_fixed_admission_faq("Ma truong Truong Dai hoc An ninh Nhan dan la gi?")

    assert faq is not None
    assert "M\u00e3 tr\u01b0\u1eddng tuy\u1ec3n sinh" in faq["answer"]
    assert "**T04**" in faq["answer"]
    assert "ANH" in faq["answer"]


def test_school_overview_intro_query_matches_without_false_hieu_truong_collision():
    faq = get_fixed_admission_faq("gioi thieu truong dai hoc an ninh nhan dan")

    assert faq is not None
    assert "T04" in faq["answer"]


def test_rector_question_returns_fixed_leadership_answer():
    faq = get_fixed_admission_faq("Ai la hieu truong?")

    assert faq is not None
    assert RECTOR_NAME in faq["answer"]
    assert RECTOR_TITLE in faq["answer"]
    assert RECTOR_NOTE in faq["answer"]
    assert "Phan Xuan Tuy" not in faq["answer"]
    assert ORG_SOURCE in faq["sources"]


def test_bare_rector_keyword_returns_fixed_leadership_answer():
    faq = get_fixed_admission_faq("hieu truong")

    assert faq is not None
    assert RECTOR_NAME in faq["answer"]


def test_rector_title_with_school_name_returns_fixed_leadership_answer():
    faq = get_fixed_admission_faq("Hieu truong Truong Dai hoc An ninh Nhan dan")

    assert faq is not None
    assert RECTOR_NAME in faq["answer"]


def test_rector_duty_question_does_not_match_identity_fixed_answer():
    faq = get_fixed_admission_faq("Quyen han cua hieu truong la gi?")

    assert faq is None


def test_vice_rector_question_returns_all_fixed_vice_rectors():
    faq = get_fixed_admission_faq("Cac pho hieu truong cua nha truong la ai?")

    assert faq is not None
    assert "Nguy" in faq["answer"]
    assert "Ph" in faq["answer"]
    assert "\u0110\u1eb7ng Ng\u1ecdc To\u00e0n" in faq["answer"]
    assert "L\u00ea Ho\u00e0ng Ng\u00e2n" in faq["answer"]
    assert "Ph\u00f3 Hi\u1ec7u tr\u01b0\u1edfng" in faq["answer"]


def test_leadership_query_returns_fixed_board_list():
    faq = get_fixed_admission_faq("Ban giam hieu gom nhung ai?")

    assert faq is not None
    assert RECTOR_NAME in faq["answer"]
    assert "Nguy" in faq["answer"]
    assert "L\u00ea Ho\u00e0ng Ng\u00e2n" in faq["answer"]
    assert "Ban Gi\u00e1m hi\u1ec7u" in faq["answer"]
    assert ORG_SOURCE in faq["sources"]


def test_other_school_leadership_query_does_not_match_t04_fixed_answer():
    faq = get_fixed_admission_faq("Hieu truong Hoc vien An ninh nhan dan la ai?")

    assert faq is None


def test_quota_question_answer_does_not_leak_internal_prompt_language():
    faq = get_fixed_admission_faq(
        "Chi tieu tuyen sinh vao Truong Dai hoc An Ninh Nhan Dan?"
    )

    assert faq is not None
    assert "ban cung cap" not in faq["answer"]
    assert "bang anh cung cap" not in faq["answer"]
    assert "FAQ cung" not in faq["answer"]
    assert "he thong phai" not in faq["answer"]
    assert "ban tra loi cu" not in faq["answer"]


def test_generic_quota_and_combination_query_defaults_to_t04_fixed_answer():
    faq = get_fixed_admission_faq("thong tin ve chi tieu va to hop xet tuyen")

    assert faq is not None
    assert "220" in faq["answer"]
    assert "T04" in faq["answer"]
    assert "A00, A01, C03, D01, X02, X03, X04" in faq["answer"]


def test_exam_code_question_returns_code_table_and_follow_ups():
    faq = get_fixed_admission_faq("Ky hieu ma bai thi danh gia cua Bo Cong an?")

    assert faq is not None
    assert EXAM_CODE_INTRO in faq["answer"]
    assert "CA1" in faq["answer"]
    assert "CA4" in faq["answer"]
    assert "| M" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3


def test_exam_structure_question_returns_markdown_table():
    faq = get_fixed_admission_faq(
        "Cau truc de thi tuyen sinh dai hoc chinh quy tuyen moi?"
    )

    assert faq is not None
    assert EXAM_STRUCTURE_INTRO in faq["answer"]
    assert "180 ph" in faq["answer"]
    assert "| Ph" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3


def test_admission_method_question_returns_three_methods():
    faq = get_fixed_admission_faq("Cac phuong thuc tuyen sinh?")

    assert faq is not None
    assert METHODS_INTRO in faq["answer"]
    assert "Ph\u01b0\u01a1ng th\u1ee9c 1" in faq["answer"]
    assert "Ph\u01b0\u01a1ng th\u1ee9c 2" in faq["answer"]
    assert "Ph\u01b0\u01a1ng th\u1ee9c 3" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3
