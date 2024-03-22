import requests



class LunarCrushProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://lunarcrush.com/api4"

    def get_top_coins(self, sort="alt_rank"):
        endpoint = f"/public/coins/list/v2?sort={sort}"
        url = self.base_url + endpoint
        headers = {'Authorization': f'Bearer {self.api_key}'}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed, code: {response.status_code}, error message: {response.text}")
