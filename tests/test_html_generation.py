import shutil
import sqlite3
import importlib
from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bs4 import BeautifulSoup
import pytest

import utils.common as common


@pytest.fixture()
def html_files(tmp_path, monkeypatch):
    """Run HTML generation scripts in a temporary directory."""
    tmp_dir = tmp_path
    # set up directory structure
    (tmp_dir / "data").mkdir()
    (tmp_dir / "docs").mkdir()

    # copy required resources
    shutil.copy(Path(common.root) / "data" / "lotto.db", tmp_dir / "data" / "lotto.db")
    shutil.copy(Path(common.root) / "docs" / "index_template.html", tmp_dir / "docs" / "index_template.html")

    # patch root used by helper modules
    monkeypatch.setattr(common, "root", str(tmp_dir))

    cwd = os.getcwd()
    os.chdir(tmp_dir)

    # reload modules so they pick up the patched root
    import utils.custom_db as custom_db
    import utils.generate_freq_sim_html as gen_html
    import auto_lotto_main
    importlib.reload(custom_db)
    importlib.reload(gen_html)
    importlib.reload(auto_lotto_main)

    original_gen = gen_html.generate_html_for_year

    def limited_generate_html_for_year(db, rows, years):
        if years is None:
            rows = rows[:10]
        return original_gen(db, rows, years)

    monkeypatch.setattr(gen_html, "generate_html_for_year", limited_generate_html_for_year)

    # replace global DB connection with one using the temp directory
    auto_lotto_main.MY_DB = custom_db.MyLottoDB()

    auto_lotto_main.update_html_with_win_status_and_predict_number()
    os.chdir(cwd)

    return (
        tmp_dir / "docs" / "index.html",
        tmp_dir / "docs" / "freq_simulation.html",
        tmp_dir / "docs" / "freq_simulation_all_years.html",
        tmp_dir / "data" / "lotto.db",
    )


def test_index_html_generation(html_files):
    index_path, _, _, db_path = html_files
    assert index_path.exists(), "index.html should be generated"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM buying_history")
    expected_rows = cur.fetchone()[0]
    cur.execute(
        "SELECT last_lotto_date, bought_numbers, win_status, predict_number_sources "
        "FROM buying_history ORDER BY last_lotto_date DESC LIMIT 1"
    )
    latest_row = cur.fetchone()
    conn.close()

    soup = BeautifulSoup(index_path.read_text(), "html.parser")
    rows = soup.select("#resultsTable tbody tr")

    assert len(rows) == expected_rows
    cells = [c.get_text(strip=True) for c in rows[0].find_all("td")]
    assert cells[0] == latest_row[0]
    assert cells[1] == latest_row[1]
    assert cells[2].startswith(latest_row[2].split()[0])
    assert cells[4] == latest_row[3]


def test_freq_simulation_html_generation(html_files):
    _, freq_path, _, db_path = html_files
    assert freq_path.exists(), "freq_simulation.html should be generated"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM history_lotto WHERE (year*10000 + month*100 + day) >= 20250125"
    )
    expected_rows = cur.fetchone()[0]
    cur.close()
    conn.close()

    soup = BeautifulSoup(freq_path.read_text(), "html.parser")
    rows = soup.select("#resultsTable tbody tr")

    assert len(rows) == expected_rows
    first_cells = [c.get_text(strip=True) for c in rows[0].find_all("td")]
    assert first_cells[-1] == "FREQ"


def test_freq_simulation_all_years_html_generation(html_files):
    _, _, all_path, db_path = html_files
    assert all_path.exists(), "freq_simulation_all_years.html should be generated"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM history_lotto")
    expected_rows = min(cur.fetchone()[0], 10)
    cur.close()
    conn.close()

    soup = BeautifulSoup(all_path.read_text(), "html.parser")
    rows = soup.select("#resultsTable tbody tr")

    assert len(rows) == expected_rows
    first_cells = [c.get_text(strip=True) for c in rows[0].find_all("td")]
    assert first_cells[-1] == "FREQ"
