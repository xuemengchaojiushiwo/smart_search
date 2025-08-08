import unittest

from python_service.pdf_layout_to_markdown import (
    normalize_text,
    _looks_like_char_grid,
    _char_grid_to_paragraph,
)


class TestPdfLayoutUtils(unittest.TestCase):
    def test_normalize_text_basic(self):
        raw = "  二零二五年二月 — 安联美元高收益基金, AUSHYAM LX!  "
        norm = normalize_text(raw)
        # 去空白/标点/大小写统一
        self.assertNotIn(" ", norm)
        self.assertNotIn("—", norm)
        self.assertIn("安联美元高收益基金", norm)
        self.assertIn("aushyamlx", norm)

    def test_char_grid_detection(self):
        # 构造一个典型的“字符网格”表格：列较多且大部分单元格为单字符
        table = [
            list("理财非存款产品有风险"),
            list("投资须谨慎理财计划"),
            list("属于非保本浮动收益"),
            list("不保证本金和收益"),
        ]
        self.assertTrue(_looks_like_char_grid(table))

        # 列较少时不应判定为字符网格
        not_grid = [
            ["证券", "行业", "地区", "%"],
            ["A", "B", "美国", "2.2"],
        ]
        self.assertFalse(_looks_like_char_grid(not_grid))

    def test_char_grid_to_paragraph(self):
        table = [
            list("安联 美元 高 收益 基金"),
            list("AM 类 美 元 收 息 股份"),
        ]
        para = _char_grid_to_paragraph(table)
        self.assertIsInstance(para, str)
        self.assertIn("安联美元高收益基金", para)


if __name__ == "__main__":
    unittest.main()


