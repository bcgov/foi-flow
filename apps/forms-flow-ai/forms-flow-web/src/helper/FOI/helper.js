import dayjs from 'dayjs';
import DateHolidayjs from 'date-holidays';
import dayjsBusinessDays from 'dayjs-business-days';
import { format, utcToZonedTime } from 'date-fns-tz';
import MINISTRYGROUPS from '../../constants/FOI/foiministrygroupConstants';
var isBetween = require('dayjs/plugin/isBetween')
var utc = require("dayjs/plugin/utc")
var timezone = require("dayjs/plugin/timezone")

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
const getPublicHoliDays = (startDate, endDate) => {
	let publicHoliDays = 0;
	let years = [];
	years.push(dayjs(startDate).year());
	if(years.includes(dayjs(endDate).year()) === false) {
		years.push(dayjs(endDate).year());
	}
	for(const year of years) {
		let holidays = hd.getHolidays(year);
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
	let startDate = dayjs(dateText);	
	let endDate = startDate.businessDaysAdd(days);
	return reconcilePublicHoliDays(startDate,endDate).format('YYYY-MM-DD');	
}

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
	if (!startDate)
		startDate = new Date();
	else
		startDate = new Date(startDate);
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
	return Object.values(MINISTRYGROUPS).some(group => userGroups.includes(group));
}

const getMinistryByValue = (userGroups) => {
	const ministryGroup = Object.values(MINISTRYGROUPS).filter(element => userGroups.includes(element));
	return Object.keys(MINISTRYGROUPS).find(key => MINISTRYGROUPS[key] === ministryGroup);
}

const addToFullnameList = (userArray, team) => {
	if(team) {
		let currentMember;

		//fullname array for username -> fullname value pairs
		let fullnameArray = JSON.parse(sessionStorage.getItem('fullnameList'));
		if(!fullnameArray || !Array.isArray(fullnameArray)) {
			fullnameArray = [];
		}
	
		//teams saved in fullnameList
		let fullnameTeamArray = JSON.parse(sessionStorage.getItem('fullnameTeamList'));
		if(!fullnameTeamArray || !Array.isArray(fullnameTeamArray)) {
			fullnameTeamArray = [];
		}
	
		if(userArray && Array.isArray(userArray)) {
			userArray.forEach(team => {
				if(team && team.members && Array.isArray(team.members)) {
					team.members.forEach(member => {
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
	
			if(!fullnameTeamArray.includes(team)) {
				fullnameTeamArray.push(team);
			}
		}
	
		sessionStorage.setItem('fullnameList', JSON.stringify(fullnameArray));
	}
}

const getFullnameList = () => {
	return JSON.parse(sessionStorage.getItem('fullnameList'));
}

export { replaceUrl, formatDate, businessDay, addBusinessDays, calculateDaysRemaining, isMinistryCoordinator, isMinistryLogin, getMinistryByValue, addToFullnameList, getFullnameList };
