import os
import asyncio
from telegram import Bot

from .utils import (
    API_TELEGRAM_BOT,
    MAIN_DIR
)
from .database import (
    CreateBackup,
    DatabaseHandler
)
from .processInput import (
    UserInputProcessor
)

class TelegramBot:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.bot = Bot(API_TELEGRAM_BOT)

        self.last_update_id_filename = os.path.join(MAIN_DIR, ".last_update_id_bot")
        self.get_last_update_id()
        self.chat_id = None
        
    def get_last_update_id(self):
        if os.path.isfile(self.last_update_id_filename):
           with open(self.last_update_id_filename, "r") as f:
               self.last_update_id = int(f.readlines()[0].strip()) 
        else:
            self.last_update_id = None

    def save_last_update_id(self, update_id: int):
        with open(self.last_update_id_filename, "w") as f:
            f.write(str(update_id))

    async def processMessages(self):
        new_entries = [m for m in self.messages if "DELETE" not in m]
        del_entries = [m for m in self.messages if "DELETE" in m]        

        success_new_entries = []
        fail_new_entries = []
        success_del_entries = []
        fail_del_entries = []
        
        for message in new_entries:
            info = UserInputProcessor(message)
            if info.isValid:
                self.db_handler.add_entry(
                    month=info.month, 
                    year=info.year,
                    day=info.day, 
                    category=info.category, 
                    value=info.value, 
                    description=info.description,
                )
                success_new_entries.append(message)
            else:
                fail_new_entries.append(message)
        
        for message in del_entries:
            message = message.replace("DELETE", "")
            info = UserInputProcessor(message)
            if info.isValid:
                success = self.db_handler.delete_entry(
                                month=info.month, 
                                year=info.year,
                                day=info.day, 
                                category=info.category, 
                                value=info.value, 
                                description=info.description,
                            )
                if success:
                    success_del_entries.append(message)
                else:
                    fail_del_entries.append(message)
            else:
                fail_del_entries.append(message)
                    
        if success_new_entries:
            await self.bot.send_message(text="THE FOLLOWING EXPENSES WERE ADDED: ", chat_id=self.chat_id)
            for message in success_new_entries:
                await self.bot.send_message(text=message, chat_id=self.chat_id)
        if fail_new_entries:
            await self.bot.send_message(text="COULDN'T ADD THE FOLLOWING EXPENSES: ", chat_id=self.chat_id)
            for message in fail_new_entries:
                await self.bot.send_message(text=message, chat_id=self.chat_id)
        if success_del_entries:
            await self.bot.send_message(text="THE FOLLOWING EXPENSES WERE DELETED: ", chat_id=self.chat_id)
            for message in success_del_entries:
                await self.bot.send_message(text=message, chat_id=self.chat_id)
        if fail_del_entries:
            await self.bot.send_message(text="COULDN'T DELETE THE FOLLOWING EXPENSES: ", chat_id=self.chat_id)
            for message in fail_del_entries:
                await self.bot.send_message(text=message, chat_id=self.chat_id)
            
    async def run(self):
        ## Asynchronous run logic.
        await self.get_updates()
        self.messages = []
        for update in self.updates:        
            self.save_last_update_id(update.update_id)
            self.messages.append(update.message.text)
            self.chat_id = update.message.chat.id
        await self.processMessages()
        
    async def get_updates(self):
        ## Fetch updates asynchronously.
        offset = self.last_update_id+1 if self.last_update_id else None
        self.updates = await self.bot.getUpdates(offset=offset)     

async def mainBot():
    CreateBackup()
    bot = TelegramBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(mainBot())
    