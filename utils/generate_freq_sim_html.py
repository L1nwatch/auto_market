#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate frequency-weighted simulation HTML."""

import json
import re
import datetime
import os
from utils.common import root
from utils.frequency_predict import FrequencyWeightedPredictor
from utils.custom_db import MyLottoDB


def top_frequencies(db, current_date, years=2, top_n=10):
    """Return the ``top_n`` most frequent numbers prior to ``current_date``.

    ``years`` specifies how many years of draws should be analysed. If ``years``
    is ``None`` the entire history is considered.
    """
    if years is None:
        start_date = db.get_first_lotto_date()
    else:
        start_date = current_date - datetime.timedelta(days=365 * years)
    past_draws = db.get_numbers_in_range(start_date, current_date)

    freq = {i: 0 for i in range(1, 50)}
    for draw in past_draws:
        for n in draw:
            if 1 <= n <= 49:
                freq[n] += 1

    return sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:top_n]


def parse_numbers(data_str):
    data = json.loads(data_str)
    if '0' in data:
        text = data['0']
    else:
        first = next(iter(data.values()))
        if isinstance(first, list):
            first = ' '.join(first[0]) if isinstance(first[0], list) else ' '.join(first)
        text = str(first)
    text = re.sub(r"\s+", " ", text.strip())
    # include the bonus ball as well so we have seven numbers in total
    numbers = [int(n) for n in re.findall(r"\d+", text)[:7]]
    return numbers, text


def get_past_numbers(db, start_date, end_date):
    rows = db.get_numbers_in_range(start_date, end_date)
    return rows


def freq_predict(db, predictor, current_date, years=2):
    """Return predicted numbers using ``FrequencyWeightedPredictor`` logic.

    ``years`` indicates how many years of historical draws to analyse. If
    ``years`` is ``None`` the entire history is used. Only draws before
    ``current_date`` are considered. ``predictor`` is reused across calls to
    avoid reinitialising the database connection.
    """
    if years is None:
        start_date = db.get_first_lotto_date()
    else:
        start_date = current_date - datetime.timedelta(days=365 * years)
    past_draws = get_past_numbers(db, start_date, current_date)

    if not past_draws:
        return [1, 2, 3, 4, 5, 6]

    original_get_recent = predictor._get_recent_numbers
    predictor._get_recent_numbers = lambda reference_date=None: past_draws
    result_str = predictor.predict(current_date.strftime("%Y-%m-%d"))
    predictor._get_recent_numbers = original_get_recent

    return [int(n) for n in result_str.split("-")]


def generate_html_for_year(db, rows, years):
    result_rows = []
    total_win_numbers = 0
    distribution = {i: 0 for i in range(7)}

    predictor = FrequencyWeightedPredictor()
    # Prevent writing prediction results to the database during generation.
    predictor.db.save_predict_nums = lambda *args, **kwargs: None

    for year, month, day, data in rows:
        current_date = datetime.date(year, month, day)
        predicted_nums = freq_predict(db, predictor, current_date, years=years)
        predicted_str = '-'.join(f"{n:02d}" for n in predicted_nums)
        freq_list = top_frequencies(db, current_date, years=years)
        freq_str = ' '.join(f"{n:02d}({c})" for n, c in freq_list)
        # ``index.html`` treats the "win number" for a ticket purchased on
        # ``current_date`` as the results from the *next* draw.  Mirror that
        # behaviour here by fetching the very next record in the database.  If
        # there is no subsequent draw yet, the status should remain ``empty``.
        next_row = db.get_next_record(f"{year}-{month:02d}-{day:02d}")
        has_next = next_row is not None
        if has_next:
            actual_nums, actual_str = parse_numbers(next_row['data'])
        else:
            actual_nums, actual_str = [], ''

        match_count = sum(1 for n in predicted_nums if n in actual_nums)
        date_str = f"{year}-{month:02d}-{day:02d}"

        if has_next:
            total_win_numbers += match_count
            if match_count in distribution:
                distribution[match_count] += 1
            win_status = f"match {match_count} number, win number: {actual_str}"
        else:
            win_status = "empty"

        row_html = (
            '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>FREQ</td></tr>'.format(
                date_str, predicted_str, win_status, freq_str
            )
        )
        result_rows.append(row_html)

    total_tickets = len(result_rows)
    avg_hit_rate = total_win_numbers / (total_tickets * 6) if total_tickets else 0

    years_label = f"{years}Y" if years is not None else "ALL"
    summary_html = [f"<h3>FREQ-{years_label}</h3>"]
    summary_html.append(
        f"<table><tr><th>Total Tickets Bought</th><td>{total_tickets}</td></tr>"
        f"<tr><th>Total Win Numbers</th><td>{total_win_numbers}</td></tr>"
        f"<tr><th>Average Hit Rate</th><td>{avg_hit_rate:.2%}</td></tr></table>"
    )

    distribution_rows = []
    resolved_tickets = sum(distribution.values())
    for i in range(7):
        hit_rate = 0
        if resolved_tickets:
            hit_rate = distribution[i] / resolved_tickets
        distribution_rows.append(
            f"<tr><td>{i}</td><td>{distribution[i]}</td><td>{hit_rate:.2%}</td></tr>"
        )
    distribution_html = [f"<h3>FREQ-{years_label}</h3>"]
    distribution_html.append(
        "<table><thead><tr><th>Matched Numbers</th><th>Ticket Count</th><th>Hit Rate</th></tr></thead><tbody>"
        + ''.join(distribution_rows) + "</tbody></table>"
    )

    template_path = os.path.join(root, 'docs', 'index_template.html')
    with open(template_path, 'r') as f:
        html = f.read()
    html = html.replace('Historical Lotto Results', f'Frequency Weighted Simulation ({years_label})')
    nav_links = (
        '<a href="freq_simulation_1_year.html">1Y Freq Sim</a> | '
        '<a href="freq_simulation_2_year.html">2Y Freq Sim</a> | '
        '<a href="freq_simulation_3_year.html">3Y Freq Sim</a> | '
        '<a href="freq_simulation_4_year.html">4Y Freq Sim</a> | '
        '<a href="freq_simulation_5_year.html">5Y Freq Sim</a> | '
        '<a href="freq_simulation_all_years.html">All Freq Sim</a> | '
        '<a href="index.html">Back to Results</a>'
    )
    html = html.replace('{{ nav_links }}', nav_links)
    html = html.replace('LLM Predict Results', 'Number Frequency (Top 10)')
    html = html.replace('{{ summary_tables }}', '\n'.join(summary_html))
    html = html.replace('{{ matched_distribution_tables }}', '\n'.join(distribution_html))
    html = html.replace('{{ need_to_be_replaced }}', '\n'.join(result_rows))

    out_name = f'freq_simulation_{years}_year.html' if years is not None else 'freq_simulation_all_years.html'
    out_path = os.path.join(root, 'docs', out_name)
    with open(out_path, 'w') as f:
        f.write(html)
    if years == 2:
        # maintain legacy filename expected by tests and README
        legacy_path = os.path.join(root, 'docs', 'freq_simulation.html')
        with open(legacy_path, 'w') as f:
            f.write(html)

    return out_path


def main():
    db = MyLottoDB()
    start_date = datetime.date(2025, 1, 25)
    rows = db.get_history_since(start_date)

    for years in range(1, 6):
        generate_html_for_year(db, rows, years)

    # build simulation using the entire history
    first_date = db.get_first_lotto_date()
    if first_date:
        all_rows = db.get_history_since(first_date)
        generate_html_for_year(db, all_rows, None)


if __name__ == '__main__':
    main()
