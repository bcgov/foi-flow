import {
  httpPOSTRequest,
  httpGETRequest,
} from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  serviceActionError,
  setRestrictedReqTaglist
} from "../../../actions/FOI/foiRequestActions";
import { catchError, fnDone} from './foiServicesUtil';
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";

export const fetchPotentialApplicants = (firstname, lastname, email, phone, ...rest) => {
  // console.log("fetch applicants" + firstname)
  // console.log(firstname)
  // console.log(lastname)
  
  const done = fnDone(rest);
  // await new Promise(resolve => {setTimeout(resolve, 3000)});
  // done(null, [
  //   { id: 1, lastName: 'Snow', firstName: 'Jon', age: 35 },
  //   { id: 2, lastName: 'Lannister', firstName: 'Cersei', age: 42 },
  //   { id: 3, lastName: 'Lannister', firstName: 'Jaime', age: 45 },
  //   { id: 4, lastName: 'Stark', firstName: 'Arya', age: 16 },
  //   { id: 5, lastName: 'Targaryen', firstName: 'Daenerys', age: null },
  //   { id: 7, lastName: 'Clifford', firstName: 'Ferrara', age: 44 },
  //   { id: 8, lastName: 'Frances', firstName: 'Rossini', age: 36 },
  //   { id: 9, lastName: 'Roxie', firstName: 'Harvey', age: 65 },
  // ]);
  // return;
  const apiUrlgetRequestDetails = replaceUrl(
    API.FOI_GET_REQUEST_APPLICANTS,
    "<email>",
    email
  );
  return (dispatch) => {
    httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          done(null, res.data)
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error in fetching potential applicants`)
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const fetchApplicantInfo = async (firstname, ...rest) => {
  
  const done = fnDone(rest);
  done(null, 
    { id: 1, lastName: 'Snow', firstName: 'Jon', age: 35, email: 'jon.snow@gmail.com',
     additionalPersonalInfo: {birthDate: "2023-12-07"},
     requestHistory: [{requestId: "EDU-2023-234345", receivedDate: "2023-12-07", currentState: "Open", requestDescription: "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but als"}]  
    }
  );
  return;
  // const apiUrlgetRequestDetails = replaceUrl(replaceUrl(
  //   API.FOI_MINISTRYVIEW_REQUEST_API,
  //   "<requestid>",
  //   requestId
  // ), "<ministryid>", ministryId);
  // return (dispatch) => {
  //   httpGETRequest(apiUrlgetRequestDetails, {}, UserService.getToken())
  //     .then((res) => {
  //       if (res.data) {
  //         const foiRequest = res.data;
  //         dispatch(clearMinistryViewRequestDetails({}));
  //         dispatch(setFOIMinistryViewRequestDetail(foiRequest));
  //         dispatch(fetchFOIMinistryAssignedToList(foiRequest.selectedMinistries[0].code.toLowerCase()));
  //         dispatch(setFOILoader(false));
  //       } else {
  //         dispatch(serviceActionError(res));
  //         dispatch(setFOILoader(false));
  //         throw new Error(`Error in fetching ministry request details for request# ${requestId} ministry# ${ministryId}`)
  //       }
  //     })
  //     .catch((error) => {
  //       catchError(error, dispatch);
  //     });
  // };
};

export const fetchApplicantContactHistory = (...rest) => {
  const done = fnDone(rest);
  done(null, 
    [{ 
      field: "Email",
      value: "a@b.ca",
      date: "2023-12-11",
      username: "foiintake@idir",
    }]
  );
}

export const saveApplicantInfo = (applicant, ...rest) => {
  const done = fnDone(rest);
  const apiUrlgetRequestDetails = API.FOI_SAVE_REQUEST_APPLICANT_INFO;
  return (dispatch) => {
    httpPOSTRequest(apiUrlgetRequestDetails, applicant, UserService.getToken())
      .then((res) => {
        if (res.data) {
          dispatch(setRestrictedReqTaglist(res.data));
          done(null, res.data);
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error in saving applicant`);
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  }
};

export const fetchApplicantProfileByKeyword = (keywords, ...rest) => {
  const done = fnDone(rest);
  const apiUrl = API.FOI_REQUEST_APPLICANTS_SEARCH_KEYWORDS;
  return (dispatch) => {
    httpPOSTRequest(apiUrl, keywords, UserService.getToken())
      .then((res) => {
        if (res.data) {
          done(null, res.data)
        } else {
          dispatch(serviceActionError(res));
          throw new Error(`Error in fetching potential applicants`)
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  }
};