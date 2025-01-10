#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import openai
import os
from loguru import logger

__author__ = '__L1n__w@tch'

ai_key = os.getenv("OPENAI_API_KEY")


class LargeLanguageModel:
    def __init__(self):
        self.client = openai.OpenAI(api_key=ai_key)

    def openai_request(self, prompt):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that responds with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content

    def predict(self, history_data):
        prompt = {
            "background": "The following dataset contains 24 groups of numbers. Each group consists of 6 main numbers and 1 special number, all selected from the range 01 to 49.",
            "dataset": history_data,
            "task": "1. Analyze the dataset to identify any patterns or characteristics in how the numbers are selected. 2. Summarize the patterns observed in the main numbers and the special numbers. 3. Generate 5 new groups of numbers that follow the identified patterns.",
            "response_format": "{'generate_nums': ['01', '02', '03, '04', '05', '06', '07']}"
        }
        logger.info(f"Prompt: {prompt}")
        # send prompt to model and get numbers
        logger.info("send prompt to model and get numbers")
        response = self.openai_request(prompt)
        return response


if __name__ == "__main__":
    pass
