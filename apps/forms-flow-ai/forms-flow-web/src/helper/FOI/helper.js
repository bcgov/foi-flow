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
export { replaceUrl, formatDate };
