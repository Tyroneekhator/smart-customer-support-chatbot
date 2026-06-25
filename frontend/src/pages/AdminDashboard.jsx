import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { API_BASE_URL, getDashboardSummary } from "../services/api";

function currency(value) {
  return `£${Number(value || 0).toFixed(2)}`;
}

function formatDate(value) {
  if (!value) {
    return "Not available";
  }

  return new Date(value).toLocaleString();
}

function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    setIsLoading(true);
    setError("");

    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let shouldIgnore = false;

    async function loadInitialDashboard() {
      try {
        const data = await getDashboardSummary();

        if (!shouldIgnore) {
          setSummary(data);
        }
      } catch (caughtError) {
        if (!shouldIgnore) {
          setError(caughtError.message);
        }
      } finally {
        if (!shouldIgnore) {
          setIsLoading(false);
        }
      }
    }

    loadInitialDashboard();

    return () => {
      shouldIgnore = true;
    };
  }, []);

  if (isLoading) {
    return (
      <main className="admin-page">
        <p className="status-message">Loading admin dashboard...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="admin-page">
        <div className="error-box">
          <h1>Admin Dashboard</h1>
          <p>{error}</p>
          <button type="button" onClick={loadDashboard}>
            Try Again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="admin-page">
      <section className="admin-header">
        <div>
          <p className="eyebrow">Admin Area</p>
          <h1>Dashboard Overview</h1>
          <p>
            Monitor orders, revenue, product activity, and chatbot usage from
            one place.
          </p>
        </div>

        <div className="admin-actions">
          <button type="button" onClick={loadDashboard}>
            Refresh
          </button>
          <Link to="/admin/orders">Manage Orders</Link>
          <Link to="/admin/products">Manage Products</Link>
        </div>
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <span>Total Revenue</span>
          <strong>{currency(summary.total_revenue)}</strong>
        </article>
        <article className="stat-card">
          <span>Total Orders</span>
          <strong>{summary.total_orders}</strong>
        </article>
        <article className="stat-card">
          <span>Pending Orders</span>
          <strong>{summary.pending_orders}</strong>
        </article>
        <article className="stat-card">
          <span>Confirmed Orders</span>
          <strong>{summary.confirmed_orders}</strong>
        </article>
        <article className="stat-card">
          <span>Completed Orders</span>
          <strong>{summary.completed_orders}</strong>
        </article>
        <article className="stat-card">
          <span>Chat Messages</span>
          <strong>{summary.total_messages}</strong>
        </article>
        <article className="stat-card">
          <span>Products</span>
          <strong>{summary.total_products}</strong>
        </article>
        <article className="stat-card">
          <span>Available Products</span>
          <strong>{summary.available_products}</strong>
        </article>
      </section>

      <section className="admin-grid-two">
        <article className="admin-panel">
          <div className="panel-title-row">
            <h2>Recent Orders</h2>
            <Link to="/admin/orders">View all</Link>
          </div>

          {summary.recent_orders.length === 0 ? (
            <p className="muted-text">No orders yet.</p>
          ) : (
            <div className="stacked-list">
              {summary.recent_orders.map((order) => (
                <div key={order.id} className="mini-card">
                  <div className="mini-card-header">
                    <strong>Order #{order.id}</strong>
                    <span className={`status-pill status-${order.status}`}>
                      {order.status.replaceAll("_", " ")}
                    </span>
                  </div>
                  <p>
                    {order.customer_name || "Customer not provided"} · {" "}
                    {order.delivery_method || "pickup"} · {currency(order.total_price)}
                  </p>
                  <ul>
                    {order.items.map((item) => (
                      <li key={`${order.id}-${item.product_name}`}>
                        {item.quantity} × {item.product_name}
                      </li>
                    ))}
                  </ul>
                  <small>{formatDate(order.created_at)}</small>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="admin-panel">
          <h2>Popular Products</h2>

          {summary.popular_products.length === 0 ? (
            <p className="muted-text">No product sales yet.</p>
          ) : (
            <div className="table-wrapper compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Qty</th>
                    <th>Sales</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.popular_products.map((product) => (
                    <tr key={product.product_name}>
                      <td>{product.product_name}</td>
                      <td>{product.total_quantity}</td>
                      <td>{currency(product.total_sales)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </article>
      </section>

      <section className="admin-grid-two">
        <article className="admin-panel">
          <h2>Popular Chat Intents</h2>

          {summary.popular_intents.length === 0 ? (
            <p className="muted-text">No intent data yet.</p>
          ) : (
            <div className="tag-list">
              {summary.popular_intents.map((intent) => (
                <span key={intent.intent}>
                  {intent.intent}: {intent.count}
                </span>
              ))}
            </div>
          )}
        </article>

        <article className="admin-panel">
          <h2>Admin Shortcuts</h2>
          <div className="shortcut-list">
            <Link to="/admin/orders">Update order statuses</Link>
            <Link to="/admin/products">Add or edit products</Link>
            <Link to="/admin/chats">Review recent chat sessions</Link>
            <a href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer">
              Open Swagger API docs
            </a>
          </div>
        </article>
      </section>
    </main>
  );
}

export default AdminDashboard;
