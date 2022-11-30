import CountryList from './CountryProvinceList.json';

const getCountryList = () => {
    const countryList = CountryList.map(country => country.name);
    countryList.unshift("Select Country");
    return countryList;
}

const getProvinceList = (countryName) => {
    const [provinceList] = CountryList.filter(country => country.name === countryName);
    let provinceNameList = [];
    if (provinceList !== undefined) {
        provinceNameList = provinceList.states.map(province => province.name);        
    }
    provinceNameList.unshift("Select Province");
    return provinceNameList;
}

export {getCountryList, getProvinceList}