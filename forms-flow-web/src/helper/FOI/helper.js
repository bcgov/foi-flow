import dayjs from 'dayjs';
import DateHolidayjs from 'date-holidays';
import dayjsBusinessDays from 'dayjs-business-days';
import { format, utcToZonedTime } from 'date-fns-tz';
import MINISTRYGROUPS from '../../constants/FOI/foiministrygroupConstants';
import { SESSION_SECURITY_KEY, SESSION_LIFETIME } from "../../constants/constants";
import { toast } from "react-toastify";
import { KCProcessingTeams, KCScanningTeam } from "../../constants/FOI/enum";
import _ from 'lodash';

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

const isScanningTeam = (userGroups) => {
  return userGroups?.some((userGroup) =>
    userGroup.replace("/", "") == KCScanningTeam
  );
};

const isFoiAdmin = (userGroups) => {
  return (
    userGroups?.map((userGroup) => userGroup.replace("/", "")).indexOf("FOI Admin") !== -1
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
  // console.log("userArray:",userArray)
  // console.log("foiteam:",foiteam)

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
  // console.log("team-session data:",(`${team.toLowerCase()}AssignToList`).replaceAll('"',''))
  // console.log("getAssignToList() =>", getSessionData((`${team.toLowerCase()}AssignToList`).replaceAll('"','')))

  return getSessionData((`${team.toLowerCase()}AssignToList`).replaceAll('"','')) || [];
};

const getFullnameTeamList = () => {
  return getSessionData("fullnameTeamList");
};

const getMinistryRestrictedTagList = () => {
  return getSessionData("ministryRestrictedTagList");
};

const getIAOAssignToList = () => {
  //console.log("getIAOAssignToList() =>",getSessionData("iaoAssignToList"))
  return getSessionData("iaoAssignToList");
};

const getUserFullName = (firstName, lastName, userName, groupName = "") => {
  // let users = getSessionData("fullnameList");
  // if (userName) {
  //   const user = users?.find((user) => user.username === userName);
  //   return user ? user?.fullname : null;
  // }
  // return groupName;

  if (firstName && lastName) {
    return `${lastName}, ${firstName}`;
  } else if (userName) {
    return userName;
  } else {
    return groupName;
  }
  
}
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

const isRequestWatcherOrAssignee = (requestWatchers,requestAssignees,userId) => {
  return (_.map(requestWatchers, "watchedby").includes(userId) || (requestAssignees.assignedTo == userId));
}

const isRequestWatcherOrMinistryAssignee = (requestWatchers,ministryAssigneeValue,userId) => {
  return (_.map(requestWatchers, "watchedby").includes(userId) || (ministryAssigneeValue.includes(userId)));
}

const addToRestrictedRequestTagList = (requestWatchers, assigneeDetails) => {
  let fullnameList = getFullnameList();
  let fullnameArray = [];
  let fullnameSet = new Set();
  let currentMember;
  if(assigneeDetails){
    currentMember = {
      username: assigneeDetails?.assignedministryperson,
      firstname: assigneeDetails?.assignedministrypersonFirstName,
      lastname: assigneeDetails?.assignedministrypersonLastName,
      fullname: `${assigneeDetails?.assignedministrypersonLastName}, ${assigneeDetails?.assignedministrypersonFirstName}`,
      name: `${assigneeDetails?.assignedministrypersonLastName}, ${assigneeDetails?.assignedministrypersonFirstName}`,
    };
    fullnameArray.push(currentMember);
    fullnameSet.add(currentMember);
  }
  if(requestWatchers){
    requestWatchers?.forEach((watcher) => {
      let fullNameArray = fullnameList?.filter((e) => e.username === watcher?.watchedby);
      let fullName= fullNameArray[0].fullname;
      currentMember = {
        username: watcher?.watchedby,
        firstname: fullName?.split(",")[1],
        lastname: fullName?.split(",")[0],
        fullname: fullName,
        name: fullName,
      };
      if(!fullnameArray?.some((e) => e.username === watcher?.watchedby))
        fullnameArray.push(currentMember);
      fullnameSet.add(currentMember);

    });
  }
  let IAOList = getAssignToList('iao')?.filter((e) => e.type === 'iao');
  if(IAOList && IAOList?.length > 0){
    IAOList.forEach((team) => {
      team?.members.forEach((ministryUser) => {
        currentMember = {
          username: ministryUser?.username,
          firstname: ministryUser?.firstname,
          lastname: ministryUser?.lastname,
          fullname: `${ministryUser?.lastname}, ${ministryUser?.firstname}`,
          name: `${ministryUser?.lastname}, ${ministryUser?.firstname}`
        };
        if(!fullnameArray?.some((e) => e.username === ministryUser?.username))
          fullnameArray.push(currentMember);
        fullnameSet.add(currentMember);

      });
    });
  }
  saveSessionData("ministryRestrictedTagList", fullnameArray);
};

const getRestrictedRequestTagList = () => {
  return getSessionData("restrictedrequesttagList") || [];
};

const isRequestRestricted = (requestDetails, ministryId) => {
  if(ministryId){
    return requestDetails?.iaorestricteddetails?.isrestricted;
  } 
  else
    return requestDetails?.isiaorestricted;
}

const isRequestMinistryRestricted = (requestDetails) => {
  return requestDetails?.ministryrestricteddetails?.isrestricted;
}

const isrecordtimeout = (createDate, slaHrs) => {
  let dt1_str = createDate.replace("|", ",");
  let dt1 = new Date(dt1_str);
  let dt2 = new Date();
  let diff =  (dt2.getTime() - dt1.getTime()) / 1000;
  diff = diff/(60*60)
  let diffhrs = Math.abs(Math.round(diff));
  return diffhrs >= slaHrs;
};

const readUploadedFileAsBytes = (inputFile) => {
  const temporaryFileReader = new FileReader();

  return new Promise((resolve, reject) => {
    temporaryFileReader.onerror = () => {
      temporaryFileReader.abort();
      reject(new DOMException("Problem parsing input file."));
    };

    temporaryFileReader.onload = () => {
      resolve(temporaryFileReader.result);
    };
    temporaryFileReader.readAsArrayBuffer(inputFile);
  });
};

const getCommentTypeIdByName = (commentTypes, name) => {
  const commentType = commentTypes.find(type => type.name === name);
  return commentType ? commentType.commenttypeid : 0;
};

const getCommentLabelFromId = (commentTypes, id) => {
  const commentType = commentTypes.find(type => type.commenttypeid === id);
  return commentType ? commentType.label?.toUpperCase() : "";
};

const getCommentTypeFromId = (commentTypes, id) => {
  const commentType = commentTypes.find(type => type.commenttypeid === id);
  if(commentType != null && commentType != undefined){
    if(commentType.name == "User submitted")
      return "general";
    else
      return commentType.name?.toLowerCase()
  }
  return "";
};

const setTeamTagList = (bcgovcode) => {
  //let fullnameList = getFullnameList();
  let iaoFullnameArray = [];
  let fullnameSet = new Set();
  let currentMember;
  let IAOList = getAssignToList('iao')?.filter((e) => e.type === 'iao');
  if(IAOList && IAOList?.length > 0){
    IAOList.forEach((team) => {
      team?.members.forEach((ministryUser) => {
        currentMember = {
          username: ministryUser?.username,
          firstname: ministryUser?.firstname,
          lastname: ministryUser?.lastname,
          fullname: `${ministryUser?.lastname}, ${ministryUser?.firstname}`,
          name: `${ministryUser?.lastname}, ${ministryUser?.firstname}`
        };
        if(!iaoFullnameArray?.some((e) => e.username === ministryUser?.username))
          iaoFullnameArray.push(currentMember);
        fullnameSet.add(currentMember);

      });
    });
    saveSessionData("iaoTagList", iaoFullnameArray);
  }
  let fullnameArray = [];

  if(bcgovcode !== null && bcgovcode !== undefined && bcgovcode !== 'iao'){
    let ministryList= getAssignToList(bcgovcode)
    //console.log("**ministryList:", ministryList)
    if(ministryList && ministryList?.length >0){
      ministryList.forEach((team) => {
        team?.members.forEach((ministryUser) => {
          currentMember = {
            username: ministryUser?.username,
            firstname: ministryUser?.firstname,
            lastname: ministryUser?.lastname,
            fullname: `${ministryUser?.lastname}, ${ministryUser?.firstname}`,
            name: `${ministryUser?.lastname}, ${ministryUser?.firstname}`
          };
          if(!fullnameArray?.some((e) => e.username === ministryUser?.username))
            fullnameArray.push(currentMember);
          fullnameSet.add(currentMember);
  
        });
      });
    }
    let _team = bcgovcode.toLowerCase().replace(/['"]+/g, '');
    //console.log("******_team*******",_team)
    console.log("*************",fullnameArray)
    saveSessionData(`${_team}TagList`, fullnameArray);
  }

  
};

const getIAOTagList = (bcgovcode) => {
  let _team = bcgovcode.toLowerCase()?.replace(/['"]+/g, '');
  console.log("_team",_team)
  console.log("=>",getSessionData(`${_team}TagList`))
  return getSessionData(`${_team}TagList`) || [];
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
  isRequestWatcherOrAssignee,
  isRequestWatcherOrMinistryAssignee,
  formatDateInPst,
  isProcessingTeam,
  isScanningTeam,
  isFlexTeam,
  isIntakeTeam,
  encrypt,
  decrypt,
  addToRestrictedRequestTagList,
  getRestrictedRequestTagList,
  isRequestRestricted,
  isRequestMinistryRestricted,
  getMinistryRestrictedTagList,
  isrecordtimeout,
  isFoiAdmin,
  readUploadedFileAsBytes,
  getUserFullName,
  getCommentTypeIdByName,
  getCommentLabelFromId,
  getIAOAssignToList,
  setTeamTagList,
  getIAOTagList,
  getCommentTypeFromId
};