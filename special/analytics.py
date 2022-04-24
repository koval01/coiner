import logging

from config import GA_ID, GA_SECRET
from aiohttp import ClientSession
from aiogram import types


class Analytics:
    def __int__(self) -> None:
        self.id = GA_ID
        self.secret = GA_SECRET

        self.host = "www.google-analytics.com"
        self.path = "mp/collect"

    async def request(self, json: dict, params: dict) -> None:
        async with ClientSession() as session:
            try:
                await session.post(
                    f"https://{self.host}/{self.path}", json=json, params=params
                )
            except Exception as e:
                logging.warning(
                    "Error sending request to Google Analytics. Error name: %s. Error details: %s" %
                    e.__class__.__name__, e
                )

    def build_payload(self, user_id: int, user_lang_code: str, action_name: str) -> dict:
        return {
            'client_id': user_id,
            'user_id': user_id,
            'events': [{
                'name': action_name,
                'params': {
                    'language': user_lang_code,
                    'engagement_time_msec': '1',
                }
            }],
        }

    async def send(self, message: types.Message) -> None:
        await self.request({
            "measurement_id": self.id, "api_secret": self.secret
        }, self.build_payload(
            message.from_user.id,
            message.from_user.language_code,
            message.get_command()
        ))

    def __str__(self) -> str:
        return self.id
