import dayjs from 'dayjs';
import DateHolidayjs from 'date-holidays';
import dayjsBusinessDays from 'dayjs-business-days';
var isBetween = require('dayjs/plugin/isBetween')
dayjs.extend(isBetween);
dayjs.extend(dayjsBusinessDays);
const hd = new DateHolidayjs('CA','BC');

const replaceUrl = (URL, key, value) => {
  return URL.replace(key, value);
};
const formatDate = (d) => {
  if(d !== "") {
    var _d= new Date(d)
    let ye = new Intl.DateTimeFormat('en-US', { year: 'numeric' }).format(_d);
    let mo = new Intl.DateTimeFormat('en-US', { month: '2-digit' }).format(_d);
    let da = new Intl.DateTimeFormat('en-US', { day: '2-digit' }).format(_d);
    return `${ye}-${mo}-${da}`;
  }
}
const getPublicHoliDays = (startDate, endDate) => {
	let publicHoliDays = 0;
	let years = [];
	years.push(dayjs(startDate).year());
	if(years.includes(dayjs(endDate).year()) === false) {
		years.push(dayjs(endDate).year());
	}
	for(const year of years) {
		const holidays = hd.getHolidays(year);
		for (const entry of holidays) {			
			if(entry.type === "public" && dayjs(entry.date).isBetween(startDate, endDate, null, '[]')) {
				publicHoliDays++;
			}		
		}
	}
	return publicHoliDays;
}
const reconcilePublicHoliDays = (startDate, endDate) => {	
	while(true) {		
		let publicHoliDays = getPublicHoliDays(startDate,endDate);		
		if(publicHoliDays === 0) {
			break;
		}
		startDate = endDate;
		endDate = endDate.businessDaysAdd(publicHoliDays);
		
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
    return (new Date(endDate) - new Date(startDate)) / millisecondsPerDay;
}
const calculateDaysRemaining = (endDate) => {
	const startDate = new Date();
    endDate = new Date(endDate);
	const publicHoliDays = getPublicHoliDays(startDate, endDate);
	const weekendDays = countWeekendDays(startDate, endDate);
	const noOfDays = daysBetween(startDate, endDate);   
	return Math.round(noOfDays) - Math.round(publicHoliDays) - Math.round(weekendDays);
}

export { replaceUrl, formatDate, addBusinessDays, calculateDaysRemaining };
