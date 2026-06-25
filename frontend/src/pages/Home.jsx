import { Link } from "react-router-dom";
import { API_BASE_URL } from "../services/api";

function Home() {
  return (
    <main className="home-page">
      <section className="hero-section">
        <div>
          <p className="eyebrow">Smart Customer Support Chatbot</p>

          <h1>CookieBot Customer Support Assistant</h1>

          <p className="hero-text">
            A full-stack customer support chatbot that helps customers ask about
            cookie products, prices, delivery, opening hours, and cart-style
            orders while giving admins a dashboard to manage the shop.
          </p>

          <div className="hero-actions">
            <Link to="/chat" className="primary-link">
              Start Chatting
            </Link>

            <Link to="/admin" className="secondary-link">
              Admin Login
            </Link>

            <a
              href={`${API_BASE_URL}/docs`}
              target="_blank"
              rel="noreferrer"
              className="secondary-link"
            >
              View Backend API
            </a>
          </div>
        </div>

        <div className="hero-card">
          <h2>Project Features</h2>

          <ul>
            <li>Rule-based chatbot responses</li>
            <li>Product-specific price replies</li>
            <li>Cart-style multi-item orders</li>
            <li>Order confirmation and cancellation</li>
            <li>Protected admin dashboard with live stats</li>
            <li>Order status and product management</li>
          </ul>
        </div>
      </section>
    </main>
  );
}

export default Home;
