import axios from "axios";
import UserService from "../../services/UserService";

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

export const httpOSSGETRequest = (url, requestOptions) => {
  return axios.get(url, requestOptions);
};

export const httpOSSPUTRequest = (url, data, requestOptions) => {  
  return axios.put(url, data, requestOptions);
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

export const httpDELETERequest = (url, data, token, isBearer = true) => {
  return axios.delete(url, data, {
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

