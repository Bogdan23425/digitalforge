import http from "k6/http";
import { check } from "k6";

export const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8000";

export const BUYER_EMAIL =
  __ENV.BUYER_EMAIL || "demo-buyer@digitalforge.local";
export const BUYER_PASSWORD = __ENV.BUYER_PASSWORD || "DemoPass123";

export const SELLER_EMAIL =
  __ENV.SELLER_EMAIL || "demo-seller@digitalforge.local";
export const SELLER_PASSWORD = __ENV.SELLER_PASSWORD || "DemoPass123";

export function withJson(csrfToken) {
  const headers = {
    "Content-Type": "application/json",
  };
  if (csrfToken) {
    headers["X-CSRFToken"] = csrfToken;
  }
  return { headers };
}

export function getCsrf(jar) {
  const response = http.get(`${BASE_URL}/api/v1/auth/csrf/`, {
    jar,
  });
  check(response, {
    "csrf endpoint returns 200": (r) => r.status === 200,
  });
  const cookies = jar.cookiesForURL(BASE_URL);
  return cookies.csrftoken && cookies.csrftoken.length > 0
    ? cookies.csrftoken[0]
    : "";
}

export function login(email, password, jar) {
  const csrfToken = getCsrf(jar);
  const response = http.post(
    `${BASE_URL}/api/v1/auth/login/`,
    JSON.stringify({
      email,
      password,
    }),
    {
      ...withJson(csrfToken),
      jar,
    }
  );
  check(response, {
    "login returns 200": (r) => r.status === 200,
  });
  return { response, csrfToken };
}

export function expectedStatuses(statuses) {
  return http.expectedStatuses(...statuses);
}

export function getFirstPublishedProductSlug() {
  const response = http.get(`${BASE_URL}/api/v1/products/`);
  check(response, {
    "public product list returns 200": (r) => r.status === 200,
  });
  const data = response.json();
  const items = Array.isArray(data) ? data : data.results || [];
  if (!items.length) {
    throw new Error("No published products found. Approve at least one product first.");
  }
  return items[0].slug;
}

export function getFirstPublishedProductId() {
  const response = http.get(`${BASE_URL}/api/v1/products/`);
  check(response, {
    "public product list returns 200": (r) => r.status === 200,
  });
  const data = response.json();
  const items = Array.isArray(data) ? data : data.results || [];
  if (!items.length) {
    throw new Error("No published products found. Approve at least one product first.");
  }
  return items[0].id;
}
