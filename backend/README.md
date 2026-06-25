# Smart Customer Support Chatbot Backend

This is the FastAPI backend for the Smart Customer Support Chatbot project. It provides chatbot responses, database-driven product detection, cart-style order management, customer/delivery details, chat history, dashboard summary data, admin authentication, and deployment-ready database configuration.

## Technologies Used

- Python
- FastAPI
- SQLite
- PostgreSQL support
- SQLAlchemy
- Pydantic
- Uvicorn
- Signed bearer-token admin authentication
- Pytest backend test suite
- HTTPX/FastAPI TestClient endpoint testing
- Docker deployment support

## Backend Folder Structure

```text
backend/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── migrations.py
│   ├── seed.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   └── data/
│
├── tests/
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## How to Run the Backend

Open a terminal inside the project folder:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

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


## Run Backend Tests

After installing the backend requirements, run:

```powershell
pytest
```

The tests use a separate SQLite database at `backend/tests/test_chatbot.db`, which is reset before each test. The file is ignored by Git.

The Stage 6 test suite covers:

- public health/product endpoints
- admin login and bearer-token protection
- product create/update validation
- chatbot order flow
- manual order API
- order status updates
- dashboard summary data
- chat history and recent sessions

## Environment Variables

The backend works locally without a `.env` file. To customise settings, copy the example file:

```powershell
copy .env.example .env
```

Available settings:

```env
DATABASE_URL=sqlite:///./chatbot.db
# DATABASE_URL=postgresql://cookiebot_user:cookiebot_password@localhost:5432/cookiebot_db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin123!
ADMIN_SECRET_KEY=replace-this-with-a-long-random-secret-key
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES=120
```


## Deployment Preparation

The backend is now ready for deployment with either Docker or a Python hosting platform.

Deployment files added for the backend:

```text
backend/Dockerfile
backend/.dockerignore
```

The backend also supports PostgreSQL through `DATABASE_URL`.

Example PostgreSQL URL:

```env
DATABASE_URL=postgresql://cookiebot_user:cookiebot_password@localhost:5432/cookiebot_db
```

### Docker backend build

From the main project folder:

```powershell
docker build -t cookiebot-backend ./backend
```

### Docker backend run

```powershell
docker run -p 8000:8000 --env-file backend/.env cookiebot-backend
```

### Production backend start command

For a hosting provider that runs Python directly, use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If the hosting provider does not set `$PORT`, use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Important production settings

Before public deployment, change these values:

```env
ADMIN_PASSWORD=replace-with-a-strong-admin-password
ADMIN_SECRET_KEY=replace-with-a-long-random-secret-key
CORS_ORIGINS=https://your-frontend-domain.com
DATABASE_URL=postgresql://user:password@host:5432/database_name
```

Do not deploy publicly with the local default admin password.

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/api/info` | Project info |
| POST | `/api/chat/` | Send chatbot message and manage the pending order cart |
| POST | `/api/auth/login` | Admin login and token creation |
| GET | `/api/auth/me` | Current admin profile, protected |
| POST | `/api/auth/logout` | Admin logout helper, protected |
| GET | `/api/chat/history/{session_id}` | Get chat history, protected |
| DELETE | `/api/chat/history/{session_id}` | Delete chat history, protected |
| GET | `/api/chat/sessions/recent` | Recent chat sessions, protected |
| POST | `/api/products/` | Create product, protected |
| GET | `/api/products/` | Product list |
| PATCH | `/api/products/{product_id}` | Update product details or availability, protected |
| POST | `/api/orders/` | Create a manual order with multiple order items, protected |
| GET | `/api/orders/` | Order list with nested items, protected |
| GET | `/api/orders/session/{session_id}` | Get orders by session, protected |
| GET | `/api/orders/{order_id}` | Get one order, protected |
| PATCH | `/api/orders/{order_id}/status` | Update order status, protected |
| PATCH | `/api/orders/{order_id}/customer` | Update customer and delivery details, protected |
| GET | `/api/dashboard/summary` | Dashboard summary, protected |

## Stage 3 Order System

The backend now uses a professional cart-style order structure.

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

This allows one order to contain many items.

Example chatbot message:

```text
I want 2 chocolate chip and 1 macaron
```

The backend now saves this as one pending order with two order items.

## Customer and Delivery Details

The chatbot can update the pending order when the user sends details like:

```text
my name is Tyrone and my phone is 08012345678
I want delivery to 12 Test Street
pickup please
```

The API also supports direct updates through:

```text
PATCH /api/orders/{order_id}/customer
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

## Notes

The project currently creates tables automatically on startup. A lightweight migration helper is included in `app/migrations.py` so older local Stage 1/Stage 2 SQLite databases can receive the new Stage 3 order fields.


## Stage 4 Backend Support

Stage 4 adds a small backend improvement for the admin product page:

```text
PATCH /api/products/{product_id}
```

This endpoint lets the frontend update product name, description, price, and availability. The chatbot only uses products marked as available, so the admin can hide products from the customer menu without deleting old order history.


## Stage 5 Admin Authentication

Stage 5 adds an `admin_users` table and protects admin-only backend routes with signed bearer tokens.

Public endpoints still include customer chat and product viewing. Protected endpoints include dashboard summary, orders, product create/update, and admin chat history tools.

Default local admin:

```text
Username: admin
Password: Admin123!
```

Login endpoint:

```text
POST /api/auth/login
```

Example login body:

```json
{
  "username": "admin",
  "password": "Admin123!"
}
```

The response includes an `access_token`. Use it as a bearer token when calling protected admin endpoints.

## Stage 6 Testing and Quality Improvements

Stage 6 adds automated backend testing and removes code-quality warnings from the current FastAPI/Pydantic setup.

Added files:

```text
backend/pytest.ini
backend/tests/conftest.py
backend/tests/test_public_endpoints.py
backend/tests/test_auth_and_protection.py
backend/tests/test_products_api.py
backend/tests/test_chatbot_orders.py
backend/tests/test_orders_api.py
backend/tests/test_dashboard_and_chat_history.py
```

Quality improvements:

- Pydantic response schemas now use `ConfigDict(from_attributes=True)`
- SQLAlchemy timestamp defaults now use timezone-aware UTC helpers
- Backend tests reset the database before every test
- Protected admin endpoints are tested with and without valid tokens
- Chatbot order, confirmation, cancellation, and customer-detail flows are tested



## Latest chatbot behavior fix

When a customer confirms an order and then types `I would like to order again`, CookieBot now shows the menu again and asks what cookies they would like to order next instead of giving a fallback reply.


## Latest chatbot behavior fix

CookieBot now understands interest changes more naturally:

- If the customer says `I am not interested` or `I am not interested in cookies`, CookieBot replies: `Ok, please let me know when you are interested.`
- If the customer later says `I am interested`, `I am intrested`, `please I like to order cookies`, or a similar order request, CookieBot shows the menu again and asks what cookies they would like to buy.
- The typo `intrested` is supported as well as the correct spelling `interested`.


## Stage 7 Deployment Improvements

Stage 7 added:

- PostgreSQL-ready database configuration
- `psycopg2-binary` dependency for PostgreSQL connections
- Dockerfile for the backend
- Docker Compose support at the project root
- Production environment variable examples
- Deployment documentation
- Database URL compatibility for providers that use `postgres://` URLs
