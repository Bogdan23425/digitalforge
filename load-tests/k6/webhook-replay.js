import http from "k6/http";
import { check, sleep } from "k6";

import { BASE_URL, expectedStatuses } from "./common.js";

export const options = {
  vus: Number(__ENV.VUS || 3),
  duration: __ENV.DURATION || "20s",
  thresholds: {
    checks: ["rate>0.99"],
  },
};

export default function () {
  const eventId = __ENV.REPLAY_SAME_EVENT === "true"
    ? "evt_k6_replay_fixed"
    : `evt_k6_replay_${__VU}_${__ITER}`;

  const response = http.post(
    `${BASE_URL}/api/v1/payments/webhooks/`,
    JSON.stringify({
      event_id: eventId,
      event_type: "payment.succeeded",
      provider: "stripe",
      provider_payment_id: `pi_k6_${__VU}_${__ITER}`,
    }),
    {
      headers: {
        "Content-Type": "application/json",
      },
      responseCallback: expectedStatuses([200, 404, 422, 429]),
    }
  );

  check(response, {
    "webhook returns guarded status": (r) =>
      r.status === 200 || r.status === 404 || r.status === 422 || r.status === 429,
  });

  sleep(1);
}
