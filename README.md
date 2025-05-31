# Telegram Bot for Technical Support - "We Sell Everything!"

This bot automates technical support for the "We Sell Everything!" online store. It answers frequently asked questions, collects user requests, and directs them to the appropriate departments (programmers or sales).

## Description

The bot offers the following features:

*   **Automatic answers to frequently asked questions (FAQ):** The bot has a knowledge base with answers to common user questions.
*   **Request collection in a database:** All user requests to specialists are stored in an SQLite database (in memory).
*   **Request routing to departments:** The bot allows users to select a department (programmers or sales) and submit their request.
*   **Text message processing:** The bot understands user text messages.
*   **(In Development) Voice message support:** In the current version, voice message support is limited.

## Requirements

*   Python 3.7+
*   Libraries:
    *   `python-telegram-bot`
    *   `sqlite3` (included in the Python standard library)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [Your repository URL]
    cd [Repository directory name]
    ```

2.  **Install the necessary libraries:**
    ```bash
    pip install python-telegram-bot
    ```

3.  **Configure the bot token:**

    *   **WARNING:** Do not store the bot token in a public repository! The best practice is to use environment variables. This example stores the token directly in the code, which is **STRONGLY DISCOURAGED** for production environments.
    *   Open the `config.py` file and find the line:
        ```python
        TELEGRAM_TOKEN = "your telegram token"  # Replace with your token
        ```
    *   Replace `your telegram token` with the token you received from BotFather in Telegram.

## Running the Bot

1.  **Run the `main.py` script:**
    ```bash
    python main.py
    ```

2.  **Open Telegram and find your bot by its username.**

3.  **Send the `/start` command to the bot to begin.**

## Usage

1.  After starting the bot, send the `/start` command.
2.  The bot will ask you to select a question from the FAQ or contact a specialist.
3.  If you select a question from the FAQ, the bot will automatically answer it.
4.  If you select "Contact a specialist", the bot will ask you to choose a department (programmers or sales).
5.  After selecting a department, you will be asked to describe your problem.
6.  Your request will be saved in the database (in memory) and forwarded to the appropriate specialists (manual processing of requests is required in the current version).

## Administrators

### Viewing Requests

In the current version of the bot, requests are stored in an in-memory SQLite database. To view requests, you need to:

1.  Modify the `main.py` code to use a file-based SQLite database (specify the file path instead of `:memory:`).
2.  Use any SQLite database browser tool (e.g., DB Browser for SQLite) to open the database file and view the `support_requests` table.

### Processing Requests

The current version of the bot does not automatically send requests to specialists. The administrator needs to manually view the requests in the database and forward them to the appropriate departments. Automatic notification of specialists is planned for the future.

## Future Development

*   Implement voice message processing (transcription to text).
*   Automatic notification of specialists about new requests.
*   Create a web interface for viewing and managing requests.
*   Add the ability for users to rate the quality of the bot's answers.
*   Improve the FAQ system with the ability to add and edit questions and answers through an administrative interface.

## Acknowledgments

*   [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - for the excellent library for working with the Telegram Bot API.

## License

Soon...
