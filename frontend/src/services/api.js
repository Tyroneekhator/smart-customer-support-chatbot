export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const ADMIN_TOKEN_KEY = "cookiebot_admin_token";
const ADMIN_PROFILE_KEY = "cookiebot_admin_profile";

export function getStoredAdminToken() {
  return localStorage.getItem(ADMIN_TOKEN_KEY);
}

export function getStoredAdminProfile() {
  const storedProfile = localStorage.getItem(ADMIN_PROFILE_KEY);

  if (!storedProfile) {
    return null;
  }

  try {
    return JSON.parse(storedProfile);
  } catch {
    localStorage.removeItem(ADMIN_PROFILE_KEY);
    return null;
  }
}

function decodeTokenPayload(token) {
  try {
    const payload = token.split(".")[1];
    const paddedPayload = `${payload}${"=".repeat((4 - (payload.length % 4)) % 4)}`;
    return JSON.parse(atob(paddedPayload.replaceAll("-", "+").replaceAll("_", "/")));
  } catch {
    return null;
  }
}

export function isAdminLoggedIn() {
  const token = getStoredAdminToken();

  if (!token) {
    return false;
  }

  const payload = decodeTokenPayload(token);

  if (!payload?.exp || payload.exp * 1000 < Date.now()) {
    clearAdminSession();
    return false;
  }

  return true;
}

export function clearAdminSession() {
  localStorage.removeItem(ADMIN_TOKEN_KEY);
  localStorage.removeItem(ADMIN_PROFILE_KEY);
}

function saveAdminSession(data) {
  localStorage.setItem(ADMIN_TOKEN_KEY, data.access_token);
  localStorage.setItem(ADMIN_PROFILE_KEY, JSON.stringify(data.admin));
}

async function request(endpoint, options = {}) {
  const token = getStoredAdminToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = "Request failed.";

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = `${response.status} ${response.statusText}`;
    }

    if (response.status === 401) {
      clearAdminSession();
    }

    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export async function loginAdmin(username, password) {
  const data = await request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

  saveAdminSession(data);
  return data;
}

export async function logoutAdmin() {
  try {
    if (getStoredAdminToken()) {
      await request("/api/auth/logout", {
        method: "POST",
      });
    }
  } finally {
    clearAdminSession();
  }
}

export async function getCurrentAdmin() {
  return request("/api/auth/me");
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
