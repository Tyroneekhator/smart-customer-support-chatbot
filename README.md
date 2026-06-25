# Smart Customer Support Chatbot

A full-stack customer support chatbot for a cookie shop. The project uses a **FastAPI backend**, **SQLite database**, **React/Vite frontend**, admin authentication, cart-style orders, chat history, product management, dashboard reporting, and automated backend tests.

The chatbot, called **CookieBot**, can answer customer questions, show the cookie menu, detect products and quantities, handle multi-item orders, save customer and delivery details, confirm or cancel orders, and guide customers when they want to order again.

## Project Demo

Watch the demo video here:

[Watch Demo Video](https://drive.google.com/file/d/1B9Z7DNIH85Z_q9rMXUWAWN0j3wvgzgIY/view?usp=sharing)

## Current Features

### Customer Chatbot Features

- Friendly CookieBot customer chat interface
- Database-driven cookie menu
- Product price replies using live database prices
- Product spelling and alias support
- Better quantity detection using digits and number words
- Multi-item order detection in one message
- Cart-style pending order per chat session
- Order confirmation
- Order cancellation
- Pickup and delivery method support
- Customer name, phone, email, and delivery address saving
- Session-based chat history
- Clear chat option
- Helpful fallback replies
- Menu shown when the customer says they want to buy cookies
- Menu shown again when the customer wants to order again
- Polite response when the customer is not interested
- Menu shown again when the customer later says they are interested

### Admin Features

- Admin login page
- Protected admin frontend routes
- JWT-style signed bearer token authentication
- Admin logout
- Admin dashboard
- Admin order management
- Admin product management
- Admin chat session viewing
- Admin chat history deletion
- Protected backend admin endpoints

### Backend Features

- FastAPI backend
- SQLite database
- SQLAlchemy models
- Pydantic schemas
- Product API
- Order API
- Chat API
- Dashboard API
- Auth API
- Swagger API documentation
- Lightweight local database migration helper
- Automated backend tests with pytest

### Frontend Features

- React/Vite frontend
- React Router navigation
- Home page
- Chat page
- Admin login page
- Admin dashboard page
- Admin orders page
- Admin products page
- Admin chats page
- Protected admin routes
- Responsive CSS styling

## Tech Stack

### Backend

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Uvicorn
- Pytest
- HTTPX

### Frontend

- React
- Vite
- JavaScript
- CSS
- React Router
- ESLint

## Project Structure

```text
smart-customer-support-chatbot-main/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── migrations.py
│   │   ├── seed.py
│   │   ├── data/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth_and_protection.py
│   │   ├── test_chatbot_orders.py
│   │   ├── test_dashboard_and_chat_history.py
│   │   ├── test_orders_api.py
│   │   ├── test_products_api.py
│   │   └── test_public_endpoints.py
│   │
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ProtectedRoute.jsx
│   │   ├── pages/
│   │   │   ├── AdminChats.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── AdminLogin.jsx
│   │   │   ├── AdminOrders.jsx
│   │   │   ├── AdminProducts.jsx
│   │   │   ├── Chat.jsx
│   │   │   └── Home.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── .env.example
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

## Requirements

Install these before running the project:

- Python 3.10 or newer
- Node.js 18 or newer
- npm
- VS Code or another code editor

## How to Run the Project

You need two terminals:

- Terminal 1: backend
- Terminal 2: frontend

Keep both terminals running while using the project.

## 1. Run the Backend

Open PowerShell or the VS Code terminal inside the project folder.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 2. Run the Frontend

Open a second PowerShell or VS Code terminal inside the project folder.

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Main Pages

| Page | URL | Description |
|---|---|---|
| Home | `http://localhost:5173` | Landing page |
| Chat | `http://localhost:5173/chat` | Customer CookieBot chat page |
| Admin Login | `http://localhost:5173/admin/login` | Admin login page |
| Admin Dashboard | `http://localhost:5173/admin` | Protected dashboard summary |
| Admin Orders | `http://localhost:5173/admin/orders` | Protected order management page |
| Admin Products | `http://localhost:5173/admin/products` | Protected product management page |
| Admin Chats | `http://localhost:5173/admin/chats` | Protected chat history page |

## Admin Login

For local development, the default admin account is:

```text
Username: admin
Password: Admin123!
```

After logging in, the admin can access:

```text
/admin
/admin/orders
/admin/products
/admin/chats
```

If a user tries to open an admin page without logging in, they are redirected to:

```text
/admin/login
```

## Important Security Note

The default admin account is only for local development.

Before deploying the project, create a backend `.env` file and change the admin details:

```powershell
copy backend\.env.example backend\.env
```

Example values:

```env
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=choose-a-strong-password
ADMIN_SECRET_KEY=replace-this-with-a-long-random-secret-key
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## Environment Files

Example environment files are included:

```text
backend/.env.example
frontend/.env.example
```

For local development, the project can run without manually creating `.env` files.

To customise settings, copy the example files:

```powershell
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

## Main API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Checks if the API is running |
| GET | `/health` | Health check endpoint |
| GET | `/api/info` | Shows project information |
| POST | `/api/chat/` | Sends a message to CookieBot |
| GET | `/api/products/` | Gets all public products |
| GET | `/api/products/search/{product_name}` | Searches for a product |

### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Logs in an admin user |
| GET | `/api/auth/me` | Gets the current logged-in admin |

### Protected Admin Endpoints

These endpoints require an admin bearer token.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/summary` | Gets dashboard summary data |
| GET | `/api/orders/` | Gets all orders with their items |
| POST | `/api/orders/` | Creates a manual order with order items |
| GET | `/api/orders/session/{session_id}` | Gets orders by chat session |
| GET | `/api/orders/{order_id}` | Gets one order with its items |
| PATCH | `/api/orders/{order_id}/status` | Updates an order status |
| PATCH | `/api/orders/{order_id}/customer` | Updates customer and delivery details |
| POST | `/api/products/` | Creates a product |
| PATCH | `/api/products/{product_id}` | Updates product details or availability |
| GET | `/api/chat/history/{session_id}` | Gets chat history for a session |
| DELETE | `/api/chat/history/{session_id}` | Deletes chat history for a session |
| GET | `/api/chat/sessions/recent` | Gets recent chat sessions |

## Example Chat Messages

Try these messages in the chat page:

```text
hello
what do you sell?
show me the menu
i want to buy cookies
how much are your cookies?
how much is chocolate chip?
are you open today?
do you deliver?
where are you located?
I want two sugar cookies
Can I order 3 macarons?
I want 2 chocolate chip and 1 macaron
I want 2 choclate chip
add 1 shortbread
my name is Tyrone and my phone is 08012345678
I want delivery to 12 Test Street
pickup please
confirm
cancel
thank you
i would like to order again
new order
I am not interested
I am not intrested in cookies
I am interested
please I like to order cookies
bye
```

## Latest CookieBot Conversation Behaviour

### Customer wants to buy cookies

If the user says:

```text
i want to buy cookies
```

CookieBot shows the menu and asks which cookies the customer wants to buy.

### Customer confirms an order

If the customer confirms a pending cart, CookieBot confirms the full order, shows the ordered items, total price, saved details, and thanks the customer.

### Customer wants to order again

If the user says:

```text
i would like to order again
```

CookieBot shows the menu again and asks what cookies they would like to order this time.

Supported similar phrases include:

```text
order again
new order
another order
place another order
buy again
buy more
order more
```

### Customer is not interested

If the user says:

```text
I am not interested
```

or:

```text
I am not intrested in cookies
```

CookieBot replies:

```text
Ok, please let me know when you are interested.
```

### Customer becomes interested later

If the user later says:

```text
I am interested
```

or:

```text
please I like to order cookies
```

CookieBot shows the menu again.

## Stage 3 Order System

The order system uses a cart-style order design.

The project now uses:

```text
orders
- id
- session_id
- status
- customer_name
- customer_email
- customer_phone
- delivery_method
- delivery_address
- notes
- subtotal
- total_price
- created_at
- updated_at

order_items
- id
- order_id
- product_id
- product_name
- quantity
- unit_price
- line_total
- created_at
```

This means one customer order can contain many products.

Example:

```text
Order #1
- 2 Chocolate Chip Cookies
- 1 Macaron Cookie
Total: £6.50
```

## Order Statuses

Supported statuses:

```text
pending
confirmed
preparing
out_for_delivery
completed
cancelled
```

## Example Manual Order API Body

You can test this in Swagger at `/docs` using `POST /api/orders/`.

Because this endpoint is protected, log in first using `/api/auth/login`, then click **Authorize** in Swagger and paste the bearer token.

```json
{
  "session_id": "manual-test-session",
  "items": [
    {
      "product_name": "Chocolate Chip Cookie",
      "quantity": 2
    },
    {
      "product_name": "Macaron Cookie",
      "quantity": 1
    }
  ],
  "customer_name": "Tyrone",
  "customer_phone": "08012345678",
  "delivery_method": "delivery",
  "delivery_address": "12 Test Street"
}
```

## Database

The backend uses SQLite for local development.

The database file is created automatically when the backend runs.

Main database tables:

- `products`
- `chat_messages`
- `orders`
- `order_items`
- `admin_users`

A lightweight migration helper is included in:

```text
backend/app/migrations.py
```

It helps older local databases work with the newer order and admin fields.

## Run Backend Tests

From the backend folder:

```powershell
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

The Stage 6 test suite covers:

- public endpoints
- admin login
- protected routes
- product creation and updates
- duplicate product validation
- chatbot multi-item orders
- chatbot order confirmation
- chatbot order cancellation
- customer detail saving
- manual admin orders
- order status updates
- dashboard totals
- recent chat sessions
- chat history viewing
- chat history deletion
- interested and not interested chatbot replies
- order again chatbot behaviour
- buy cookies menu behaviour

## Run Frontend Quality Checks

From the frontend folder:

```powershell
cd frontend
npm install
npm run lint
npm run build
```

Use these before submitting or uploading the project.

## Stage 1 Cleanup Completed

- Added a proper root `.gitignore`
- Converted `backend/requirements.txt` to normal UTF-8 text
- Simplified backend dependencies
- Added `backend/.env.example`
- Added `frontend/.env.example`
- Moved product seed data into `backend/app/seed.py`
- Cleaned `backend/app/main.py`
- Made the database URL configurable
- Replaced the default frontend README
- Removed unused Vite starter assets

## Stage 2 Chatbot Logic Improvements Completed

- Chatbot reads available products from the database
- New products added through the product API can be detected by the chatbot
- Product aliases are generated automatically from product names
- Common aliases such as `choc chip`, `macaron`, `macaroon`, `gingerbread`, and `oatmeal` are supported
- Simple spelling mistakes such as `choclate chip` can still be understood
- Quantity detection supports digits and number words
- One message can detect multiple requested products
- Menu and price replies use live database product information

## Stage 3 Order System Improvements Completed

- Added `OrderItem` model
- Updated `Order` model with customer and delivery fields
- Added order totals: `subtotal` and `total_price`
- Chatbot now adds items to one pending cart/order per session
- Repeated products are merged by increasing quantity
- Confirming an order confirms the full cart
- Cancelling an order cancels the full cart
- Added customer/delivery update support
- Added `PATCH /api/orders/{order_id}/customer`
- Updated dashboard summary with revenue, pending orders, confirmed orders, cancelled orders, completed orders, and popular products

## Stage 4 Admin Dashboard Frontend Completed

- Added `/admin`
- Added `/admin/orders`
- Added `/admin/products`
- Added `/admin/chats`
- Dashboard shows revenue, order totals, product totals, popular products, recent orders, and popular intents
- Orders page supports searching, filtering, viewing order items, and updating order status
- Products page supports adding, editing, searching, and hiding/showing products
- Chats page supports viewing recent chat sessions, opening chat history, and deleting chat history

## Stage 5 Admin Login and Protected Routes Completed

- Added admin login page
- Added admin logout
- Added signed bearer-token authentication
- Added admin user database table
- Added default local admin seeding
- Protected admin frontend routes
- Protected admin backend endpoints
- Customer chatbot remains public

## Stage 6 Testing and Quality Improvements Completed

- Added pytest backend test suite
- Added tests for public endpoints
- Added tests for auth and protected routes
- Added tests for products API
- Added tests for chatbot orders
- Added tests for orders API
- Added tests for dashboard and chat history
- Updated frontend lint/build checks
- Fixed React Hooks lint issue in admin pages
- Added tests for latest CookieBot conversation behaviours

## Recommended Next Improvements

- Stage 7: Prepare deployment with PostgreSQL and Docker
- Add password reset or admin password change screen
- Add pagination for orders and chat sessions
- Add order receipt download or email confirmation
- Add customer order tracking page
- Add product image upload
- Add analytics charts to the admin dashboard

## Troubleshooting

### Backend does not start

Make sure the virtual environment is activated:

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend cannot connect to backend

Make sure the backend is running at:

```text
http://127.0.0.1:8000
```

Then restart the frontend:

```powershell
cd frontend
npm run dev
```

### Admin page redirects to login

This is expected if you are not logged in.

Go to:

```text
http://localhost:5173/admin/login
```

Then log in with the local development admin account.

### Protected endpoint returns 401

Log in first through `/api/auth/login`, then send the token as a bearer token.

In Swagger, click **Authorize** and paste the token.

### Database looks outdated

The project includes a lightweight migration helper.

If you are still having local development database issues and you do not need old data, stop the backend and delete the local SQLite database file, then restart the backend so it can recreate the database.

## CV Summary

Built a full-stack customer support chatbot using React, FastAPI, and SQLite, featuring a database-driven cookie menu, rule-based product and quantity detection, cart-style multi-item orders, customer delivery details, admin authentication, protected dashboard pages, product/order management, chat history, and automated backend testing.
