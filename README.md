# WPBrigade — Admin User-Management Chatbot

An operational Admin Chatbot built with **Python, FastAPI, and SQLite** that allows administrators to add, update, and remove user information through natural chat commands.

## Features
1. **Simple Email Auto-Login:** Automatically logs in any user whose email exists in the system database (e.g., `admin@wpbrigade.com`, `asim.jameel7113@gmail.com`, `samantha@xyz.com`, or newly added users).
2. **Natural Language Chat Commands:**
   - `can you add the user "john.smith@xyz.com" with phone number "+92332"`
   - `can you update samanthas city to Cordoba`
   - `can you remove the user "john.smith@xyz.com"`

## How to Run Locally
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
