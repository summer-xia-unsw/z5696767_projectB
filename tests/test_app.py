"""Smoke tests for the Streamlit app.

The app should load precomputed results and render the full investor journey
without recomputing models at runtime.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def navigation_radio(at: AppTest):
    for radio in at.radio:
        if radio.label == "Navigation":
            return radio
    raise AssertionError("Navigation radio was not rendered")


def test_streamlit_app_renders():
    at = AppTest.from_file("streamlit_app.py", default_timeout=30)
    at.run()

    assert len(at.exception) == 0
    page_text = " ".join(markdown.value for markdown in at.markdown)
    assert "TODO" not in page_text
    assert "NovaAlloc" in page_text

    radio_labels = [radio.label for radio in at.radio]
    assert "Navigation" in radio_labels


def test_streamlit_app_navigation_pages_render():
    pages = ["Funds", "Allocation", "Sentiment", "Fusion", "Data Health"]
    at = AppTest.from_file("streamlit_app.py", default_timeout=30)
    at.run()

    for page in pages:
        navigation_radio(at).set_value(page)
        at.run()
        assert len(at.exception) == 0, f"{page} page raised a Streamlit exception"

    assert "Report Figures" not in navigation_radio(at).options


def test_redesigned_report_figure_exports_exist():
    root = Path(__file__).resolve().parents[1]
    png_dir = root / "results" / "figures" / "Redesign" / "png"
    pdf_dir = root / "results" / "figures" / "Redesign" / "pdf"

    png_files = sorted(png_dir.glob("*.png"))
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    assert len(png_files) == 13
    assert len(pdf_files) == 13
    for png_path in png_files:
        assert (pdf_dir / f"{png_path.stem}.pdf").exists()
