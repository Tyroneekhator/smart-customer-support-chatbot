import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import AdminDashboard from "./pages/AdminDashboard";
import AdminOrders from "./pages/AdminOrders";
import AdminProducts from "./pages/AdminProducts";
import AdminChats from "./pages/AdminChats";

function App() {
  return (
    <div className="app">
      <nav className="navbar">
        <Link to="/" className="logo">
          CookieBot
        </Link>

        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/chat">Chat</Link>
          <Link to="/admin">Admin</Link>
          <Link to="/admin/orders">Orders</Link>
          <Link to="/admin/products">Products</Link>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/orders" element={<AdminOrders />} />
        <Route path="/admin/products" element={<AdminProducts />} />
        <Route path="/admin/chats" element={<AdminChats />} />
      </Routes>
    </div>
  );
}

export default App;
