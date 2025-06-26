#!/bin/env python3
# -*- coding: utf-8 -*-
"""Frequency weighted lotto predictor."""
import datetime
from utils.common import logger
from utils.custom_db import MyLottoDB


class FrequencyWeightedPredictor:
    """Predict lotto numbers using frequency analysis of past draws."""

    def __init__(self):
        self.db = MyLottoDB()

    def _get_recent_numbers(self):
        """Return lists of lotto numbers from the last two years."""
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=365 * 2)
        return self.db.get_lotto_numbers_since(start)

    def predict(self, last_lotto_date):
        draws = self._get_recent_numbers()
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
