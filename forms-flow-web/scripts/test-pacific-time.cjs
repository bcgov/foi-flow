const { spawnSync } = require("node:child_process");
const path = require("node:path");

const tests = [
  "src/helper/FOI/helper.pacificTime.test.js",
  "src/helper/FOI/helper.businessDays.test.js",
  "src/components/FOI/FOIRequest/RequestDetails.pacificTime.test.js",
  "src/components/FOI/FOIRequest/OpenInformation/OpenInfo.pacificTime.test.tsx",
];

for (const zone of ["America/Vancouver", "America/Los_Angeles", "UTC"]) {
  console.log(`\nPacific Time regression: browser default ${zone}`);
  const result = spawnSync(process.execPath, [
    require.resolve("react-scripts/bin/react-scripts"),
    "test", "--watchAll=false", "--runInBand",
    // These tests use Testing Library, not the legacy global Enzyme setup.
    "--setupFilesAfterEnv=@testing-library/jest-dom",
    "--runTestsByPath", ...tests,
  ], {
    cwd: path.resolve(__dirname, ".."),
    env: { ...process.env, CI: "true", TZ: zone },
    stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status || 1);
}
