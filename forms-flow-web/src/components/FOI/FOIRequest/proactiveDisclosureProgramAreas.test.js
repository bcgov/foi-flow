import { isProactiveDisclosureProgramArea } from "./proactiveDisclosureProgramAreas";

describe("Proactive Disclosure program area eligibility", () => {
  it("includes LDB", () => {
    expect(
      isProactiveDisclosureProgramArea({ iaocode: "LDB" })
    ).toBe(true);
  });

  it.each([
    "OCC",
    "TIC",
    "CLB",
    "CFD",
    "COR",
    "IIO",
    "LSB",
    "MGC",
    "OBC",
  ])("continues to exclude %s", (iaocode) => {
    expect(
      isProactiveDisclosureProgramArea({ iaocode })
    ).toBe(false);
  });

  it("includes a standard ministry", () => {
    expect(
      isProactiveDisclosureProgramArea({ iaocode: "AGR" })
    ).toBe(true);
  });
});
