import dayjs from 'dayjs';
import DateHolidayjs from 'date-holidays';
import dayjsBusinessDays from 'dayjs-business-days';
import { format, utcToZonedTime } from 'date-fns-tz';
import MINISTRYGROUPS from '../../constants/FOI/foiministrygroupConstants';
import { SESSION_SECURITY_KEY, SESSION_LIFETIME } from "../../constants/constants";
var isBetween = require('dayjs/plugin/isBetween')
var utc = require("dayjs/plugin/utc")
var timezone = require("dayjs/plugin/timezone")
var CryptoJS = require("crypto-js");

dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(isBetween);
dayjs.extend(dayjsBusinessDays);
const hd = new DateHolidayjs('CA','BC');

const replaceUrl = (URL, key, value) => {
  return URL.replace(key, value);
};

const formatInTimeZone = (date, fmt, tz) =>
	format(utcToZonedTime(date, tz), 
			fmt, 
			{ timeZone: tz });

const formatDate = (d, formatString = 'yyyy-MM-dd') => {
	if (d) {	
	return formatInTimeZone(d, formatString, 'UTC');
	}
	else {
		return "";
	}
}

const businessDay = (date) => {	
	return dayjs(date).isBusinessDay();
}

const getHolidayList = (years) => {
	let holidays = [];
	for(const year of years) {
		holidays = hd.getHolidays(year);
	}
	return holidays;
}
const getPublicHoliDays = (startDate, endDate) => {
	let publicHoliDays = 0;
	let years = [];
	years.push(dayjs(startDate).year());
	const endYear = dayjs(endDate).year();
	if(years.includes(endYear) === false) {
		years.push(endYear);
	}
	const holidays = getHolidayList(years);
	for (const entry of holidays) {
		let day = dayjs(entry.date).day();			
		if(entry.type === "public" && dayjs(entry.date).isBetween(startDate, endDate, null, '[]') && (day >= 1 && day <= 5)) {
			publicHoliDays++;
		}
		//Handle Easter Monday
		if(entry.name === "Good Friday" && dayjs(entry.date).add(3,'day').isBetween(startDate, endDate, null, '[]')) {
			publicHoliDays++;
		}	
		//Handle Boxing Day weekends
		if(entry.name === "Boxing Day" && (day === 6 || day === 0) && dayjs(entry.date).isBetween(startDate, endDate, null, '[]')) {
			publicHoliDays++;
		}			
	}	
	return publicHoliDays;
}
const reconcilePublicHoliDays = (startDate, endDate) => {
	let publicHoliDays = getPublicHoliDays(startDate,endDate);
	endDate = endDate.businessDaysAdd(publicHoliDays);
	startDate = endDate;
	if(publicHoliDays != 0) {			
		reconcilePublicHoliDays(startDate, endDate)
	}
	return endDate;
}
const addBusinessDays = (dateText, days) => {
	if(!dateText) {
		return 0;
	}
	let startDate = dayjs(dateText);	
	let endDate = startDate.businessDaysAdd(days);
	return reconcilePublicHoliDays(startDate,endDate).format('YYYY-MM-DD');	
}

const revertReconciledPublicHolidays = (startDate, endDate) => {
  let publicHoliDays = getPublicHoliDays(startDate, endDate);
  endDate = endDate.businessDaysSubtract(publicHoliDays);
  startDate = endDate;
  if (publicHoliDays != 0) {
    reconcilePublicHoliDays(startDate, endDate);
  }
  return endDate;
};

const removeBusinessDays = (dateText, days) => {
  if (!dateText) {
    return 0;
  }
  let startDate = dayjs(dateText);
  let endDate = startDate.businessDaysSubtract(days);

  return revertReconciledPublicHolidays(startDate, endDate).format("YYYY-MM-DD");
};

const countWeekendDays = (startDate, endDate) =>
{  
  var ndays = 1 + Math.round((endDate.getTime()-startDate.getTime())/(24*3600*1000));
  var nsaturdays = Math.floor( (startDate.getDay()+ndays) / 7 );
  return 2*nsaturdays + (startDate.getDay()===0) - (endDate.getDay()===6);
}

const daysBetween = (startDate, endDate) => {
    var millisecondsPerDay = 24 * 60 * 60 * 1000;
    return (endDate - startDate) / millisecondsPerDay;
}
const calculateDaysRemaining = (endDate, startDate) => {	
	if (!startDate) {
		startDate = new Date();
	}
	else {
		startDate = new Date(startDate);
	}	
    endDate = new Date(endDate);	
	const publicHoliDays = getPublicHoliDays(startDate, endDate);
	const weekendDays = countWeekendDays(startDate, endDate);
	const noOfDays = daysBetween(startDate, endDate);
	return ((Math.round(noOfDays) - Math.round(publicHoliDays) - Math.round(weekendDays)) + 1);
}

const isMinistryCoordinator = (userdetail, ministryteam) => 
{

	if(userdetail === undefined || userdetail === null || userdetail === '' || userdetail.groups === undefined || userdetail.groups.length === 0 || ministryteam === undefined || ministryteam === '')
	{
		return false
	}

	if(userdetail.groups.indexOf("/Intake Team") != -1 || userdetail.groups.indexOf("/Flex Team") != -1 || userdetail.groups.indexOf("/Processing Team") != -1)
	{
		return false
	}
	else if(userdetail.groups.indexOf("/"+ministryteam) != -1)
	{
		return true
	}
	else{
		return false
	}

}

const isMinistryLogin = (userGroups) => {
	return Object.values(MINISTRYGROUPS).some(group => userGroups?.includes(group));
}

const getMinistryByValue = (userGroups) => {
	const ministryGroup = Object.values(MINISTRYGROUPS).filter(element => userGroups.includes(element));
	console.log("!!!",MINISTRYGROUPS);
	return Object.keys(MINISTRYGROUPS).find(key => MINISTRYGROUPS[key] === ministryGroup);
}

const encrypt = (obj) => {
	return CryptoJS.AES.encrypt(JSON.stringify(obj), SESSION_SECURITY_KEY).toString();
};

const decrypt = (encrypted) => {
	if(encrypted) {
		var bytes  = CryptoJS.AES.decrypt(encrypted, SESSION_SECURITY_KEY);
		return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
	} else {
		return {};
	}
};

const saveSessionData = (key, data) => {
	var expiresInMilliseconds = Date.now() + SESSION_LIFETIME;
	var sessionObject = {
		expiresAt: new Date(expiresInMilliseconds),
		sessionData: data
	}

	sessionStorage.setItem(key, encrypt(sessionObject));
};

const getSessionData = (key) => {
	var sessionObject = decrypt(sessionStorage.getItem(key));

	if(sessionObject && sessionObject.sessionData && sessionObject.expiresAt) {
		var currentDate = new Date();
		var expirationDate = sessionObject.expiresAt;

		if(Date.parse(currentDate) < Date.parse(expirationDate)) {
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
	if (!foiteam)
		return

	const _team = foiteam.toLowerCase();
	let currentMember;

	//fullname array (all teams) -> fullname value pairs
	let fullnameArray = getSessionData('fullnameList');
if(!Array.isArray(fullnameArray)) {
		fullnameArray = [];
	}
	
	//teams saved in fullnameList
	let fullnameTeamArray = getSessionData('fullnameTeamList');
	if(!Array.isArray(fullnameTeamArray)) {
		fullnameTeamArray = [];
	}
	
	//extract fullname and append to the array
if(Array.isArray(userArray)) {
		userArray?.forEach(team => {
	if(Array.isArray(team?.members)) {
			team.members?.forEach(member => {
			if(!fullnameArray.some(e => e.username === member.username)) {
					currentMember = {
						username: member.username,
						fullname: `${member.lastname}, ${member.firstname}`
					};
					fullnameArray.push(currentMember);  
				}
			});
		}
		});
	
		//save team name
		if(!fullnameTeamArray.includes(_team)) {
			fullnameTeamArray.push(_team);
			saveSessionData(`fullnameTeamList`, fullnameTeamArray);

			//save for assignedto or ministryassignto dropdown
			saveSessionData(`${_team}AssignToList`, userArray);
		}
	}	
	saveSessionData('fullnameList', fullnameArray);	
}

const getFullnameList = () => {
	return getSessionData('fullnameList');
}

const getAssignToList = (team) => {
	return getSessionData(`${team.toLowerCase()}AssignToList`);
}

const getFullnameTeamList = () => {
	return getSessionData('fullnameTeamList');
}

const ConditionalComponent = ({condition, children}) => {
	if(!condition) {
		return null
	}

	return <>
		{children}
	</>
}

const getMinistryCode = (userGroups) => {
	const ministryGroup = Object.values(MINISTRYGROUPS).find(element => userGroups?.includes(element));
	return Object.keys(MINISTRYGROUPS).find(key => MINISTRYGROUPS[key] === ministryGroup);
}

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
  getMinistryCode
};