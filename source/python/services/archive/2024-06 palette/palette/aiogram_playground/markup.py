from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


API_TOKEN = "YOUR_API_TOKEN_HERE"

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Create a simple ReplyKeyboardMarkup


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm your bot!\nUse the keyboard below:", reply_markup=keyboard_markup)


@dp.message_handler(lambda message: message.text == "Hi")
async def handle_hi(message: types.Message):
    await message.reply("Hello! How can I assist you today?")


@dp.message_handler(lambda message: message.text == "Bye")
async def handle_bye(message: types.Message):
    await message.reply("Goodbye! Have a nice day!")


if __name__ == "__main__":
    executor.run(dp, skip_updates=True)
