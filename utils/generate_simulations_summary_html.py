#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a summary page for all simulation results."""

import os
import re
import datetime
import utils.common as common
from utils.custom_db import MyLottoDB
from utils import generate_freq_sim_html as freq_module
from utils import generate_least_freq_sim_html as lfreq_module
import inspect


def _strip_labels(section: str) -> str:
    """Remove FREQ/LFREQ labels from a summary snippet."""
    return re.sub(r"<h3>\s*(?:L?FREQ-[^<]*)</h3>", "", section)


def _extract_heading(html: str) -> str:
    match = re.search(r"<h1>(.*?)</h1>", html)
    return match.group(1) if match else ""


def main() -> str:
    docs_dir = os.path.join(common.root, "docs")

    db = MyLottoDB()
    start_date = datetime.date(2025, 1, 25)
    rows = db.get_history_since(start_date)

    def build_sections(generator) -> list[str]:
        sections = []
        accepts_return = 'return_data' in inspect.signature(generator).parameters
        for years in [1, 2, 3, 4, 5, None]:
            if accepts_return:
                path, summary, dist = generator(db, rows, years, return_data=True)
            else:
                path = generator(db, rows, years)
                summary = dist = ''
            with open(path, "r") as f:
                html = f.read()
            heading = _extract_heading(html)
            match = re.match(r"(.*) \(([^)]+)\)", heading)
            if match:
                heading = f"({match.group(2)}){match.group(1).strip()}"
            content = _strip_labels(summary)
            if dist:
                content += "\n<h3>Matched Count Distribution</h3>\n" + _strip_labels(dist)
            sections.append(
                f"<section>\n        <h2>{heading}</h2>\n        {content}\n    </section>"
            )
        return sections

    # Use the 2 year frequency simulation to obtain common styles
    with open(os.path.join(docs_dir, "freq_simulation.html"), "r") as f:
        style_html = f.read()
    style_match = re.search(r"<style>(.*?)</style>", style_html, re.S)
    style = style_match.group(1) if style_match else ""
    style += (
        "\n.summary-sections{display:flex;flex-wrap:nowrap;gap:20px;overflow-x:auto;}"
        "\n.summary-sections section{flex:0 0 300px;}"
        "\n.summary-sections table{display:table;width:100%;}"
        "\n.distribution-table{table-layout:fixed;width:100%;}"
        "\n.distribution-table th:nth-child(1), .distribution-table td:nth-child(1){width:33%;}"
        "\n.distribution-table th:nth-child(2), .distribution-table td:nth-child(2){width:33%;}"
        "\n.distribution-table th:nth-child(3), .distribution-table td:nth-child(3){width:34%;}"
        "\n"
    )

    freq_sections = build_sections(freq_module.generate_html_for_year)
    least_sections = build_sections(lfreq_module.generate_html_for_year)

    nav_links = (
        '<a href="freq_simulation_1_year.html">1Y Freq Sim</a> | '
        '<a href="freq_simulation_2_year.html">2Y Freq Sim</a> | '
        '<a href="freq_simulation_3_year.html">3Y Freq Sim</a> | '
        '<a href="freq_simulation_4_year.html">4Y Freq Sim</a> | '
        '<a href="freq_simulation_5_year.html">5Y Freq Sim</a> | '
        '<a href="freq_simulation_all_years.html">All Freq Sim</a><br>'
        '<a href="least_freq_simulation_1_year.html">1Y Least Freq Sim</a> | '
        '<a href="least_freq_simulation_2_year.html">2Y Least Freq Sim</a> | '
        '<a href="least_freq_simulation_3_year.html">3Y Least Freq Sim</a> | '
        '<a href="least_freq_simulation_4_year.html">4Y Least Freq Sim</a> | '
        '<a href="least_freq_simulation_5_year.html">5Y Least Freq Sim</a> | '
        '<a href="least_freq_simulation_all_years.html">All Least Freq Sim</a> | '
        '<a href="index.html">Back to Results</a>'
    )

    freq_html_section = '<div class="summary-sections">' + ''.join(freq_sections) + '</div>'
    least_html_section = '<div class="summary-sections">' + ''.join(least_sections) + '</div>'

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Simulations Summary</title>
    <style>{style}</style>
</head>
<body>
<header>
    <h1>Simulations Summary</h1>
    <nav>{nav_links}</nav>
</header>
<main>
    {freq_html_section}
    {least_html_section}
</main>
</body>
</html>
"""
    out_path = os.path.join(docs_dir, "simulations_summary.html")
    with open(out_path, "w") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    main()
