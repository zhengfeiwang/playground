import os

import requests
from dotenv import load_dotenv


class Mimir:
    SYSTEM_PROMPT = """You are working on a multi-agent context solving a software engineering problem. You play the planner role to lead the executor agent(s) to solve the problem.
Please think like a senior software engineer and provide a detailed plan for the executor agent(s) to solve the problem.
Try to split tasks into simpler sub-tasks, specify test requirements, set clear checkpoints and tell the executor agent(s) how to check its work.
Be clear and specific, prioitize agility and don't over-design or over-engineer the solution."""

    def __init__(self):
        if not os.getenv("AZURE_OPENAI_API_KEY"):
            load_dotenv()
        self._api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self._endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    def plan(self, message: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key,
        }
        data = {
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            "model": "o3-mini",
        }
        response = requests.post(self._endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    mimir = Mimir()
    print(mimir.plan("Hello, how are you?"))
