const replaceUrl = (URL, key, value) => {
    return URL.replace(key, value);
  };
  const formatDate = (d) => {
    if(d !== "") {
      let ye = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(d);
      let mo = new Intl.DateTimeFormat('en', { month: '2-digit' }).format(d);
      let da = new Intl.DateTimeFormat('en', { day: '2-digit' }).format(d);
      return `${ye}-${mo}-${da}`;
    }
  }
  export { replaceUrl, formatDate };
  