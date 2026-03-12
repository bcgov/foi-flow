import * as EmailValidator from "email-validator";

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
export const validateApplicantProfileFields = (applicantProfile) => {
  if (!applicantProfile || Object.keys(applicantProfile).length === 0) {
    return true; // invalid
  }

  const email = applicantProfile?.email?.trim();
  const emailProvided = email && email.length > 0;
  const emailValid = emailProvided && EmailValidator.validate(email);

  const addressFieldsPresent =
    applicantProfile?.address &&
    applicantProfile?.city &&
    applicantProfile?.province &&
    applicantProfile?.country &&
    applicantProfile?.postal;

  // EMAIL + ADDRESS RULE
  let contactInvalid = false;

  if (emailProvided && !emailValid) {
    contactInvalid = true;
  }

  if (!emailProvided && !addressFieldsPresent) {
    contactInvalid = true;
  }

  return contactInvalid;
};
