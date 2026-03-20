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
    return true;
  }
  const email = applicantProfile?.email?.trim();
  const emailProvided = email && email.length > 0;
  const emailValid = emailProvided && EmailValidator.validate(email);
  const addressFieldsValid =
    (Object.hasOwn(applicantProfile, 'address') && applicantProfile?.address !== "" && applicantProfile?.address !== null && applicantProfile?.address?.length <= 120) && 
    (Object.hasOwn(applicantProfile, 'city') && applicantProfile?.city !== "" && applicantProfile?.city !== null && applicantProfile?.city?.length <= 120) &&
    (Object.hasOwn(applicantProfile, 'province') && applicantProfile?.province !== "" && applicantProfile?.province !== null && applicantProfile?.province?.length <= 120) &&
    (Object.hasOwn(applicantProfile, 'country') && applicantProfile?.country !== "" && applicantProfile?.country !== null && applicantProfile?.country?.length <= 120) &&
    (Object.hasOwn(applicantProfile, 'postal') &&  applicantProfile?.postal !== "" && applicantProfile?.postal !== null && applicantProfile?.postal?.length <= 6);
  const applicantDetailFieldsValid = 
    (Object.hasOwn(applicantProfile, 'firstName') && applicantProfile?.firstName !== "" && applicantProfile?.firstName !== null && applicantProfile?.firstName?.length <= 50) && 
    (Object.hasOwn(applicantProfile, 'lastName') && applicantProfile?.lastName !== "" && applicantProfile?.lastName !== null && applicantProfile?.lastName?.length <= 50) &&
    (Object.hasOwn(applicantProfile, 'category') && applicantProfile?.category !== "" && applicantProfile?.category !== null);
  const charFieldLengthInvalid = 
    applicantProfile?.address?.length > 120 ||
    applicantProfile?.city?.length > 120 ||
    applicantProfile?.province?.length > 120 ||
    applicantProfile?.country?.length > 120 ||
    applicantProfile?.postal?.length > 6 ||
    applicantProfile?.middleName?.length > 50 ||
    applicantProfile?.businessName?.length > 255 ||
    applicantProfile?.addressSecondary?.length > 120 ||
    applicantProfile?.phonePrimary?.length > 50 ||
    applicantProfile?.phoneSecondary?.length > 50 ||
    applicantProfile?.workPhonePrimary?.length > 50 ||
    applicantProfile?.workPhoneSecondary?.length > 50 ||
    applicantProfile?.additionalPersonalInfoValid?.alsoKnownAs?.length > 250 ||
    applicantProfile?.additionalPersonalInfoValid?.personalHealthNumber?.length > 50 ||
    applicantProfile?.publicServiceEmployeeNumber?.length > 50 ||
    applicantProfile?.correctionalServiceNumber?.length > 50;

  let contactInvalid = false;
  // Mandatory Field Validation
  if (emailProvided && !emailValid) {
    contactInvalid = true;
  }
  if (!emailProvided && !addressFieldsValid) {
    contactInvalid = true;
  }
  if (!applicantDetailFieldsValid) {
    contactInvalid = true;
  }
  // Field Length Validation
  if (charFieldLengthInvalid) {
    contactInvalid = true;
  }

  return contactInvalid;
};
