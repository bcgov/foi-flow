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
const getObserveDays = (startDate, endDate) => {
	let observeDays = 0;
	let years = [];
	years.push(dayjs(startDate).year());
	if(years.includes(dayjs(endDate).year()) === false) {
		years.push(dayjs(endDate).year());
	}
	for(const year of years) {
		const holidays = hd.getHolidays(year);
		for (const entry of holidays) {
			const day = dayjs(entry.date).day();
			if(entry.type === "public" && (day === 6 || day === 0) && dayjs(entry.date).isBetween(startDate, endDate, null, '[]')) {
				console.log(entry.date);
				observeDays++;
			}		
		}
	}
	return observeDays;
}
const reconcileObserveDays = (startDate, endDate) => {	
	while(true) {		
		let reconcileDays = getObserveDays(startDate,endDate);		
		if(reconcileDays === 0) {
			break;
		}
		startDate = endDate;
		endDate = endDate.businessDaysAdd(reconcileDays);
		
	}
	return endDate;
}
const addBusinessDays = (dateText, days) => {
let startDate = dayjs(dateText);   
let endDate = startDate.businessDaysAdd(days);
return reconcileObserveDays(startDate,endDate).format('YYYY-MM-DD');	
}
export { replaceUrl, formatDate, addBusinessDays };
