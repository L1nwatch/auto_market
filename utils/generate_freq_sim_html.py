#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate frequency-weighted simulation HTML."""

import sqlite3
import json
import re
import datetime
import os
from utils.common import root
from utils.frequency_predict import FrequencyWeightedPredictor


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
    numbers = [int(n) for n in re.findall(r"\d+", text)[:7]]
    return numbers, text


def get_past_numbers(cur, start_val, end_val):
    cur.execute(
        "SELECT data FROM history_lotto WHERE (year*10000+month*100+day) >= ? AND (year*10000+month*100+day) < ?",
        (start_val, end_val),
    )
    rows = [r[0] for r in cur.fetchall()]
    numbers = []
    for r in rows:
        nums, _ = parse_numbers(r)
        numbers.append(nums)
    return numbers


def freq_predict(cur, predictor, current_date):
    """Return predicted numbers for the given date using the existing predictor.

    Only draws on or after 2025-01-25 are considered when building the
    frequency table.
    """
    min_start = datetime.date(2025, 1, 25)
    start_date = max(min_start, current_date - datetime.timedelta(days=365 * 2))
    start_val = start_date.year * 10000 + start_date.month * 100 + start_date.day
    end_val = current_date.year * 10000 + current_date.month * 100 + current_date.day
    past_draws = get_past_numbers(cur, start_val, end_val)

    # When there are no prior draws in the limited range, fall back to the
    # predictor's default behaviour (which uses a wider history window). This
    # avoids returning the trivial sequence ``1-2-3-4-5-6`` which happens when
    # all frequencies are zero.
    if not past_draws:
        result_str = predictor.predict(current_date.strftime("%Y-%m-%d"))
        return [int(n) for n in result_str.split("-")]

    # Temporarily override the predictor's data source with draws from our
    # restricted range.
    original_get_recent = predictor._get_recent_numbers
    predictor._get_recent_numbers = lambda reference_date=None: past_draws
    result_str = predictor.predict(current_date)
    predictor._get_recent_numbers = original_get_recent

    numbers = [int(n) for n in result_str.split("-")]
    return numbers


def main():
    db_path = os.path.join(root, 'data', 'lotto.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    start_val = 20250125
    cur.execute(
        'SELECT year, month, day, data FROM history_lotto '
        'WHERE (year * 10000 + month * 100 + day) >= ? '
        'ORDER BY year ASC, month ASC, day ASC',
        (start_val,)
    )
    rows = cur.fetchall()

    result_rows = []
    total_win_numbers = 0
    distribution = {i: 0 for i in range(7)}

    predictor = FrequencyWeightedPredictor()
    predictor.db.save_predict_nums = lambda *args, **kwargs: None

    for year, month, day, data in rows:
        current_date = datetime.date(year, month, day)
        predicted_nums = freq_predict(cur, predictor, current_date)
        predicted_str = '-'.join(f"{n:02d}" for n in predicted_nums)
        actual_nums, actual_str = parse_numbers(data)
        match_count = sum(1 for n in predicted_nums if n in actual_nums)
        total_win_numbers += match_count
        if match_count in distribution:
            distribution[match_count] += 1
        date_str = f"{year}-{month:02d}-{day:02d}"
        win_status = f"match {match_count} number, win number: {actual_str}"
        row_html = '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>FREQ</td></tr>'.format(
            date_str, predicted_str, win_status, predicted_str
        )
        result_rows.append(row_html)

    total_tickets = len(result_rows)
    avg_hit_rate = total_win_numbers / (total_tickets * 6) if total_tickets else 0

    summary_html = ["<h3>FREQ</h3>"]
    summary_html.append(
        f"<table><tr><th>Total Tickets Bought</th><td>{total_tickets}</td></tr>"
        f"<tr><th>Total Win Numbers</th><td>{total_win_numbers}</td></tr>"
        f"<tr><th>Average Hit Rate</th><td>{avg_hit_rate:.2%}</td></tr></table>"
    )

    distribution_rows = []
    for i in range(7):
        distribution_rows.append(f"<tr><td>{i}</td><td>{distribution[i]}</td></tr>")
    distribution_html = ["<h3>FREQ</h3>"]
    distribution_html.append(
        "<table><thead><tr><th>Matched Numbers</th><th>Ticket Count</th></tr></thead><tbody>"
        + ''.join(distribution_rows) + "</tbody></table>"
    )

    template_path = os.path.join(root, 'docs', 'index_template.html')
    with open(template_path, 'r') as f:
        html = f.read()
    html = html.replace('Historical Lotto Results', 'Frequency Weighted Simulation')
    html = html.replace('href="freq_simulation.html"', 'href="index.html"')
    html = html.replace('Frequency Simulation', 'Back to Results')
    html = html.replace('{{ summary_tables }}', '\n'.join(summary_html))
    html = html.replace('{{ matched_distribution_tables }}', '\n'.join(distribution_html))
    html = html.replace('{{ need_to_be_replaced }}', '\n'.join(result_rows))

    out_path = os.path.join(root, 'docs', 'freq_simulation.html')
    with open(out_path, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
