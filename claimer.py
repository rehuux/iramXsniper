"""
Username monitoring & claiming logic using user account
Developer: @gotweeds | Owner: Syed Rehan
"""

import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.account import CheckUsernameRequest, UpdateUsernameRequest
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest as ChannelUpdateUsername
import config
from database import get_pending_usernames, mark_claimed, update_last_checked

class UsernameClaimer:
    def __init__(self):
        self.client = None
        self.is_running = False

    async def start(self):
        """Initialize user client"""
        self.client = TelegramClient(
            'session',
            config.API_ID,
            config.API_HASH,
            device_model='UsernameSniper',
            system_version='1.0'
        )
        try:
            if config.SESSION_STRING:
                await self.client.start(session_string=config.SESSION_STRING)
            else:
                await self.client.start(phone=config.PHONE_NUMBER)
            me = await self.client.get_me()
            print(f"✅ User logged in as: {me.first_name} (@{me.username})")
            # Save session string for future runs
            if not config.SESSION_STRING:
                session_string = await self.client.session.save()
                print(f"💾 Session string (save in .env): {session_string}")
            return True
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    async def check_availability(self, username: str) -> bool:
        """Return True if username is available"""
        try:
            result = await self.client(CheckUsernameRequest(username))
            return result
        except errors.FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return False
        except Exception as e:
            print(f"⚠️ Check error: {e}")
            return False

    async def claim_to_channel(self, username: str) -> bool:
        """Create a channel and claim username"""
        try:
            # Create channel
            channel = await self.client(CreateChannelRequest(
                title=f"@{username}",
                about=f"Username claimed via {config.DEV_NAME}",
                megagroup=False
            ))
            channel_id = channel.chats[0].id
            # Assign username
            await self.client(ChannelUpdateUsername(
                channel=channel_id,
                username=username
            ))
            return True
        except errors.UsernameOccupiedError:
            print(f"❌ @{username} taken during claim")
            return False
        except errors.FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return False
        except Exception as e:
            print(f"❌ Claim error: {e}")
            return False

    async def claim_to_user(self, username: str) -> bool:
        """Claim username to user account"""
        try:
            await self.client(UpdateUsernameRequest(username))
            return True
        except errors.UsernameOccupiedError:
            return False
        except errors.FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return False
        except Exception as e:
            print(f"❌ Claim error: {e}")
            return False

    async def monitor_and_claim(self, username: str, user_id: int, bot):
        """Monitor a single username and claim when available"""
        print(f"🔍 Monitoring @{username} for user {user_id}")
        while self.is_running:
            try:
                available = await self.check_availability(username)
                update_last_checked(username)

                if available:
                    print(f"🎯 @{username} is AVAILABLE! Claiming...")
                    if config.CLAIM_TO == 'channel':
                        success = await self.claim_to_channel(username)
                    else:
                        success = await self.claim_to_user(username)

                    if success:
                        mark_claimed(username)
                        msg = f"✅ @{username} claimed successfully!"
                        print(msg)
                        # Send notification to the user who added it
                        try:
                            await bot.send_message(user_id, msg)
                        except Exception as e:
                            print(f"⚠️ Failed to send notification: {e}")
                        break  # stop monitoring this username
                    else:
                        # Claim failed – maybe taken instantly, keep watching
                        await asyncio.sleep(1)
                        continue

                await asyncio.sleep(config.CHECK_INTERVAL)

            except Exception as e:
                print(f"⚠️ Error monitoring @{username}: {e}")
                await asyncio.sleep(2)

    async def monitor_loop(self, bot):
        """Main monitoring loop – checks all pending usernames"""
        self.is_running = True
        while self.is_running:
            pending = get_pending_usernames()
            if not pending:
                await asyncio.sleep(5)
                continue

            # Launch a monitor task for each pending username
            tasks = []
            for entry in pending:
                username = entry['username']
                user_id = entry['user_id']
                tasks.append(asyncio.create_task(
                    self.monitor_and_claim(username, user_id, bot)
                ))

            # Wait for all to finish (they finish when claimed or stopped)
            await asyncio.gather(*tasks, return_exceptions=True)

            # If we stopped, exit loop
            if not self.is_running:
                break

            # Otherwise, loop again to pick up any new usernames added
            await asyncio.sleep(1)

    async def stop(self):
        self.is_running = False
        if self.client:
            await self.client.disconnect()
