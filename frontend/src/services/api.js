const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let errorMessage = "Request failed.";

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = `${response.status} ${response.statusText}`;
    }

    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export async function sendChatMessage(message, sessionId) {
  return request("/api/chat/", {
    method: "POST",
    body: JSON.stringify({
      message: message,
      session_id: sessionId || "",
    }),
  });
}

export async function getProducts() {
  return request("/api/products/");
}

export async function createProduct(product) {
  return request("/api/products/", {
    method: "POST",
    body: JSON.stringify(product),
  });
}

export async function updateProduct(productId, product) {
  return request(`/api/products/${productId}`, {
    method: "PATCH",
    body: JSON.stringify(product),
  });
}

export async function getOrders() {
  return request("/api/orders/");
}

export async function updateOrderStatus(orderId, status) {
  return request(`/api/orders/${orderId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function updateOrderCustomer(orderId, customerDetails) {
  return request(`/api/orders/${orderId}/customer`, {
    method: "PATCH",
    body: JSON.stringify(customerDetails),
  });
}

export async function getChatHistory(sessionId) {
  return request(`/api/chat/history/${sessionId}`);
}

export async function deleteChatHistory(sessionId) {
  return request(`/api/chat/history/${sessionId}`, {
    method: "DELETE",
  });
}

export async function getRecentChatSessions() {
  return request("/api/chat/sessions/recent");
}

export async function getDashboardSummary() {
  return request("/api/dashboard/summary");
}
