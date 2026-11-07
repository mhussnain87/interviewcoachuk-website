#!/usr/bin/env python3
"""Checks that a new post built by generate_post.py gets its own tracking tags.

Run from the repo root:  python3 -m unittest tools/test_generate_post.py
No API call is made; the page is built from the template with sample content.
"""
import datetime, os, re, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_post as gp


class NewPostTags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tpl = open(gp.TEMPLATE, encoding="utf-8").read()
        cls.page = gp.build_page(tpl, "pharmacist interview questions",
                                 "pharmacist-interview-questions-uk", "pharmacist",
                                 gp.SAMPLE_DATA, datetime.date(2026, 11, 7))
        cls.tags = gp.tracking_tags(cls.page)

    def test_every_ct_uses_own_code(self):
        cts = [v for k, v in self.tags if k == "ct"]
        self.assertEqual(cts, ["pharmacist-nav", "pharmacist-top", "pharmacist-end", "pharmacist-side"])

    def test_every_utm_medium_uses_own_code(self):
        meds = {v for k, v in self.tags if k == "utm_medium"}
        self.assertEqual(meds, {"pharmacist"})

    def test_play_campaigns_are_placements(self):
        camps = [v for k, v in self.tags if k == "utm_campaign"]
        # each Play link carries the campaign twice (top-level and in referrer=)
        self.assertEqual(camps, ["top", "top", "end", "end", "side", "side"])

    def test_no_template_tags_or_question_lines(self):
        body = self.page.split("</style>")[-1]
        self.assertNotIn("icuk-q-cta", body)
        self.assertIsNone(re.search(r"ct=b7-|utm_medium(=|%3D)b7\b", self.page))

    def test_default_code_from_slug(self):
        self.assertEqual(gp.default_code("pharmacist-interview-questions-uk"), "pharmacist")
        self.assertEqual(gp.default_code("why-do-you-want-to-work-here-interview-answer"),
                         "why-do-you-want-to-work-here")

    def test_existing_codes_are_found(self):
        codes = gp.existing_codes()
        self.assertEqual(codes.get("b7"), "nhs-band-7-interview-questions")
        self.assertEqual(codes.get("midwife"), "midwife-interview-questions-uk")


if __name__ == "__main__":
    unittest.main()
