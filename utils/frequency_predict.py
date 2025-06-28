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

    def _get_recent_numbers(self, reference_date=None):
        """Return lists of lotto numbers from the two years prior to `reference_date`."""
        if reference_date is None:
            reference_date = datetime.datetime.now()
        if isinstance(reference_date, datetime.date) and not isinstance(reference_date, datetime.datetime):
            reference_date = datetime.datetime.combine(reference_date, datetime.time.min)
        start = reference_date - datetime.timedelta(days=365 * 2)
        return self.db.get_lotto_numbers_since(start)

    def predict(self, last_lotto_date):
        if isinstance(last_lotto_date, (datetime.date, datetime.datetime)):
            reference_date = (last_lotto_date if isinstance(last_lotto_date, datetime.datetime)
                             else datetime.datetime.combine(last_lotto_date, datetime.time.min))
            last_lotto_date_str = last_lotto_date.strftime("%Y-%m-%d")
        else:
            reference_date = datetime.datetime.strptime(last_lotto_date, "%Y-%m-%d")
            last_lotto_date_str = last_lotto_date

        draws = self._get_recent_numbers(reference_date=reference_date)
        freq = {i: 0 for i in range(1, 50)}
        for draw in draws:
            for num in draw:
                if 1 <= num <= 49:
                    freq[num] += 1
        top_six = sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:6]
        numbers = sorted([n for n, _ in top_six])
        result = "-".join(f"{n:02d}" for n in numbers)
        self.db.save_predict_nums(
            last_lotto_date_str,
            {"method": "frequency_weighted"},
            result,
            source="FREQ",
        )
        logger.info(f"Predict numbers: {result}")
        return result


class LeastFrequencyWeightedPredictor:
    """Predict lotto numbers using least frequent numbers from past draws."""

    def __init__(self):
        self.db = MyLottoDB()

    def _get_recent_numbers(self, reference_date=None):
        if reference_date is None:
            reference_date = datetime.datetime.now()
        if (
            isinstance(reference_date, datetime.date)
            and not isinstance(reference_date, datetime.datetime)
        ):
            reference_date = datetime.datetime.combine(reference_date, datetime.time.min)
        start = reference_date - datetime.timedelta(days=365 * 2)
        return self.db.get_lotto_numbers_since(start)

    def predict(self, last_lotto_date):
        if isinstance(last_lotto_date, (datetime.date, datetime.datetime)):
            reference_date = (
                last_lotto_date
                if isinstance(last_lotto_date, datetime.datetime)
                else datetime.datetime.combine(last_lotto_date, datetime.time.min)
            )
            last_lotto_date_str = last_lotto_date.strftime("%Y-%m-%d")
        else:
            reference_date = datetime.datetime.strptime(last_lotto_date, "%Y-%m-%d")
            last_lotto_date_str = last_lotto_date

        draws = self._get_recent_numbers(reference_date=reference_date)
        freq = {i: 0 for i in range(1, 50)}
        for draw in draws:
            for num in draw:
                if 1 <= num <= 49:
                    freq[num] += 1
        bottom_six = sorted(freq.items(), key=lambda x: (x[1], x[0]))[:6]
        numbers = sorted([n for n, _ in bottom_six])
        result = "-".join(f"{n:02d}" for n in numbers)
        self.db.save_predict_nums(
            last_lotto_date_str,
            {"method": "least_frequency_weighted"},
            result,
            source="LFREQ",
        )
        logger.info(f"Predict numbers: {result}")
        return result
