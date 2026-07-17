// Minimal ambient declaration so CRA's TypeScript build does not fail on
// tests that import redux-mock-store. The package ships no types, and the
// @types/redux-mock-store dev-dependency is not installed in the Docker
// build image; a bare module declaration is enough because tests only use
// the default export as a factory.
declare module "redux-mock-store";
