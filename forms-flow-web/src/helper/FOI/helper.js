import dayjs from 'dayjs';
import DateHolidayjs from 'date-holidays';
import dayjsBusinessDays from 'dayjs-business-days';
import { format, utcToZonedTime } from 'date-fns-tz';
import MINISTRYGROUPS from '../../constants/FOI/foiministrygroupConstants';
import { SESSION_SECURITY_KEY, SESSION_LIFETIME } from "../../constants/constants";
import { toast } from "react-toastify";
import { KCProcessingTeams } from "../../constants/FOI/enum";

let isBetween = require("dayjs/plugin/isBetween");
let utc = require("dayjs/plugin/utc");
let timezone = require("dayjs/plugin/timezone");
let CryptoJS = require("crypto-js");

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(isBetween);
dayjs.extend(dayjsBusinessDays);
const hd = new DateHolidayjs("CA", "BC");

const replaceUrl = (URL, key, value) => {
  return URL.replace(key, value);
};

const formatInTimeZone = (date, fmt, tz) =>
  format(utcToZonedTime(date, tz), fmt, { timeZone: tz });

const formatDate = (d, formatString = "yyyy-MM-dd") => {
  if (d) {
    return formatInTimeZone(d, formatString, "UTC");
  } else {
    return "";
  }
};

const formatDateInPst = (d, formatString = "yyyy-MM-dd") => {
  if (d) {
    return formatInTimeZone(d, formatString, "America/Vancouver");
  } else {
    return "";
  }
};

const businessDay = (date) => {
  return dayjs(date).isBusinessDay();
};

const getHolidayList = (startYear, endYear) => {
  let holidays = [];
  if (startYear > endYear) {
    let temp = startYear;
    startYear = endYear;
    endYear = temp;
  }
  for (; startYear <= endYear; startYear++) {
    holidays = holidays.concat(hd.getHolidays(startYear));
  }
  return holidays;
};
const getPublicHoliDays = (startDate, endDate) => {
  let publicHoliDays = 0;
  const startYear = dayjs(startDate).year();
  const endYear = dayjs(endDate).year();
  const holidays = getHolidayList(startYear, endYear);
  for (const entry of holidays) {
    if (
      entry.type === "public" &&
      dayjs(entry.date).isBetween(startDate, endDate, null, "[]")
    ) {
      publicHoliDays++;
    }
  }
  return publicHoliDays;
};
const reconcilePublicHoliDays = (startDate, endDate) => {
  let publicHoliDays = getPublicHoliDays(startDate, endDate);
  endDate = endDate.businessDaysAdd(publicHoliDays);
  startDate = endDate;
  if (publicHoliDays !== 0) {
    return reconcilePublicHoliDays(startDate, endDate);
  }
  return endDate;
};
const addBusinessDays = (dateText, days) => {
  if (!dateText) {
    return 0;
  }
  let startDate = dayjs(dateText);
  let endDate = startDate.businessDaysAdd(days);
  return reconcilePublicHoliDays(startDate, endDate).format("YYYY-MM-DD");
};

const revertReconciledPublicHolidays = (startDate, endDate) => {
  let publicHoliDays = getPublicHoliDays(startDate, endDate);
  endDate = endDate.businessDaysSubtract(publicHoliDays);
  startDate = endDate;
  if (publicHoliDays !== 0) {
    return reconcilePublicHoliDays(startDate, endDate);
  }
  return endDate;
};

const removeBusinessDays = (dateText, days) => {
  if (!dateText) {
    return 0;
  }
  let startDate = dayjs(dateText);
  let endDate = startDate.businessDaysSubtract(days);

  return revertReconciledPublicHolidays(startDate, endDate).format(
    "YYYY-MM-DD"
  );
};

const countWeekendDays = (startDate, endDate) => {
  let ndays =
    1 +
    Math.round((endDate.getTime() - startDate.getTime()) / (24 * 3600 * 1000));
  let nsaturdays = Math.floor((startDate.getDay() + ndays) / 7);
  return 2 * nsaturdays + (startDate.getDay() === 0) - (endDate.getDay() === 6);
};

const daysBetween = (startDate, endDate) => {
  let millisecondsPerDay = 24 * 60 * 60 * 1000;
  return (endDate - startDate) / millisecondsPerDay;
};
const calculateDaysRemaining = (endDate, startDate) => {
  if (!startDate) {
    startDate = new Date();
  } else {
    startDate = new Date(startDate);
  }
  endDate = new Date(endDate);
  const publicHoliDays = getPublicHoliDays(startDate, endDate);
  const weekendDays = countWeekendDays(startDate, endDate);
  const noOfDays = daysBetween(startDate, endDate);
  if (noOfDays < 0) {
    return (
      Math.ceil(noOfDays) +
      Math.round(publicHoliDays) -
      Math.round(weekendDays)
    )
  } else {
    return (
      Math.floor(noOfDays) -
      Math.round(publicHoliDays) -
      Math.round(weekendDays) +
      1
    );
  }
};

const isMinistryCoordinator = (userdetail, ministryteam) => {
  if (
    userdetail === undefined ||
    userdetail === null ||
    userdetail === "" ||
    userdetail.groups === undefined ||
    userdetail.groups.length === 0 ||
    ministryteam === undefined ||
    ministryteam === ""
  ) {
    return false;
  }

  if (
    userdetail.groups.indexOf("/Intake Team") !== -1 ||
    userdetail.groups.indexOf("/Flex Team") !== -1 ||
    userdetail.groups.indexOf("/Processing Team") !== -1
  ) {
    return false;
  } else if (userdetail.groups.indexOf("/" + ministryteam) !== -1) {
    return true;
  } else {
    return false;
  }
};

const isMinistryLogin = (userGroups) => {
  return Object.values(MINISTRYGROUPS).some((group) =>
    userGroups?.includes(group)
  );
};
const isProcessingTeam = (userGroups) => {
  return userGroups?.some((userGroup) =>
    KCProcessingTeams.includes(userGroup.replace("/", ""))
  );
};

const isFlexTeam = (userGroups) => {
  return (
    userGroups?.map((userGroup) => userGroup.replace("/", "")).indexOf("Flex Team") !== -1
  );
};

const isIntakeTeam = (userGroups) => {
  return (
    userGroups?.map((userGroup) => userGroup.replace("/", "")).indexOf("Intake Team") !== -1
  );
};

const getMinistryByValue = (userGroups) => {
  const ministryGroup = Object.values(MINISTRYGROUPS).filter((element) =>
    userGroups.includes(element)
  );
  return Object.keys(MINISTRYGROUPS).find(
    (key) => MINISTRYGROUPS[key] === ministryGroup
  );
};

const encrypt = (obj) => {
  return CryptoJS.AES.encrypt(
    JSON.stringify(obj),
    SESSION_SECURITY_KEY
  ).toString();
};

const decrypt = (encrypted) => {
  if (encrypted) {
    let bytes = CryptoJS.AES.decrypt(encrypted, SESSION_SECURITY_KEY);
    return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
  } else {
    return {};
  }
};

const saveSessionData = (key, data) => {
  let expiresInMilliseconds = Date.now() + SESSION_LIFETIME;
  let sessionObject = {
    expiresAt: new Date(expiresInMilliseconds),
    sessionData: data,
  };

  sessionStorage.setItem(key, encrypt(sessionObject));
};

const getSessionData = (key) => {
  let sessionObject = decrypt(sessionStorage.getItem(key));

  if (sessionObject && sessionObject.sessionData && sessionObject.expiresAt) {
    let currentDate = new Date();
    let expirationDate = sessionObject.expiresAt;

    if (Date.parse(currentDate) < Date.parse(expirationDate)) {
      return sessionObject.sessionData;
    } else {
      sessionStorage.removeItem(key);
      console.log(`${key} session expired`);
      return null;
    }
  } else {
    return null;
  }
};

const addToFullnameList = (userArray, foiteam) => {
  if (!foiteam) return;

  const _team = foiteam.toLowerCase();
  let currentMember;

  //fullname array (all teams) -> fullname value pairs
  let fullnameArray = getSessionData("fullnameList");
  if (!Array.isArray(fullnameArray)) {
    fullnameArray = [];
  }

  //teams saved in fullnameList
  let fullnameTeamArray = getSessionData("fullnameTeamList");
  if (!Array.isArray(fullnameTeamArray)) {
    fullnameTeamArray = [];
  }

  //extract fullname and append to the array
  if (Array.isArray(userArray)) {
    userArray?.forEach((team) => {
      if (Array.isArray(team?.members)) {
        team.members?.forEach((member) => {
          if (!fullnameArray.some((e) => e.username === member.username)) {
            currentMember = {
              username: member.username,
              fullname: `${member.lastname}, ${member.firstname}`,
            };
            fullnameArray.push(currentMember);
          }
        });
      }
    });

    //save team name
    if (!fullnameTeamArray.includes(_team)) {
      fullnameTeamArray.push(_team);
      saveSessionData(`fullnameTeamList`, fullnameTeamArray);

      //save for assignedto or ministryassignto dropdown
      saveSessionData(`${_team}AssignToList`, userArray);
    }
  }
  saveSessionData("fullnameList", fullnameArray);
};

const getFullnameList = () => {
  return getSessionData("fullnameList") || [];
};

const getAssignToList = (team) => {
  return getSessionData(`${team.toLowerCase()}AssignToList`);
};

const getFullnameTeamList = () => {
  return getSessionData("fullnameTeamList");
};

const ConditionalComponent = ({ condition, children }) => {
  if (!condition) {
    return null;
  }

  return <>{children}</>;
};

const getMinistryCode = (userGroups) => {
  const ministryGroup = Object.values(MINISTRYGROUPS).find((element) =>
    userGroups?.includes(element)
  );
  return Object.keys(MINISTRYGROUPS).find(
    (key) => MINISTRYGROUPS[key] === ministryGroup
  );
};

const errorToast = (errorMessage) => {
  return toast.error(errorMessage, {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: true,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    progress: undefined,
  });
};

export {
  replaceUrl,
  formatDate,
  businessDay,
  addBusinessDays,
  calculateDaysRemaining,
  isMinistryCoordinator,
  isMinistryLogin,
  getMinistryByValue,
  addToFullnameList,
  getFullnameList,
  getAssignToList,
  getFullnameTeamList,
  ConditionalComponent,
  removeBusinessDays,
  getMinistryCode,
  errorToast,
  formatDateInPst,
  isProcessingTeam,
  isFlexTeam,
  isIntakeTeam,
  encrypt,
  decrypt,
};