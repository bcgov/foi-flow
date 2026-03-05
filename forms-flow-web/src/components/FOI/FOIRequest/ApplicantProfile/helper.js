export const clearObject = (obj) => {
  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => {
      if (value && typeof value === "object" && !Array.isArray(value)) {
        return [key, clearObject(value)];
      }
      return [key, null];
    }),
  );
};
