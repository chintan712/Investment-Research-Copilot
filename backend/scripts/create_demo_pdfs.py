from pathlib import Path
import argparse

import fitz


DEMO_DOCUMENTS = {
    "Acme_Financial_Statements.pdf": [
        "ACME CORP | FICTIONAL DEMO DATA | Financial Statements",
        "2024 revenue was $100 million and 2025 revenue was $118.7 million. 2025 EBITDA was $26 million, net income was $15 million, and total debt was $84 million.",
        "Gross margin was 61.2% in 2025, compared with 63.0% in 2024. Management attributes the decrease to input-cost pressure and customer implementation work.",
    ],
    "Acme_Management_Presentation.pdf": [
        "ACME CORP | FICTIONAL DEMO DATA | Management Presentation",
        "Management expects continued growth from its enterprise analytics platform. The five largest customers represented 42% of 2025 revenue.",
        "The company plans to invest in product development and international sales. These investments may temporarily pressure operating margins.",
    ],
    "Acme_Risk_Report.pdf": [
        "ACME CORP | FICTIONAL DEMO DATA | Risk Report",
        "Principal risks identified by management are customer concentration, leverage, and margin pressure. The largest customer represented 16% of 2025 revenue.",
        "Total debt of $84 million and 2025 EBITDA of $26 million imply leverage of approximately 3.23x. A slowdown in customer renewals could reduce cash available for debt service.",
    ],
}


def create_pdf(path: Path, title: str, paragraphs: list[str]) -> None:
    document = fitz.open()
    for paragraph in paragraphs:
        page = document.new_page()
        page.insert_textbox(fitz.Rect(60, 60, 535, 130), paragraph, fontsize=18, fontname="helv", color=(0.1, 0.2, 0.18))
        page.insert_textbox(fitz.Rect(60, 170, 535, 760), paragraph, fontsize=12, fontname="helv", lineheight=1.5)
    document.save(path)
    document.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create fictional Acme Corp research PDFs")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "demo")
    output_dir = parser.parse_args().output_dir
    output_dir.mkdir(exist_ok=True)
    for filename, paragraphs in DEMO_DOCUMENTS.items():
        create_pdf(output_dir / filename, filename.removesuffix(".pdf"), paragraphs)
    print(f"Created {len(DEMO_DOCUMENTS)} fictional PDFs in {output_dir}")


if __name__ == "__main__":
    main()
