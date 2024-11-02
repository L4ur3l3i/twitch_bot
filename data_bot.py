import os
import asyncio
from twitchAPI.twitch import Twitch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DataBot():
    def __init__(self):
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.twitch = Twitch(self.client_id, self.client_secret)
        asyncio.run(self.twitch.authenticate_app([]))

    async def get_user(self, login):
        async for user in self.twitch.get_users(logins=[login]):
            return user

    async def get_user_id(self, login):
        user = await self.get_user(login)
        return user['data'][0]['id']

    async def get_user_follows(self, user_id):
        async for follow in self.twitch.get_users_follows(from_id=user_id):
            yield follow

    async def get_user_followers(self, user_id):
        async for follow in self.twitch.get_users_follows(to_id=user_id):
            yield follow

    async def get_user_follows_count(self, user_id):
        count = 0
        async for follow in self.get_user_follows(user_id):
            count += 1
        return count

    async def get_user_followers_count(self, user_id):
        count = 0
        async for follow in self.get_user_followers(user_id):
            count += 1
        return count

    async def get_user_follows_list(self, user_id):
        follows = []
        async for follow in self.get_user_follows(user_id):
            follows.append(follow)
        return follows

    async def get_user_followers_list(self, user_id):
        followers = []
        async for follow in self.get_user_followers(user_id):
            followers.append(follow)
        return followers

    async def get_user_follows_names(self, user_id):
        follows = []
        async for follow in self.get_user_follows(user_id):
            follows.append(follow['to_name'])
        return follows

    async def get_user_followers_names(self, user_id):
        followers = []
        async for follow in self.get_user_followers(user_id):
            followers.append(follow['from_name'])
        return followers

    async def get_user_follows_names_list(self, user_id):
        follows = []
        async for follow in self.get_user_follows(user_id):
            follows.append(follow['to_name'])
        return follows

    async def get_user_followers_names_list(self, user_id):
        followers = []
        async for follow in self.get_user_followers(user_id):
            followers.append(follow['from_name'])
        return followers

