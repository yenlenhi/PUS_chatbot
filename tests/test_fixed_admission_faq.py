from src.utils.fixed_admission_faq import get_fixed_admission_faq


def test_quota_question_returns_fixed_answer():
    faq = get_fixed_admission_faq(
        "Chỉ tiêu tuyển sinh vào Trường Đại học An Ninh Nhân Dân?"
    )

    assert faq is not None
    assert "100" in faq["answer"]
    assert "| Trường/nhóm ngành |" in faq["answer"]


def test_exam_code_question_returns_code_table():
    faq = get_fixed_admission_faq("Ký hiệu mã bài thi đánh giá của Bộ Công an?")

    assert faq is not None
    assert "CA1" in faq["answer"]
    assert "CA4" in faq["answer"]
    assert "| Mã bài thi |" in faq["answer"]


def test_exam_structure_question_returns_markdown_table():
    faq = get_fixed_admission_faq(
        "Câu trúc đề thi tuyển sinh đại học chính quy tuyển mới?"
    )

    assert faq is not None
    assert "180 phút" in faq["answer"]
    assert "| Phần thi | Nội dung |" in faq["answer"]


def test_admission_method_question_returns_three_methods():
    faq = get_fixed_admission_faq("Các phương thức tuyển sinh?")

    assert faq is not None
    assert "Phương thức 1" in faq["answer"]
    assert "Phương thức 2" in faq["answer"]
    assert "Phương thức 3" in faq["answer"]
