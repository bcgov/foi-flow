import Holidays from "date-holidays";
import moment from "moment-timezone";
import { calculateBusinessDaysBetween } from "./helper";
import { getReceivedDate, getClosedDate } from "../../components/FOI/Dashboard/utils";

describe("retained Vancouver timezone fixtures", () => {
  test.each([
    ["2025-01-15T20:00:00Z", "2025-01-15 12:00:00"],
    ["2026-01-15T20:00:00Z", "2026-01-15 12:00:00"],
    ["2026-03-08T09:59:59Z", "2026-03-08 01:59:59"],
    ["2026-03-08T10:00:00Z", "2026-03-08 03:00:00"],
    ["2026-11-01T08:59:59Z", "2026-11-01 01:59:59"],
    ["2026-11-01T09:00:00Z", "2026-11-01 02:00:00"],
    ["2026-11-03T07:30:00Z", "2026-11-03 00:30:00"],
    ["2026-11-02T23:31:00Z", "2026-11-02 16:31:00"],
    ["2027-01-15T19:00:00Z", "2027-01-15 12:00:00"],
  ])("%s is %s in Vancouver", (instant, expected) => {
    expect(moment.tz(instant, "America/Vancouver").format("YYYY-MM-DD HH:mm:ss")).toBe(expected);
  });

  test.each([
    ["2026-11-11T07:30:00Z", "Remembrance Day"],
    ["2026-12-25T07:30:00Z", "Christmas Day"],
    ["2025-12-25T08:30:00Z", "Christmas Day"],
  ])("the shipped holiday provider recognizes %s", (instant, name) => {
    const holidays = new Holidays("CA", "BC");
    expect(holidays.isHoliday(new Date(instant))).toEqual(
      expect.arrayContaining([expect.objectContaining({ name })])
    );
  });
});

describe.each([
  ["received date", getReceivedDate, "receivedDateUF"],
  ["closed date", getClosedDate, "closedate"],
])("dashboard %s follows B.C. calendar and cutoff", (label, displayDate, field) => {
  test.each([
    ["2026-11-02T23:29:00Z", "NOV 02 2026"],
    ["2026-11-02T23:30:00Z", "NOV 02 2026"],
    ["2026-11-02T23:30:59Z", "NOV 02 2026"],
    ["2026-11-02T23:31:00Z", "NOV 03 2026"],
    ["2026-11-02T18:31:00-05:00", "NOV 03 2026"],
    ["2026-11-03T07:30:00Z", "NOV 03 2026"],
    ["2025-01-15T00:30:00Z", "JAN 14 2025"],
    ["2025-01-15T00:31:00Z", "JAN 15 2025"],
    ["2027-01-15T23:31:00Z", "JAN 18 2027"],
    ["2026-11-06T23:31:00Z", "NOV 09 2026"],
    ["2026-11-10T23:31:00Z", "NOV 12 2026"],
    ["2026-11-11 16:31:00", "NOV 12 2026"],
    ["2026-11-11T23:31:00Z", "NOV 12 2026"],
    // Offset-less API values are already Vancouver wall time; date-only
    // business fields must not be reinterpreted as UTC instants.
    ["2026-11-02 16:29:00.000000", "NOV 02 2026"],
    ["2026-11-02 16:30:59.000000", "NOV 02 2026"],
    ["2026-11-02 16:31:00.000000", "NOV 03 2026"],
    ["2026-11-02", "NOV 02 2026"],
    ["2026-11-07", "NOV 09 2026"],
    ["", ""],
    [null, ""],
    ["not a date", ""],
    ["2026-02-30", ""],
  ])("%s displays %s", (value, expected) => {
    expect(displayDate({ row: { [field]: value } })).toBe(expected);
  });

  test("retains the existing in-hours holiday policy", () => {
    // Holiday policy is outside this timezone correction. The existing UI
    // advances for weekends/after-cutoff and skips holidays during advancement.
    expect(displayDate({ row: { [field]: "2026-11-11 10:00:00" } })).toBe("NOV 11 2026");
  });
});

describe("Open Information business-day publication warning", () => {
  test.each([
    ["2026-11-10", "2026-11-12", 1],
    ["2026-11-09", "2026-11-23", 9],
    ["2026-11-09", "2026-11-24", 10],
    ["2026-11-23", "2026-11-09", -9],
    ["2026-11-02", "2026-11-02", 0],
    ["2026-11-06", "2026-11-09", 1],
    ["2026-03-06", "2026-03-09", 1],
    ["2025-11-10", "2025-11-12", 1],
    ["2026-12-24", "2026-12-25", 0],
    ["2026-11-03T07:30:00Z", "2026-11-04", 1],
  ])("%s to %s counts %i days", (from, to, expected) => {
    expect(calculateBusinessDaysBetween(from, to)).toBe(expected);
  });
});
