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


def top_frequencies(cur, current_date, top_n=10):
    """Return the ``top_n`` most frequent numbers prior to ``current_date``.

    The search range mirrors the predictor logic: only draws from the two
    years preceding ``current_date`` are considered.
    """
    start_date = current_date - datetime.timedelta(days=365 * 2)
    start_val = start_date.year * 10000 + start_date.month * 100 + start_date.day
    end_val = current_date.year * 10000 + current_date.month * 100 + current_date.day
    past_draws = get_past_numbers(cur, start_val, end_val)

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
    """Return predicted numbers using ``FrequencyWeightedPredictor`` logic.

    The predictor normally inspects the last two years of draws when
    calculating frequencies. Here we ensure only draws before ``current_date``
    influence the result. ``predictor`` is reused across calls to avoid
    reinitialising the database connection.
    """
    start_date = current_date - datetime.timedelta(days=365 * 2)
    start_val = start_date.year * 10000 + start_date.month * 100 + start_date.day
    end_val = current_date.year * 10000 + current_date.month * 100 + current_date.day
    past_draws = get_past_numbers(cur, start_val, end_val)

    if not past_draws:
        return [1, 2, 3, 4, 5, 6]

    original_get_recent = predictor._get_recent_numbers
    predictor._get_recent_numbers = lambda reference_date=None: past_draws
    result_str = predictor.predict(current_date.strftime("%Y-%m-%d"))
    predictor._get_recent_numbers = original_get_recent

    return [int(n) for n in result_str.split("-")]


def main():
    db_path = os.path.join(root, 'data', 'lotto.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    start_val = 20250125
    cur.execute(
        'SELECT year, month, day, data FROM history_lotto '
        'WHERE (year * 10000 + month * 100 + day) >= ? '
        'ORDER BY year DESC, month DESC, day DESC',
        (start_val,)
    )
    rows = cur.fetchall()

    result_rows = []
    total_win_numbers = 0
    distribution = {i: 0 for i in range(7)}

    predictor = FrequencyWeightedPredictor()
    # Prevent writing prediction results to the database during generation.
    predictor.db.save_predict_nums = lambda *args, **kwargs: None

    for year, month, day, data in rows:
        current_date = datetime.date(year, month, day)
        predicted_nums = freq_predict(cur, predictor, current_date)
        predicted_str = '-'.join(f"{n:02d}" for n in predicted_nums)
        freq_list = top_frequencies(cur, current_date)
        freq_str = ' '.join(f"{n:02d}({c})" for n, c in freq_list)
        # ``index.html`` treats the "win number" for a ticket purchased on
        # ``current_date`` as the results from the *next* draw.  Mirror that
        # behaviour here by fetching the very next record in the database.  If
        # there is no subsequent draw yet, the status should remain ``empty``.
        cur.execute(
            'SELECT data FROM history_lotto '
            'WHERE (year * 10000 + month * 100 + day) > ? '
            'ORDER BY year ASC, month ASC, day ASC LIMIT 1',
            (year * 10000 + month * 100 + day,)
        )
        next_row = cur.fetchone()
        has_next = next_row is not None
        if has_next:
            actual_nums, actual_str = parse_numbers(next_row[0])
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

    summary_html = ["<h3>FREQ</h3>"]
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
    distribution_html = ["<h3>FREQ</h3>"]
    distribution_html.append(
        "<table><thead><tr><th>Matched Numbers</th><th>Ticket Count</th><th>Hit Rate</th></tr></thead><tbody>"
        + ''.join(distribution_rows) + "</tbody></table>"
    )

    template_path = os.path.join(root, 'docs', 'index_template.html')
    with open(template_path, 'r') as f:
        html = f.read()
    html = html.replace('Historical Lotto Results', 'Frequency Weighted Simulation')
    html = html.replace('href="freq_simulation.html"', 'href="index.html"')
    html = html.replace('Frequency Simulation', 'Back to Results')
    html = html.replace('LLM Predict Results', 'Number Frequency (Top 10)')
    html = html.replace('{{ summary_tables }}', '\n'.join(summary_html))
    html = html.replace('{{ matched_distribution_tables }}', '\n'.join(distribution_html))
    html = html.replace('{{ need_to_be_replaced }}', '\n'.join(result_rows))

    out_path = os.path.join(root, 'docs', 'freq_simulation.html')
    with open(out_path, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
