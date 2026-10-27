import moment from "moment-timezone";

const BUSINESS_TIME_ZONE = "America/Vancouver";

/**
 * For receipt business-wall values and date-only business fields, missing
 * offsets mean B.C. calendar time. Explicit offsets and Date objects identify
 * an instant. This parser must not be used for UTC-naive audit timestamps;
 * the API must normalize any created_at receipt fallback to the wall contract.
 *
 * Use the bundled timezone data so business decisions do not depend on the
 * browser's default zone or its separately maintained timezone database.
 */
const parseBusinessDateTime = (value) => {
  if (value === undefined || value === null || value === "") return null;
  if (typeof value !== "string" && typeof value !== "number" && !(value instanceof Date)) return null;

  const date = typeof value === "string"
    ? moment.tz(value, moment.ISO_8601, true, BUSINESS_TIME_ZONE)
    : moment(value).tz(BUSINESS_TIME_ZONE);

  return date.isValid() ? date : null;
};

export { BUSINESS_TIME_ZONE, parseBusinessDateTime };
