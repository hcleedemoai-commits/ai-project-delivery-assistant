import json
import re


class AIResponseParser:
    """
    Turns an AI's text reply into structured JSON.
    Tries a direct parse first, then falls back to pulling out the first
    {...} block in case the model added extra commentary around it.
    """

    def parse(self, response_text: str):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            json_text = self._extract_json(response_text)
            if json_text:
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass

            return {
                "error": "Unable to parse AI response as JSON",
                "raw_response": response_text,
            }

    def _extract_json(self, text: str):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group() if match else None
