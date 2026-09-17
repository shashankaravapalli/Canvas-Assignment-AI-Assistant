# Canvas Assignment AI Assistant

A Discord-based assistant that connects to the Canvas LMS API to help students track and organize coursework and assignment deadlines.

## Features

- Connects to Canvas using the Canvas API
- Retrieves upcoming assignments
- Checks assignments due today
- Checks assignments due within the next 7 days
- Provides Discord commands for quick access
- Includes demo assignments for testing when live courses are unavailable
- Keeps API credentials secure using environment variables

## Discord Commands

- `!today` — Show assignments due today
- `!week` — Show assignments due in the next 7 days
- `!assignments` — Show upcoming Canvas assignments
- `!testassignments` — Display sample assignments for testing
- `!commands` — Display available bot commands

## Technologies

- Python
- Discord.py
- Canvas LMS REST API
- Requests
- python-dotenv
- GitHub Codespaces

## Security

Canvas API and Discord bot tokens are stored in a `.env` file and are excluded from Git using `.gitignore`.

## Current Status

The Discord bot and Canvas API integration are implemented. Demo mode allows the application to be tested when active Canvas courses or assignments are unavailable.