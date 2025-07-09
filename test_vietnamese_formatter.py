"""
Test Vietnamese text formatter
"""
from src.utils.vietnamese_text_formatter import format_vietnamese_text

def test_formatter():
    """Test Vietnamese text formatting"""
    
    # Test cases
    test_cases = [
        {
            "input": "truong dai hoc an ninh nhan dan",
            "expected": "Trường Đại học An ninh Nhân dân"
        },
        {
            "input": "phuong thuc tuyen sinh",
            "expected": "phương thức tuyển sinh"
        },
        {
            "input": "bo cong an",
            "expected": "Bộ Công an"
        },
        {
            "input": "dieu kien du tuyen",
            "expected": "điều kiện dự tuyển"
        },
        {
            "input": "chuong trinh dao tao",
            "expected": "chương trình đào tạo"
        },
        {
            "input": "ket qua thi tot nghiep",
            "expected": "kết quả thi tốt nghiệp"
        },
        {
            "input": "truong   dai   hoc   an   ninh   nhan   dan   co   3   phuong   thuc   tuyen   sinh",
            "expected": "Trường Đại học An ninh Nhân dân có 3 phương thức tuyển sinh"
        },
        {
            "input": "phuong thuc 1:tuyen thang theo quy che tuyen sinh",
            "expected": "phương thức 1: tuyển thẳng theo quy chế tuyển sinh"
        },
        {
            "input": "phuong thuc 2:xet tuyen ket hop chung chi ngoai ngu quoc te",
            "expected": "phương thức 2: xét tuyển kết hợp chứng chỉ ngoại ngữ quốc tế"
        }
    ]
    
    print("Testing Vietnamese Text Formatter:")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case["input"]
        expected = test_case["expected"]
        result = format_vietnamese_text(input_text)
        
        print(f"\nTest {i}:")
        print(f"Input:    '{input_text}'")
        print(f"Expected: '{expected}'")
        print(f"Result:   '{result}'")
        print(f"Status:   {'✓ PASS' if result.lower() == expected.lower() else '✗ FAIL'}")

def test_simple():
    """Simple test"""
    text = "phuong thuc tuyen sinh cua truong co nhung gi?"
    result = format_vietnamese_text(text)
    print(f"Input: {text}")
    print(f"Output: {result}")

if __name__ == "__main__":
    test_simple()
    print("\n" + "="*50 + "\n")
    test_formatter()
