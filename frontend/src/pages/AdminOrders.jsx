import { useEffect, useMemo, useState } from "react";
import { getOrders, updateOrderStatus } from "../services/api";

const ORDER_STATUSES = [
  "pending",
  "confirmed",
  "preparing",
  "out_for_delivery",
  "completed",
  "cancelled",
];

function currency(value) {
  return `£${Number(value || 0).toFixed(2)}`;
}

function formatDate(value) {
  if (!value) {
    return "Not available";
  }

  return new Date(value).toLocaleString();
}

function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [updatingOrderId, setUpdatingOrderId] = useState(null);

  async function loadOrders() {
    setIsLoading(true);
    setError("");

    try {
      const data = await getOrders();
      setOrders(data);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let shouldIgnore = false;

    async function loadInitialOrders() {
      try {
        const data = await getOrders();

        if (!shouldIgnore) {
          setOrders(data);
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

    loadInitialOrders();

    return () => {
      shouldIgnore = true;
    };
  }, []);

  const filteredOrders = useMemo(() => {
    const cleanedSearch = searchTerm.toLowerCase().trim();

    return orders.filter((order) => {
      const matchesStatus = statusFilter === "all" || order.status === statusFilter;
      const searchableText = [
        order.id,
        order.session_id,
        order.customer_name,
        order.customer_email,
        order.customer_phone,
        order.delivery_method,
        order.delivery_address,
        order.notes,
        ...order.items.map((item) => item.product_name),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch = !cleanedSearch || searchableText.includes(cleanedSearch);
      return matchesStatus && matchesSearch;
    });
  }, [orders, searchTerm, statusFilter]);

  async function handleStatusChange(orderId, status) {
    setUpdatingOrderId(orderId);
    setError("");
    setSuccess("");

    try {
      const updatedOrder = await updateOrderStatus(orderId, status);
      setOrders((previousOrders) =>
        previousOrders.map((order) =>
          order.id === orderId ? updatedOrder : order,
        ),
      );
      setSuccess(`Order #${orderId} status updated to ${status.replaceAll("_", " ")}.`);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setUpdatingOrderId(null);
    }
  }

  return (
    <main className="admin-page">
      <section className="admin-header">
        <div>
          <p className="eyebrow">Admin Area</p>
          <h1>Order Management</h1>
          <p>View customer orders, filter them, and update their progress.</p>
        </div>

        <div className="admin-actions">
          <button type="button" onClick={loadOrders}>
            Refresh Orders
          </button>
        </div>
      </section>

      <section className="admin-panel">
        <div className="filter-row">
          <label>
            Search orders
            <input
              type="search"
              placeholder="Search by customer, phone, product, or order ID"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </label>

          <label>
            Status filter
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value="all">All statuses</option>
              {ORDER_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </label>
        </div>

        {error && <p className="error-text">{error}</p>}
        {success && <p className="success-text">{success}</p>}

        {isLoading ? (
          <p className="status-message">Loading orders...</p>
        ) : filteredOrders.length === 0 ? (
          <p className="muted-text">No orders match your current filters.</p>
        ) : (
          <div className="orders-list">
            {filteredOrders.map((order) => (
              <article key={order.id} className="order-card">
                <div className="order-card-header">
                  <div>
                    <h2>Order #{order.id}</h2>
                    <p>
                      {order.customer_name || "Customer not provided"} · {" "}
                      {order.delivery_method || "pickup"}
                    </p>
                  </div>

                  <span className={`status-pill status-${order.status}`}>
                    {order.status.replaceAll("_", " ")}
                  </span>
                </div>

                <div className="order-meta-grid">
                  <span>
                    <strong>Total:</strong> {currency(order.total_price)}
                  </span>
                  <span>
                    <strong>Phone:</strong> {order.customer_phone || "Not provided"}
                  </span>
                  <span>
                    <strong>Email:</strong> {order.customer_email || "Not provided"}
                  </span>
                  <span>
                    <strong>Created:</strong> {formatDate(order.created_at)}
                  </span>
                </div>

                {order.delivery_address && (
                  <p className="order-address">
                    <strong>Address:</strong> {order.delivery_address}
                  </p>
                )}

                {order.notes && (
                  <p className="order-address">
                    <strong>Notes:</strong> {order.notes}
                  </p>
                )}

                <div className="table-wrapper compact-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {order.items.map((item) => (
                        <tr key={item.id}>
                          <td>{item.product_name}</td>
                          <td>{item.quantity}</td>
                          <td>{currency(item.unit_price)}</td>
                          <td>{currency(item.line_total)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="order-actions-row">
                  <label>
                    Update status
                    <select
                      value={order.status}
                      disabled={updatingOrderId === order.id}
                      onChange={(event) => handleStatusChange(order.id, event.target.value)}
                    >
                      {ORDER_STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {status.replaceAll("_", " ")}
                        </option>
                      ))}
                    </select>
                  </label>

                  <small>Session: {order.session_id}</small>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default AdminOrders;
