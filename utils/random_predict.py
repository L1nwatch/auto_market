#!/bin/env python3
# -*- coding: utf-8 -*-
"""Generate random lotto numbers."""
import random
from utils.common import logger
from utils.custom_db import MyLottoDB


class RandomLottoNumberGenerator:
    """Simple random lotto number generator."""

    def __init__(self):
        self.db = MyLottoDB()

    def predict(self, last_lotto_date):
        numbers = random.sample(range(1, 50), 6)
        numbers.sort()
        result = "-".join(f"{n:02d}" for n in numbers)
        self.db.save_predict_nums(
            last_lotto_date,
            {"method": "random"},
            result,
            source="RANDOM",
        )
        logger.info(f"Predict numbers: {result}")
        return result
