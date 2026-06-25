# Smart Customer Support Chatbot Frontend

This is the **React + Vite frontend** for the Smart Customer Support Chatbot project.

The frontend provides a customer-facing CookieBot chat interface and an admin area for managing orders, products, dashboard statistics, and chat sessions. It connects to the FastAPI backend through REST API endpoints.

---

## Main Features

### Customer Features

- Home page
- CookieBot chat page
- Customer can view the cookie menu
- Customer can place cart-style orders through chat
- Customer can order multiple cookie types in one conversation
- Customer can confirm or cancel an order
- Customer can ask to order again and see the menu again
- Customer can say they are not interested and the bot responds politely
- Customer can later say they are interested and the bot presents the menu again
- Chat session support

### Admin Features

- Admin login page
- Protected admin dashboard routes
- Admin logout
- Dashboard summary cards
- Recent orders preview
- Popular products section
- Popular chatbot intents section
- Order management page
- Product management page
- Chat sessions page
- Product availability toggle
- Order status update from the frontend
- Chat history viewing
- Chat history deletion

---

## Tech Stack

- React
- Vite
- JavaScript
- React Router
- CSS
- Fetch API
- ESLint

---

## Frontend Folder Structure

```text
frontend/
│
├── src/
│   ├── components/
│   │   └── ProtectedRoute.jsx
│   │
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Chat.jsx
│   │   ├── AdminLogin.jsx
│   │   ├── AdminDashboard.jsx
│   │   ├── AdminOrders.jsx
│   │   ├── AdminProducts.jsx
│   │   └── AdminChats.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
│
├── .env.example
├── package.json
├── vite.config.js
└── README.md
```

---

## Requirements

Before running the frontend, install:

- Node.js
- npm

Check your versions:

```powershell
node -v
npm -v
```

---

## Important: Start the Backend First

The frontend depends on the FastAPI backend.

Start the backend first from the main project folder:

```powershell
cd backend
.venv\Scripts\activate
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

---

## How to Run the Frontend

Open a second terminal in the main project folder.

```powershell
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:5173
```

Keep both the backend and frontend terminals running.

---

## Environment Variable

The frontend uses this backend API URL by default:

```text
http://127.0.0.1:8000
```

If you want to customise it, create a `.env` file inside the `frontend` folder.

You can copy the example file:

```powershell
copy .env.example .env
```

Then set:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

After changing `.env`, restart the frontend server:

```powershell
npm run dev
```

---

## Frontend Routes

### Public Routes

```text
/
```

Home page.

```text
/chat
```

Customer CookieBot chat page.

### Admin Routes

```text
/admin/login
```

Admin login page.

```text
/admin
```

Admin dashboard.

```text
/admin/orders
```

Admin order management page.

```text
/admin/products
```

Admin product management page.

```text
/admin/chats
```

Admin chat sessions page.

---

## Admin Login

Default local development login:

```text
Username: admin
Password: Admin123!
```

After logging in, the frontend saves the admin token locally and sends it with protected admin API requests.

Admin pages are protected. If you try to open an admin page without logging in, you will be redirected to:

```text
/admin/login
```

Use the logout button to end the admin session.

---

## Admin Dashboard

The admin dashboard shows:

- Total revenue
- Total orders
- Pending orders
- Confirmed orders
- Completed orders
- Total chat messages
- Total products
- Available products
- Recent orders
- Popular products
- Popular chatbot intents

---

## Admin Orders Page

The orders page allows the admin to:

- View all orders
- Search orders
- Filter orders by status
- View customer details
- View delivery method
- View order items
- View order totals
- Update order status

Supported order statuses:

```text
pending
confirmed
preparing
out_for_delivery
completed
cancelled
```

---

## Admin Products Page

The products page allows the admin to:

- View all products
- Search products
- Add a new product
- Edit product name
- Edit product description
- Edit product price
- Show or hide products

Hidden products are not shown as available products to the customer chatbot.

---

## Admin Chat Sessions Page

The chat sessions page allows the admin to:

- View recent chat sessions
- Open a session's chat history
- Review customer and bot messages
- Delete a chat session history

---

## CookieBot Conversation Behaviour

The chat page supports customer messages such as:

```text
hello
what do you sell?
i want to buy cookies
how much is chocolate chip?
I want 2 chocolate chip and 1 macaron
I want two sugar cookies
confirm
cancel
i would like to order again
I am not interested
I am interested
please I like to order cookies
thank you
bye
```

Expected chatbot behaviour includes:

- If the user says they want to buy cookies, the bot shows the menu.
- If the user orders specific cookies, the bot adds them to a pending cart.
- If the user confirms, the bot confirms the full order.
- If the user says they want to order again, the bot shows the menu again.
- If the user says they are not interested, the bot politely pauses.
- If the user later says they are interested, the bot shows the menu again.

---

## Useful Commands

Run the development server:

```powershell
npm run dev
```

Run ESLint:

```powershell
npm run lint
```

Create a production build:

```powershell
npm run build
```

Preview the production build locally:

```powershell
npm run preview
```

---

## Quality Checks

Before submitting or uploading the project, run:

```powershell
npm run lint
npm run build
```

Both commands should complete successfully.

---

## Troubleshooting

### 1. Frontend opens but chatbot does not reply

Make sure the backend is running:

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

Then refresh the frontend.

---

### 2. Admin dashboard says unauthorised

Go to:

```text
http://localhost:5173/admin/login
```

Log in again using the admin account.

---

### 3. Changes in `.env` are not working

Restart the Vite server:

```powershell
CTRL + C
npm run dev
```

---

### 4. Port 5173 is already in use

Vite may start on another port, such as:

```text
http://localhost:5174
```

Use the URL shown in the terminal.

---

### 5. CORS error in the browser console

Make sure the backend allows the frontend URL.

For local development, the frontend usually runs at:

```text
http://localhost:5173
```

The backend should include that URL in its CORS settings.

---

## Build Output

When you run:

```powershell
npm run build
```

Vite creates a production-ready folder:

```text
frontend/dist/
```

The `dist` folder should not be committed to GitHub unless you have a specific reason to include it.

---

## Frontend Summary for CV

Built a React and Vite frontend for a smart customer support chatbot, including a customer chat interface, protected admin login, dashboard analytics, order management, product management, and chat history review connected to a FastAPI backend.
