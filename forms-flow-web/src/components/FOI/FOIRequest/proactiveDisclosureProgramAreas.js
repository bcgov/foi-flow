const PROACTIVE_DISCLOSURE_EXCLUDED_IAO_CODES = [
  "OCC",
  "TIC",
  "CLB",
  "CFD",
  "COR",
  "IIO",
  "LSB",
  "MGC",
  "OBC",
];

export const isProactiveDisclosureProgramArea = (programArea) =>
  !PROACTIVE_DISCLOSURE_EXCLUDED_IAO_CODES.includes(programArea?.iaocode);
