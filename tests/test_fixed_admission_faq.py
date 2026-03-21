from src.utils.fixed_admission_faq import get_fixed_admission_faq


def test_quota_question_returns_fixed_answer_with_intro_and_follow_ups():
    faq = get_fixed_admission_faq(
        "Chỉ tiêu tuyển sinh vào Trường Đại học An Ninh Nhân Dân?"
    )

    assert faq is not None
    assert "Theo đúng bảng chỉ tiêu bạn cung cấp" in faq["answer"]
    assert "220" in faq["answer"]
    assert "A00, A01, C03, D01, X02, X03, X04" in faq["answer"]
    assert "CA1, CA2, CA3, CA4" in faq["answer"]
    assert "| Trường/nhóm ngành |" in faq["answer"]
    assert "PT2, PT3 Nam" in faq["answer"]
    assert "PT2, PT3 Nữ" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3
    assert (
        "Điều kiện sơ tuyển vào Trường Đại học An Ninh Nhân Dân là gì?"
        in faq["follow_up_questions"]
    )


def test_generic_quota_and_combination_query_defaults_to_t04_fixed_answer():
    faq = get_fixed_admission_faq("thong tin ve chi tieu va to hop xet tuyen")

    assert faq is not None
    assert "220" in faq["answer"]
    assert "T04" in faq["answer"]
    assert "A00, A01, C03, D01, X02, X03, X04" in faq["answer"]


def test_exam_code_question_returns_code_table_and_follow_ups():
    faq = get_fixed_admission_faq("Ký hiệu mã bài thi đánh giá của Bộ Công an?")

    assert faq is not None
    assert "Bài thi đánh giá của Bộ Công an năm 2026 gồm 4 mã bài thi" in faq["answer"]
    assert "CA1" in faq["answer"]
    assert "CA4" in faq["answer"]
    assert "| Mã bài thi |" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3


def test_exam_structure_question_returns_markdown_table():
    faq = get_fixed_admission_faq(
        "Cấu trúc đề thi tuyển sinh đại học chính quy tuyển mới?"
    )

    assert faq is not None
    assert "Nếu bạn muốn hình dung nhanh đề thi năm 2026" in faq["answer"]
    assert "180 phút" in faq["answer"]
    assert "| Phần thi | Nội dung |" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3


def test_admission_method_question_returns_three_methods():
    faq = get_fixed_admission_faq("Các phương thức tuyển sinh?")

    assert faq is not None
    assert "khối trường Công an nhân dân áp dụng 3 phương thức tuyển sinh chính" in faq[
        "answer"
    ]
    assert "Phương thức 1" in faq["answer"]
    assert "Phương thức 2" in faq["answer"]
    assert "Phương thức 3" in faq["answer"]
    assert len(faq["follow_up_questions"]) == 3
