#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a summary page for all simulation results."""

import os
import re
import utils.common as common


def _extract_section(html: str) -> str:
    match = re.search(r"(<h2>Summary.*?)(?:<h2>Results|</main>)", html, re.S)
    return match.group(1).strip() if match else ""


def _extract_heading(html: str) -> str:
    match = re.search(r"<h1>(.*?)</h1>", html)
    return match.group(1) if match else ""


def main() -> str:
    docs_dir = os.path.join(common.root, "docs")
    freq_path = os.path.join(docs_dir, "freq_simulation.html")
    least_path = os.path.join(docs_dir, "least_freq_simulation.html")

    with open(freq_path, "r") as f:
        freq_html = f.read()
    with open(least_path, "r") as f:
        least_html = f.read()

    style_match = re.search(r"<style>(.*?)</style>", freq_html, re.S)
    style = style_match.group(1) if style_match else ""

    freq_heading = _extract_heading(freq_html)
    least_heading = _extract_heading(least_html)
    freq_section = _extract_section(freq_html)
    least_section = _extract_section(least_html)

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
    <section>
        <h2>{freq_heading}</h2>
        {freq_section}
    </section>
    <section>
        <h2>{least_heading}</h2>
        {least_section}
    </section>
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
