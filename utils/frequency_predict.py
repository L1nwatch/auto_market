#!/bin/env python3
# -*- coding: utf-8 -*-
"""Frequency weighted lotto predictor."""
import datetime
from utils.common import logger
from utils.custom_db import MyLottoDB


class FrequencyWeightedPredictor:
    """Predict lotto numbers using frequency analysis of past draws."""

    def __init__(self, *, min_start_date=None):
        self.db = MyLottoDB()
        # Ignore draws earlier than this date when building the
        # frequency table. Defaults to the first draw of the new
        # method on 2025‑01‑25.
        self.min_start_date = min_start_date or datetime.date(2025, 1, 25)

    def _get_recent_numbers(self):
        """Return lists of lotto numbers from the last two years."""
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=365 * 2)
        start_date = max(start.date(), self.min_start_date)
        return self.db.get_lotto_numbers_since(start_date)

    def predict(self, last_lotto_date):
        draws = self._get_recent_numbers()
        if not draws:
            # Fall back to using all available draws so that a
            # reasonable prediction is returned even for an empty
            # recent history window.
            draws = self.db.get_lotto_numbers_since(self.min_start_date)
        freq = {i: 0 for i in range(1, 50)}
        for draw in draws:
            for num in draw:
                if 1 <= num <= 49:
                    freq[num] += 1
        top_six = sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:6]
        numbers = sorted([n for n, _ in top_six])
        result = "-".join(f"{n:02d}" for n in numbers)
        self.db.save_predict_nums(
            last_lotto_date,
            {"method": "frequency_weighted"},
            result,
            source="FREQ",
        )
        logger.info(f"Predict numbers: {result}")
        return result
