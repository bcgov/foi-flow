export const PAYMENT_EXPIRY_DAYS =
  (window._env_ && window._env_.PAYMENT_EXPIRY_DAYS) ||
  process.env.PAYMENT_EXPIRY_DAYS ||
  20;