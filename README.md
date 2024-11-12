# Telegram Fast Food Bot

This project is a Telegram bot for a fast-food ordering system, allowing users to view menus, add items to their cart, and complete orders through Telegram. Built using the `aiogram` library, this bot provides a structured and interactive ordering experience.

## Features

- User registration and information collection
- Menu navigation with categories and items
- Shopping cart management
- Order placement and payment handling
- Manager notification for new orders

## Requirements

- Python 3.10+
- `aiogram` library
- `asyncio` for asynchronous operations

## Getting Started

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/telegramfastfoodbot.git
    cd telegramfastfoodbot
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. Create a `.env` file in the root directory based on `.env.example`:
    ```env
    TELEGRAM_TOKEN=your_telegram_token_here
    PAYMENT_TOKEN=your_payment_token_here
    MANAGER_ID=your_manager_id_here
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_ADDRESS=your_database_address
    DB_NAME=your_database_name
    ```

   Replace the placeholders with your actual configuration values.

### Database Setup

Configure your database settings in `.env` and ensure the database is initialized and ready for use.

### Running the Bot

1. Start the bot:
    ```bash
    python main.py
    ```

2. The bot will begin polling Telegram for updates. Users can interact with it by sending commands or selecting options from menus.

## Usage

- `/start` - Register a new user and begin interaction.
- Main Menu - View main options (e.g., place an order, view cart).
- Categories - Navigate through product categories to view items.
- Cart - Add, remove, and modify items in your cart.
- Order - Complete the order and pay directly through Telegram.

## Project Structure

- `main.py` - Entry point of the bot.
- `infrastructure/database/` - Database utility functions for managing user data, orders, and cart items.
- `presenter/bot/` - Contains bot UI elements (keyboards, menus) and helper functions.
- `settings/config.py` - Bot configuration file, including API tokens and database credentials.

## Contributing

Feel free to fork the repository and submit pull requests if you'd like to contribute!

## License

This project is licensed under the MIT License.
