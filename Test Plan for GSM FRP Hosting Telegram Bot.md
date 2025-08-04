# Test Plan for GSM FRP Hosting Telegram Bot

## 1. Introduction
This document outlines the test plan for the GSM FRP Hosting Telegram Bot, covering its core functionalities, user management, service provision, and administrative features.

## 2. Test Environment
*   **Operating System:** Ubuntu 22.04 (Sandbox Environment)
*   **Python Version:** 3.11.0rc1
*   **Dependencies:** `python-telegram-bot`, `SQLAlchemy`, `bcrypt` (as specified in `requirements.txt`)
*   **Database:** SQLite (gsm_frp_bot.db)
*   **Telegram Bot Token:** A valid Telegram Bot API token must be set as an environment variable `BOT_TOKEN`.
*   **Admin User IDs:** Admin Telegram user IDs must be set in `ADMIN_USER_IDS` environment variable (comma-separated).

## 3. Test Cases

### 3.1. Core Bot Functionality

*   **Test Case ID:** CBF-001
    *   **Description:** Verify `/start` command.
    *   **Steps:**
        1.  Send `/start` to the bot.
    *   **Expected Result:** Bot replies with a welcome message including the user's mention and instructions to use `/help`.

*   **Test Case ID:** CBF-002
    *   **Description:** Verify `/help` command.
    *   **Steps:**
        1.  Send `/help` to the bot.
    *   **Expected Result:** Bot replies with a list of all available commands and a support message.

### 3.2. User Management

*   **Test Case ID:** UM-001
    *   **Description:** Register a new user successfully.
    *   **Steps:**
        1.  Send `/register`.
        2.  Provide a valid email address when prompted.
        3.  Provide a password when prompted.
    *   **Expected Result:** Bot confirms successful registration and prompts to use `/login`.

*   **Test Case ID:** UM-002
    *   **Description:** Attempt to register with an already registered Telegram ID/email.
    *   **Steps:**
        1.  Repeat steps from UM-001 with an already registered user.
    *   **Expected Result:** Bot informs that the account already exists and suggests using `/login`.

*   **Test Case ID:** UM-003
    *   **Description:** Login with valid credentials.
    *   **Steps:**
        1.  Send `/login`.
        2.  Provide registered email when prompted.
        3.  Provide correct password when prompted.
    *   **Expected Result:** Bot confirms successful login.

*   **Test Case ID:** UM-004
    *   **Description:** Attempt to login with invalid credentials.
    *   **Steps:**
        1.  Send `/login`.
        2.  Provide incorrect email or password.
    *   **Expected Result:** Bot reports invalid credentials.

*   **Test Case ID:** UM-005
    *   **Description:** View user profile (`/profile`).
    *   **Steps:**
        1.  Send `/profile` (as a registered and logged-in user).
    *   **Expected Result:** Bot displays user's Telegram ID, username, email, balance, admin status, and registration date.

### 3.3. Service Management (User Side)

*   **Test Case ID:** SMU-001
    *   **Description:** View available services (`/services`).
    *   **Steps:**
        1.  Send `/services`.
    *   **Expected Result:** Bot lists all active services with their IDs, names, descriptions, and prices. Inline keyboard with 


buy buttons should be present.

*   **Test Case ID:** SMU-002
    *   **Description:** Purchase a service with sufficient credits.
    *   **Steps:**
        1.  Ensure user has sufficient credits (e.g., add credits via admin panel).
        2.  Send `/services`.
        3.  Click the 'Buy' button for a service.
    *   **Expected Result:** Bot confirms successful purchase, deducts credits, and provides order ID. New balance is displayed.

*   **Test Case ID:** SMU-003
    *   **Description:** Attempt to purchase a service with insufficient credits.
    *   **Steps:**
        1.  Ensure user has insufficient credits.
        2.  Send `/services`.
        3.  Click the 'Buy' button for a service.
    *   **Expected Result:** Bot informs about insufficient credits and suggests using `/addcredits`.

*   **Test Case ID:** SMU-004
    *   **Description:** View order history (`/myorders`).
    *   **Steps:**
        1.  Send `/myorders`.
    *   **Expected Result:** Bot displays a list of user's past orders, including ID, service name, status, date, device info (if any), and fulfillment details (if completed).

*   **Test Case ID:** SMU-005
    *   **Description:** Check credit balance (`/balance`).
    *   **Steps:**
        1.  Send `/balance`.
    *   **Expected Result:** Bot displays the user's current credit balance.

### 3.4. Payment Functionality (Mock)

*   **Test Case ID:** PF-001
    *   **Description:** Add credits successfully.
    *   **Steps:**
        1.  Send `/addcredits`.
        2.  Enter a positive amount (e.g., 10).
    *   **Expected Result:** Bot confirms credits added and displays new balance. A transaction record is created.

*   **Test Case ID:** PF-002
    *   **Description:** Attempt to add zero or negative credits.
    *   **Steps:**
        1.  Send `/addcredits`.
        2.  Enter 0 or a negative number.
    *   **Expected Result:** Bot prompts to enter a positive amount.

*   **Test Case ID:** PF-003
    *   **Description:** Attempt to add invalid credit amount (non-numeric).
    *   **Steps:**
        1.  Send `/addcredits`.
        2.  Enter non-numeric text.
    *   **Expected Result:** Bot prompts to enter a number.

### 3.5. Admin Panel Functionality

*   **Test Case ID:** AP-001
    *   **Description:** Access admin panel as an admin user.
    *   **Steps:**
        1.  Ensure the user's Telegram ID is in `ADMIN_USER_IDS` in `config.py`.
        2.  Send `/admin`.
    *   **Expected Result:** Bot displays the admin menu with options: Manage Users, Manage Services, Manage Orders, Broadcast Message, Cancel.

*   **Test Case ID:** AP-002
    *   **Description:** Attempt to access admin panel as a non-admin user.
    *   **Steps:**
        1.  Send `/admin` as a regular user.
    *   **Expected Result:** Bot replies with "You are not authorized to access the admin panel."

*   **Test Case ID:** AP-003
    *   **Description:** List all registered users (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Manage Users".
        3.  Select "List Users".
    *   **Expected Result:** Bot lists all registered users with their details (ID, username, email, balance, admin status).

*   **Test Case ID:** AP-004
    *   **Description:** Add a new service (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Manage Services".
        3.  Select "Add Service".
        4.  Provide service name, description, and price when prompted.
    *   **Expected Result:** Bot confirms service added with its ID.

*   **Test Case ID:** AP-005
    *   **Description:** Edit an existing service (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Manage Services".
        3.  Select "Edit Service".
        4.  Provide a valid service ID.
        5.  Select a field to edit (e.g., "price").
        6.  Provide the new value.
    *   **Expected Result:** Bot confirms service updated.

*   **Test Case ID:** AP-006
    *   **Description:** Delete a service (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Manage Services".
        3.  Select "Delete Service".
        4.  Provide a valid service ID.
    *   **Expected Result:** Bot confirms service deleted.

*   **Test Case ID:** AP-007
    *   **Description:** List all services (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Manage Services".
        3.  Select "List Services".
    *   **Expected Result:** Bot lists all services (active and inactive) with their details.

*   **Test Case ID:** AP-008
    *   **Description:** List pending orders (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Manage Orders".
        3.  Select "List Pending Orders".
    *   **Expected Result:** Bot lists all orders with "pending" status.

*   **Test Case ID:** AP-009
    *   **Description:** Fulfill a pending order (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Manage Orders".
        3.  Select "Fulfill Order".
        4.  Provide a valid pending Order ID.
        5.  Provide fulfillment details in JSON format (e.g., `{"type": "link", "link": "https://example.com/frp_solution"}`).
    *   **Expected Result:** Bot confirms order fulfilled, and the user who placed the order receives a message with fulfillment details. Order status is updated to "completed" in the database.

*   **Test Case ID:** AP-010
    *   **Description:** Broadcast a message to all users (Admin).
    *   **Steps:**
        1.  Access admin panel (`/admin`).
        2.  Select "Broadcast Message".
        3.  Enter the message to broadcast.
    *   **Expected Result:** Bot confirms message broadcasted, and all registered users receive the message.

## 4. Testing Procedure
1.  Set up the bot as per the `README.md` instructions.
2.  Run the bot.
3.  Execute each test case sequentially, verifying the expected results.
4.  Record actual results and any discrepancies.
5.  Report bugs or issues found.

## 5. Documentation
Comprehensive documentation will be created, including:
*   Setup instructions (`README.md`)
*   Usage guide for users
*   Admin guide
*   Code comments

## 6. Conclusion
This test plan aims to ensure the robustness and functionality of the GSM FRP Hosting Telegram Bot. Upon successful completion of these tests, the bot will be ready for deployment.

