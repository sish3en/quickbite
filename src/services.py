import requests


class MealApiService:
    """Encapsulates all communication with TheMealDB."""

    def __init__(self, base_url, timeout=5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def search(self, query):
        if not query or len(query.strip()) < 2:
            return [], "Please enter at least two characters."
        try:
            response = requests.get(
                f"{self.base_url}/search.php", params={"s": query.strip()}, timeout=self.timeout
            )
            response.raise_for_status()
            meals = response.json().get("meals") or []
            return meals, None
        except (requests.RequestException, ValueError):
            return [], "The meal service is temporarily unavailable. Please try again."
