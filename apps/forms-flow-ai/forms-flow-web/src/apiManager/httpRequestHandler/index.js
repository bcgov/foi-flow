import axios from "axios";

import UserService from "../../services/UserService";

// const qs = require("querystring");

export const httpGETRequest = (url, data, token, isBearer = true) => {
  return axios.get(url, {
    params: data,
    headers: {
      Authorization: isBearer
        ? `Bearer ${token || UserService.getToken()}`
        : token,
    },
  });
};

export const httpOpenGETRequest = (url) => {
  return axios.get(url);
};

export const httpOpenPOSTRequest = (url, data) => {
  const axiosConfig = {
    headers: {
        'Content-Type': 'application/json'              
    }
  };
  return axios.post(url, data, axiosConfig);
};

export const httpPOSTRequest = (url, data, token, isBearer = true) => {
  return axios.post(url, data, {
    headers: {
      Authorization: isBearer
        ? `Bearer ${token || UserService.getToken()}`
        : token,
    },
  });
};

export const httpPUTRequest = (url, data, token, isBearer = true) => {
  return axios.put(url, data, {
    headers: {
      Authorization: isBearer
        ? `Bearer ${token || UserService.getToken()}`
        : token,
    },
  });
};

/*export const httpPUTRequest = (url, data, token, isBearer=true) => {
  return axios.put(url, data, { headers: { Authorization: isBearer ?`Bearer ${ token || UserService.getToken()}`: token } });
};*/

/*export const httpPOSTRequestWithoutToken = (url, data) => {
  const config = {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  };
  return axios.post(url, qs.stringify(data), config);
};

export const httpGETRequestWithoutToken = (url, token) => {
  return axios.get(url);
};*/
