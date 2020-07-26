
import re
import unittest

from typing import List, Tuple

from grascii import regen, grammar, similarities

class TestAnnotationRegex(unittest.TestCase):

    def check_strictness_low(self, annotations: List[str], texts: List[Tuple[str, str]]):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)
        for a in annotations:
            for t in texts:
                regex = builder.make_annotation_regex(t[0], a)
                self.assertRegex(t[0] + t[1], regex)

    def test_strictness_low_circle_vowel(self):
        annotations = [
            [],
            [","],
            ["~", ","]
        ]
        texts = [("A", ""), ("A", "~"), ("A", "|."), ("A", "~|,_"),
                 ("E", ""), ("E", "~"), ("E", "|."), ("E", "~|,_"),]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_hook_vowel(self):
        annotations_o = [
            [],
            [","],
            ["(", ","],
            ["(", "_"]
        ]
        texts_o = [("O", ""), ("O", "("), ("O", "(,"), ("O", "(._")]
        annotations_u = [
            [],
            [","],
            [")", ","],
            [")", "_"]
        ]
        texts_u = [("U", ""), ("U", ")"), ("U", "),"), ("U", ")._")]
        self.check_strictness_low(annotations_o, texts_o)
        self.check_strictness_low(annotations_u, texts_u)

    def test_strictness_low_circle_diphthong(self):
        annotations = [
            [],
            ["~"],
            ["~", "|"],
            ["_"],
        ]
        texts = [("I", ""), ("I", "~"), ("I", "_"), ("I~|_"),
                ("A&E", ""), ("A&E", "~"), ("A&E", "_"), ("A&E~|_"),    
                ("A'E", ""), ("A'E", "~"), ("A'E", "_"), ("A'E~|_")]
        self.check_strictness_low(annotations, texts)
                
    def test_strictness_low_hook_diphthong(self):
        annotations = [
            [],
            ["_"],
        ]
        texts = [("AU", ""), ("AU", "_"),
                 ("OE", ""), ("OE", "_"),
                 ("EU", ""), ("EU", "_")]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_directed_consonant(self):
        annotations = [
            [],
            ["("],
            [")"],
            [","],
            ["(,"]
        ]
        texts = [("S", ""), ("S", "("), ("S", "),"),
                ("Z", ""), ("Z", "("), ("Z", "),"),
                ("TH", ""), ("TH", "("), ("TH", "),")]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_oblique_consonant(self):
        annotations = [
            [],
            [","]
        ]
        texts = [("SH", ""), ("SH", ",")]
        self.check_strictness_low(annotations, texts)

    def check_strictness_medium(self, strokes, tests):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.MEDIUM)
        for stroke in strokes:
            for test in tests:
                annotations = test[0]
                for text, expected in test[1]:
                    regex = builder.make_annotation_regex(stroke, annotations)
                    with self.subTest(annotations=annotations, text=stroke+text):
                        if expected:
                            self.assertRegex(stroke + text, regex)
                        else:
                            self.assertNotRegex(stroke + text, regex)


    def test_strictness_medium_circle_vowel(self):
        circle_vowels = ["A", "E"]
        tests = [
            ([], [("", True), (",", True), ("~|._", True)]),
            ([","], [("", False), (".", False), (",", True), ("~|,_", True)]),
            (["~"], [("", False), ("~", True), (".", False), ("~|._", True)]),
            (["~", "|", ".", "_"], [("~", False), ("|", False), (".", False),
                ("_", False), ("~|._", True)]),
        ]
        self.check_strictness_medium(circle_vowels, tests)

    def test_strictness_medium_hook_vowel(self):
        tests1 = [
            ([], [("", True), (",", True), ("(,_", True)]),
            ([","], [("", False), (".", False), (",", True), ("(,_", True)]),
            (["("], [("", False), (".", False), ("(,_", True)]),
            (["(", ".", "_"], [(".", False), ("_", False), ("(._", True)]),
        ]
        tests2 = [
            ([], [("", True), (",", True), ("),_", True)]),
            ([","], [("", False), (".", False), (",", True), ("),_", True)]),
            ([")"], [("", False), (".", False), ("),_", True)]),
            ([")", ".", "_"], [(".", False), ("_", False), (")._", True)]),
        ]
        self.check_strictness_medium(["O"], tests1)
        self.check_strictness_medium(["U"], tests2)

    def test_strictness_medium_circle_diphthong(self):
        strokes = ["I", "A&E", "A&'"]
        tests = [
            ([], [("", True), ("~", True), ("|", True), ("_", True), ("~|_", True)]),
            (["~"], [("", False), ("~", True), ("|", False), ("_", False), ("~|_", True)]),
            (["|"], [("", False), ("~", False), ("|", True), ("_", False), ("~|_", True)]),
            (["_"], [("", False), ("~", False), ("|", False), ("_", True), ("~|_", True)]),
            (["~", "|", "_"], [("", False), ("~", False), ("|", False), ("_", False), ("~|_", True)]),
        ]
        self.check_strictness_medium(strokes, tests)

    def test_strictness_medium_hook_diphthong(self):
        strokes = ["AU", "OE", "EU"]
        tests = [
            ([], [("", True), ("_", True)]),
            (["_"], [("", False), ("_", True)]),
        ]
        self.check_strictness_medium(strokes, tests)

    def test_strictness_medium_directed_consonant(self):
        strokes = ["S", "Z", "TH"]
        tests = [
            ([], [("", True), ("(", True), (")", True), (",", True), ("(,", True), ("),", True)]),
            (["("], [("", False), ("(", True), (")", False), (",", False), ("(,", True), ("),", False)]),
            ([")"], [("", False), ("(", False), (")", True), (",", False), ("(,", False), ("),", True)]),
            (["(", ","], [("", False), ("(", False), (")", False), (",", False), ("(,", True), ("),", False)]),
            ([")", ","], [("", False), ("(", False), (")", False), (",", False), ("(,", False), ("),", True)])
        ]
        self.check_strictness_medium(strokes, tests)

    def test_strictness_medium_oblique_consonant(self):
        tests = [
            ([], [("", True), (",", True)]),
            ([","], [("", False), (",", True)]),
        ]
        self.check_strictness_medium(["SH"], tests)

    def check_strictness_high(self, strokes, tests):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.HIGH)
        for stroke in strokes:
            for test in tests:
                annotations = test[0]
                for text, expected in test[1]:
                    regex = builder.make_annotation_regex(stroke, annotations)
                    with self.subTest(annotations=annotations, text=stroke+text):
                        if expected:
                            self.assertTrue(re.fullmatch(regex, stroke + text))
                        else:
                            self.assertFalse(re.fullmatch(regex, stroke + text))


    def test_strictness_high_circle_vowel(self):
        circle_vowels = ["A", "E"]
        tests = [
            ([], [("", True), (",", False), ("~|._", False)]),
            ([","], [("", False), (".", False), (",", True), ("~|,_", False)]),
            (["~"], [("", False), ("~", True), (".", False), ("~|._", False)]),
            (["~", "|", ".", "_"], [("~", False), ("|", False), (".", False),
                ("_", False), ("~|._", True)]),
        ]
        self.check_strictness_high(circle_vowels, tests)

    def test_strictness_high_hook_vowel(self):
        tests1 = [
            ([], [("", True), (",", False), ("(,_", False)]),
            ([","], [("", False), (".", False), (",", True), ("(,_", False)]),
            (["("], [("", False), (".", False), ("(,_", False)]),
            (["(", ".", "_"], [(".", False), ("_", False), ("(._", True)]),
        ]
        tests2 = [
            ([], [("", True), (",", False), ("),_", False)]),
            ([","], [("", False), (".", False), (",", True), ("),_", False)]),
            ([")"], [("", False), (".", False), ("),_", False)]),
            ([")", ".", "_"], [(".", False), ("_", False), (")._", True)]),
        ]
        self.check_strictness_high(["O"], tests1)
        self.check_strictness_high(["U"], tests2)

    def test_strictness_high_circle_diphthong(self):
        strokes = ["I", "A&E", "A&'"]
        tests = [
            ([], [("", True), ("~", False), ("|", False), ("_", False), ("~|_", False)]),
            (["~"], [("", False), ("~", True), ("|", False), ("_", False), ("~|_", False)]),
            (["|"], [("", False), ("~", False), ("|", True), ("_", False), ("~|_", False)]),
            (["_"], [("", False), ("~", False), ("|", False), ("_", True), ("~|_", False)]),
            (["~", "|", "_"], [("", False), ("~", False), ("|", False), ("_", False), ("~|_", True)]),
        ]
        self.check_strictness_high(strokes, tests)

    def test_strictness_high_hook_diphthong(self):
        strokes = ["AU", "OE", "EU"]
        tests = [
            ([], [("", True), ("_", False)]),
            (["_"], [("", False), ("_", True)]),
        ]
        self.check_strictness_high(strokes, tests)

    def test_strictness_high_directed_consonant(self):
        strokes = ["S", "Z", "TH"]
        tests = [
            ([], [("", True), ("(", False), (")", False), (",", False), ("(,", False), ("),", False)]),
            (["("], [("", False), ("(", True), (")", False), (",", False), ("(,", False), ("),", False)]),
            ([")"], [("", False), ("(", False), (")", True), (",", False), ("(,", False), ("),", False)]),
            (["(", ","], [("", False), ("(", False), (")", False), (",", False), ("(,", True), ("),", False)]),
            ([")", ","], [("", False), ("(", False), (")", False), (",", False), ("(,", False), ("),", True)])
        ]
        self.check_strictness_high(strokes, tests)

    def test_strictness_high_oblique_consonant(self):
        tests = [
            ([], [("", True), (",", False)]),
            ([","], [("", False), (",", True)]),
        ]
        self.check_strictness_high(["SH"], tests)

    def test_out_of_order_annotations(self):
        pass

    def test_invalid_annotations(self):
        pass

    def test_mutually_exclusive_annotations(self):
        pass



class TestDisjoiners(unittest.TestCase):

    def run_tests(self, builder, tests):
        for test in tests:
            interp = test[0]
            for text, expected in test[1]:
                regex = builder.build_regex(interp)
                with self.subTest(interpretation=interp, text=text):
                    if expected:
                        self.assertRegex(text, regex)
                    else:
                        self.assertNotRegex(text, regex)

    def test_strictness_low(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.LOW)
        tests = [
            (["A", "B"], [("AB", True), ("A^B", True)]),
            (["A", "^", "B"], [("AB", True), ("A^B", True)]),
            (["A", "B", "D"], [("ABD", True), ("A^BD", True), ("AB^D", True), ("A^B^D", True)]),
            (["A", "^", "B", "D"], [("ABD", True), ("A^BD", True), ("AB^D", True), ("A^B^D", True)]),
            (["A", "B", "^", "D"], [("ABD", True), ("A^BD", True), ("AB^D", True), ("A^B^D", True)]),
            (["A", "^", "B", "^", "D"], [("ABD", True), ("A^BD", True), ("AB^D", True), ("A^B^D", True)])
        ]
        self.run_tests(builder, tests)

    def test_strictness_medium(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.MEDIUM)
        tests = [
            (["A", "B"], [("AB", True), ("A^B", True)]),
            (["A", "^", "B"], [("AB", False), ("A^B", True)]),
            (["A", "B", "D"], [("ABD", True), ("A^BD", True), ("AB^D", True), ("A^B^D", True)]),
            (["A", "^", "B", "D"], [("ABD", False), ("A^BD", True), ("AB^D", False), ("A^B^D", True)]),
            (["A", "B", "^", "D"], [("ABD", False), ("A^BD", False), ("AB^D", True), ("A^B^D", True)]),
            (["A", "^", "B", "^", "D"], [("ABD", False), ("A^BD", False), ("AB^D", False), ("A^B^D", True)])
        ]
        self.run_tests(builder, tests)

    def test_strictness_high(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.HIGH)
        tests = [
            (["A", "B"], [("AB", True), ("A^B", False)]),
            (["A", "^", "B"], [("AB", False), ("A^B", True)]),
            (["A", "B", "D"], [("ABD", True), ("A^BD", False), ("AB^D", False), ("A^B^D", False)]),
            (["A", "^", "B", "D"], [("ABD", False), ("A^BD", True), ("AB^D", False), ("A^B^D", False)]),
            (["A", "B", "^", "D"], [("ABD", False), ("A^BD", False), ("AB^D", True), ("A^B^D", False)]),
            (["A", "^", "B", "^", "D"], [("ABD", False), ("A^BD", False), ("AB^D", False), ("A^B^D", True)])
        ]
        self.run_tests(builder, tests)

    def test_prefixes(self):
        pass

class TestAspirates(unittest.TestCase):

    def run_tests(self, builder, tests):
        for test in tests:
            interp = test[0]
            for text, expected in test[1]:
                regex = builder.build_regex(interp)
                with self.subTest(interpretation=interp, text=text):
                    if expected:
                        self.assertRegex(text, regex)
                    else:
                        self.assertNotRegex(text, regex)

    def test_strictness_low(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.LOW)
        tests = [
            (["A"], [("A", True), ("'A", True)]),
            (["'", "A"], [("A", True), ("'A", True)]),
            (["A", "D", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["'", "A", "D", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["'", "A", "'", "D", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["'", "A", "'", "D", "'", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["A", "'", "D", "'", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["'", "A", "D", "'", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["A", "'", "D", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["A", "D", "'", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
        ]
        self.run_tests(builder, tests)

    def test_strictness_medium(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.MEDIUM)
        tests = [
            (["A"], [("A", True), ("'A", True)]),
            (["'", "A"], [("A", False), ("'A", True)]),
            (["A", "D", "E"], [("ADE", True), ("'ADE", True), ("A'DE", True), ("AD'E", True), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
            (["'", "A", "D", "E"], [("ADE", False), ("'ADE", True), ("A'DE", False), ("AD'E", False), ("'A'DE", True),
                ("'AD'E", True), ("A'D'E", False), ("'A'D'E", True)]),
            (["'", "A", "'", "D", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", True),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", True)]),
            (["'", "A", "'", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", True)]),
            (["A", "'", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", True), ("'A'D'E", True)]),
            (["'", "A", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", True), ("A'D'E", False), ("'A'D'E", True)]),
            (["A", "'", "D", "E"], [("ADE", False), ("'ADE", False), ("A'DE", True), ("AD'E", False), ("'A'DE", True),
                ("'AD'E", False), ("A'D'E", True), ("'A'D'E", True)]),
            (["A", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", True), ("'A'DE", False),
                ("'AD'E", True), ("A'D'E", True), ("'A'D'E", True)]),
        ]
        self.run_tests(builder, tests)

    def test_strictness_high(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.HIGH)
        tests = [
            (["A"], [("A", True), ("'A", False)]),
            (["'", "A"], [("A", False), ("'A", True)]),
            (["A", "D", "E"], [("ADE", True), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", False)]),
            (["'", "A", "D", "E"], [("ADE", False), ("'ADE", True), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", False)]),
            (["'", "A", "'", "D", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", True),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", False)]),
            (["'", "A", "'", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", True)]),
            (["A", "'", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", True), ("'A'D'E", False)]),
            (["'", "A", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", True), ("A'D'E", False), ("'A'D'E", False)]),
            (["A", "'", "D", "E"], [("ADE", False), ("'ADE", False), ("A'DE", True), ("AD'E", False), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", False)]),
            (["A", "D", "'", "E"], [("ADE", False), ("'ADE", False), ("A'DE", False), ("AD'E", True), ("'A'DE", False),
                ("'AD'E", False), ("A'D'E", False), ("'A'D'E", False)]),
        ]
        self.run_tests(builder, tests)

    def test_double_aspirate(self):
        pass
        
class TestUncertaintyRegex(unittest.TestCase):
    
    def test_uncertainty_zero(self):
        # this should go under sim tests
        for stroke in grammar.STROKES:
            similars = similarities.get_similar(stroke, 0)
            self.assertEqual(len(similars), 1)
            self.assertIn(stroke, list(similars)[0])




class TestSearchMode(unittest.TestCase):

    def run_tests(self, builder, tests):
        for test in tests:
            interp = test[0]
            for text, expected in test[1]:
                regex = builder.build_regex(interp)
                with self.subTest(interpretation=interp, text=text):
                    if expected:
                        self.assertRegex(text, regex)
                    else:
                        self.assertNotRegex(text, regex)
    
    def test_match(self):
        builder = regen.RegexBuilder(search_mode=regen.SearchMode.MATCH)
        tests = [
            (["A", "B"], [("AB", True), ("ABU", False), ("DAB", False)])
        ]
        self.run_tests(builder, tests)

    def test_start(self):
        builder = regen.RegexBuilder(search_mode=regen.SearchMode.START)
        tests = [
            (["A", "B"], [("AB", True), ("ABU", True), ("DAB", False)])
        ]
        self.run_tests(builder, tests)

    def test_contains(self):
        builder = regen.RegexBuilder(search_mode=regen.SearchMode.CONTAIN)
        tests = [
            (["A", "B"], [("AB", True), ("ABU", True), ("DAB", True)])
        ]
        self.run_tests(builder, tests)

class TestFixFirst(unittest.TestCase):

    def run_tests(self, builder, tests):
        for test in tests:
            interp = test[0]
            for text, expected in test[1]:
                regex = builder.build_regex(interp)
                with self.subTest(interpretation=interp, text=text):
                    if expected:
                        self.assertRegex(text, regex)
                    else:
                        self.assertNotRegex(text, regex)

    def test_fix_first_off(self):
        builder = regen.RegexBuilder(fix_first=False, uncertainty=1)
        tests = [
            (["A", "B", "D"], [("ABD", True), ("EBD", True), ("IBD", True),
                               ("APT", True), ("EPDD", True), ("IBDT", True)])
        ]
        self.run_tests(builder, tests)

    def test_fix_first_on(self):
        builder = regen.RegexBuilder(fix_first=True, uncertainty=1)
        tests = [
            (["A", "B", "D"], [("ABD", True), ("EBD", False), ("IBD", False),
                               ("APT", True), ("EPDD", False), ("IBDT", False)])
        ]
        self.run_tests(builder, tests)

class TestStartingLetters(unittest.TestCase):
    pass


class TestRegexBuilder(unittest.TestCase):
    pass


         

    

if __name__ == "__main__":
    unittest.main()