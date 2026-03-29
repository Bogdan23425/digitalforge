import http from "k6/http";
import { check, sleep } from "k6";

import { BASE_URL, expectedStatuses } from "./common.js";

export const options = {
  vus: Number(__ENV.VUS || 5),
  duration: __ENV.DURATION || "20s",
  thresholds: {
    checks: ["rate>0.99"],
  },
};

export default function () {
  const jar = http.cookieJar();

  const csrfResponse = http.get(`${BASE_URL}/api/v1/auth/csrf/`, { jar });
  check(csrfResponse, {
    "csrf 200": (r) => r.status === 200,
  });

  const cookies = jar.cookiesForURL(BASE_URL);
  const csrfToken = cookies.csrftoken && cookies.csrftoken.length > 0
    ? cookies.csrftoken[0]
    : "";

  const loginResponse = http.post(
    `${BASE_URL}/api/v1/auth/login/`,
    JSON.stringify({
      email: __ENV.BUYER_EMAIL || "demo-buyer@digitalforge.local",
      password: "WrongPass123",
    }),
    {
      jar,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      responseCallback: expectedStatuses([400, 429]),
    }
  );

  check(loginResponse, {
    "login abuse returns 400 or 429": (r) => r.status === 400 || r.status === 429,
  });

  const resendResponse = http.post(
    `${BASE_URL}/api/v1/auth/resend-verification-code/`,
    JSON.stringify({
      email: __ENV.BUYER_EMAIL || "demo-buyer@digitalforge.local",
    }),
    {
      jar,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      responseCallback: expectedStatuses([204, 403, 422, 429]),
    }
  );

  check(resendResponse, {
    "resend abuse returns guarded status": (r) =>
      r.status === 204 || r.status === 403 || r.status === 422 || r.status === 429,
  });

  sleep(1);
}
