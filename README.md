# paid-sub-tg-bot
This is a MVP of a Telegram bot that receives payments in exchange for the invitation link to a private Telegram channel.

Stack: asyncio, aiogram, SQLite, AsyncIOScheduler.

Work in direct messages:
- upon receiving the /start command, the bot sends a welcome message;
- the welcome message includes a button for proceeding to payment ("Subscribe" button).

Payment process:
- after the user has made the payment, the bot receives a notification from the payment provider about the successful payment;
- upon receiving such a notification, the bot automatically creates a subscription (as a database entry) and notifies the user about it;
- after the subscription is created, a unique link for subscribing to the channel with a limit of 1 user is generated;
- the created link is sent to the user after payment;
- administrators of the private channel receive a notification that this user has made the payment and received an invitation link.

Background tasks:
- the only background task of the bot is to check subscriptions and remind users about expiring subscriptions;
- every day at 9:00 AM, a background task to check subscriptions is executed;
- if there are less than 3 days left until the subscription expires, the bot sends the user a reminder;
- if the subscription has expired, it is marked as inactive (removing an entry from a database), and the user is removed from the channel;
- administrators of the private channel receive a notification that this user has been removed from the channel.
