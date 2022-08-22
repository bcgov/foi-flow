import {
  SUBMISSION_ACCESS,
  ANONYMOUS_ID
} from "../constants/constants";

const replaceUrl = (URL, key, value) => {
  return URL.replace(key, value);
};

const getSubmissionAccess = (processListData) => {
  SUBMISSION_ACCESS.forEach((access) => {
    if (processListData.anonymous) {
      if (["create_own", "read_all", "update_all"].includes(access.type)) {
        access.roles.push(ANONYMOUS_ID);
      }
    } else {
      if (access.type === "create_own") {
        access.roles = access.roles.filter((id) => id !== ANONYMOUS_ID);
      }
    }
  });
  console.log(`SUBMISSION_ACCESS === ${JSON.stringify(SUBMISSION_ACCESS)}`)
  return SUBMISSION_ACCESS;
}

export { replaceUrl, getSubmissionAccess };
