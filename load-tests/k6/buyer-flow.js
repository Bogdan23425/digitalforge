import http from "k6/http";
import { check, sleep } from "k6";

import {
  BASE_URL,
  BUYER_EMAIL,
  BUYER_PASSWORD,
  expectedStatuses,
  getFirstPublishedProductId,
  getCsrf,
  login,
  withJson,
} from "./common.js";

export const options = {
  vus: Number(__ENV.VUS || 2),
  iterations: Number(__ENV.ITERATIONS || 5),
  thresholds: {
    checks: ["rate>0.95"],
  },
};

export function setup() {
  return {
    productId: getFirstPublishedProductId(),
  };
}

export default function (data) {
  const jar = http.cookieJar();
  login(BUYER_EMAIL, BUYER_PASSWORD, jar);
  const csrfToken = getCsrf(jar);

  const cartResponse = http.post(
    `${BASE_URL}/api/v1/cart/items/`,
    JSON.stringify({
      product_id: data.productId,
    }),
    {
      ...withJson(csrfToken),
      jar,
      responseCallback: expectedStatuses([201, 422, 429]),
    }
  );
  check(cartResponse, {
    "add to cart returns 201 or 422 or 429": (r) =>
      r.status === 201 || r.status === 422 || r.status === 429,
  });

  const checkoutResponse = http.post(
    `${BASE_URL}/api/v1/checkout/`,
    JSON.stringify({
      payment_provider: "stripe",
    }),
    {
      ...withJson(csrfToken),
      jar,
      responseCallback: expectedStatuses([201, 422, 429]),
    }
  );
  check(checkoutResponse, {
    "checkout returns 201 or 422 or 429": (r) =>
      r.status === 201 || r.status === 422 || r.status === 429,
  });

  sleep(1);
}
