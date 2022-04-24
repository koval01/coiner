import logging

from config import GA_ID, GA_SECRET
from aiohttp import ClientSession
from aiogram import types


class Analytics:
    def __init__(self) -> None:
        self.id = GA_ID
        self.secret = GA_SECRET

        self.host = "www.google-analytics.com"
        self.path = "mp/collect"

    async def request(self, params: dict, json: dict) -> None:
        async with ClientSession() as session:
            try:
                async with session.post(
                        f"https://{self.host}/{self.path}", json=json, params=params
                ) as response:
                    if response.status >= 200 < 300:
                        logging.debug("OK code Google Analytics")
                    else:
                        logging.warning(f"Error code Google Analytics: {response.status}. "
                                        f"Detail response: {response.text[:512]}")
            except Exception as e:
                logging.warning(
                    f"Error sending request to Google Analytics. "
                    f"Error name: {e.__class__.__name__}. Error details: {e}"
                )

    def build_payload(self, user_id: int, user_lang_code: str, action_name: str) -> dict:
        return {
            'client_id': str(user_id),
            'user_id': str(user_id),
            'events': [{
                'name': action_name,
                'params': {
                    'language': user_lang_code,
                    'engagement_time_msec': '1',
                }
            }],
        }

    async def send(self, message: types.Message, alt_action: str = None) -> None:
        await self.request({
            "measurement_id": self.id, "api_secret": self.secret
        }, self.build_payload(
            message.from_user.id,
            message.from_user.language_code,
            message.get_command()[1:] if not alt_action else alt_action
        ))

    def __str__(self) -> str:
        return self.id
