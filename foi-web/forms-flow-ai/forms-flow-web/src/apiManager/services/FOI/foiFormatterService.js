export const foiRequestDataFormatter = (requestData) =>{
    const res = {};
    requestData.forEach(request => res[request.applicantName] = request.value); //need to revisit once the api is ready
    return res;
  }