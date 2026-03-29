import http from "k6/http";
import { check, sleep } from "k6";

import { BASE_URL, getFirstPublishedProductSlug } from "./common.js";

export const options = {
  vus: Number(__ENV.VUS || 10),
  duration: __ENV.DURATION || "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<800"],
  },
};

export function setup() {
  return {
    productSlug: getFirstPublishedProductSlug(),
  };
}

export default function (data) {
  const listResponse = http.get(`${BASE_URL}/api/v1/products/`);
  check(listResponse, {
    "catalog list 200": (r) => r.status === 200,
  });

  const detailResponse = http.get(
    `${BASE_URL}/api/v1/products/${data.productSlug}/`
  );
  check(detailResponse, {
    "catalog detail 200": (r) => r.status === 200,
  });

  const searchResponse = http.get(`${BASE_URL}/api/v1/products/?q=demo`);
  check(searchResponse, {
    "catalog search 200": (r) => r.status === 200,
  });

  sleep(1);
}
