#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import openai
import os
import requests
import json
from loguru import logger
from utils.custom_db import MyLottoDB

__author__ = '__L1n__w@tch'

ai_key = os.getenv("OPENAI_API_KEY")

class LargeLanguageModel:
    def __init__(self, host="host.docker.internal", model="deepseek"):
        self.host = host
        self.model = model
        self.db = MyLottoDB()

    def deepseek_request(self, prompt):
        url = f"http://{self.host}:8080/api/generate"
        data = {
            "model": "deepseek-r1:14b",
            "prompt": json.dumps(prompt),
            "temperature": 0.5
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            result = response.text
            # logger.info("[DeepSeek] Response: {}".format(result))

            json_objects = [json.loads(line) for line in result.splitlines()]
            final_response = "".join([obj["response"] for obj in json_objects if "response" in obj])

            return final_response
        except requests.exceptions.RequestException as e:
            return f"Error interacting with Ollama API: {e}"

    def openai_request(self, prompt):
        client = openai.OpenAI(api_key=ai_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that responds with valid JSON only."},
                {"role": "user", "content": json.dumps(prompt)}
            ],
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content

    def predict(self, history_data, last_lotto_date):
        prompt = {
            "background": "The following dataset contains 24 groups of numbers. Each group consists of 6 main numbers and 1 special number, all selected from the range 01 to 49.",
            "dataset": history_data,
            "task": "0. Ignores the special number. 1. Analyze the dataset to identify any patterns or characteristics in how the numbers are selected. 2. Summarize the patterns observed in the main numbers and the special numbers. 3. Generate 5 new groups of numbers that follow the identified patterns.",
            "response_format": "{'generate_nums': ['01', '02', '03, '04', '05', '06']}"
        }
        logger.info(f"Prompt: {prompt}")
        # send prompt to model and get numbers
        logger.info("send prompt to model and get numbers")
        if self.model == "deepseek":
            response = self.deepseek_request(prompt)
        else:
            response = self.openai_request(prompt)
        self.db.save_predict_nums(last_lotto_date, prompt, response)
        return response


if __name__ == "__main__":
    pass
