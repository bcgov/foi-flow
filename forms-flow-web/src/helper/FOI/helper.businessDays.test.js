import {
  addBusinessDaysExt,
  removeBusinessDaysExt,
} from "./helper";

describe("FOI LDD business-day calculations", () => {

  describe("addBusinessDaysExt", () => {
    test.each([
      ["2026-08-27", 1, "2026-08-28"],
      ["2026-08-28", 1, "2026-08-31"],
      ["2026-12-24", 1, "2026-12-29"],
      ["2026-12-24", 5, "2027-01-05"],

      // Christmas Saturday + Boxing Day Sunday:
      // observed Monday and Tuesday.
      ["2027-12-24", 1, "2027-12-29"],
    ])(
      "%s + %i business days = %s",
      (start, days, expected) => {
        expect(addBusinessDaysExt(start, days)).toBe(expected);
      }
    );
  });

  describe("removeBusinessDaysExt", () => {
    test.each([
      ["2027-01-05", 1, "2027-01-04"],
      ["2027-01-04", 1, "2026-12-31"],
      ["2027-12-29", 1, "2027-12-24"],

      // Regression case:
      // walks from Jan 2027 back into Dec 2026 and must load
      // the 2026 Christmas/Boxing Day holiday calendar.
      ["2027-01-05", 5, "2026-12-24"],
    ])(
      "%s - %i business days = %s",
      (start, days, expected) => {
        expect(removeBusinessDaysExt(start, days)).toBe(expected);
      }
    );
  });

});

describe("business-day invariants", () => {
  test.each([
    ["2026-08-24", 1],
    ["2026-12-24", 5],
    ["2027-01-05", 5],
    ["2027-12-24", 1],
  ])(
    "add then remove returns original date: %s / %i business days",
    (start, days) => {
      const added = addBusinessDaysExt(start, days);
      const result = removeBusinessDaysExt(added, days);

      expect(result).toBe(start);
    }
  );
});
