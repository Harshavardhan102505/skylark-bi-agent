import requests

class MondayClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }

    def fetch_board_items(self, board_id: str, limit: int = 50) -> list:
        """Fetches lightweight item records from monday.com board."""
        query = """
        query ($board_id: [ID!], $limit: Int!) {
          boards (ids: $board_id) {
            items_page (limit: $limit) {
              items {
                id
                name
                column_values {
                  column {
                    title
                  }
                  text
                }
              }
            }
          }
        }
        """
        variables = {"board_id": [str(board_id)], "limit": limit}
        response = requests.post(self.url, json={"query": query, "variables": variables}, headers=self.headers)
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        try:
            return data["data"]["boards"][0]["items_page"]["items"]
        except (KeyError, IndexError):
            return []