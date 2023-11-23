import {
    httpGETRequest,
    httpPOSTRequest
  } from "../../httpRequestHandler";
  import API from "../../endpoints";
  import {
    serviceActionError,
    setFOILoader,
    setFOIAssignedToListLoader,
    setFOICategoryList,
    setFOIProgramAreaList,
    setFOIAssignedToList,
    setFOIProcessingTeamList,
    setFOIFullAssignedToList,
    setFOIMinistryAssignedToList,
    setFOIDeliveryModeList,
    setFOIReceivedModeList,
    setFOIMinistryDivisionalStages,
    setFOIPersonalDivisionsAndSections,
    setFOIPersonalSections,
    setClosingReasons,
    setFOISubjectCodeList,  
    setCommentTagListLoader, 
    setFOIAdminProgramAreaList,
    setOIPCOutcomes,
    setOIPCStatuses,
    setOIPCReviewtypes,
    setOIPCInquiryoutcomes,
  } from "../../../actions/FOI/foiRequestActions";
  import { fnDone, catchError } from "./foiServicesUtil";
  import UserService from "../../../services/UserService";
  import { replaceUrl, addToFullnameList, getAssignToList, getFullnameTeamList } from "../../../helper/FOI/helper";
  
  export const fetchFOICategoryList = () => {
    const firstCategory = { "applicantcategoryid": 0, "name": "Select Category" };
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_CATEGORIES_API, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const foiRequestCategoryList = res.data;
            let data = foiRequestCategoryList.map((category) => {
              return { ...category };
            });
            data.unshift(firstCategory);
            dispatch(setFOICategoryList(data));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching category master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching category master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };
  
  export const fetchFOIProgramAreaList = () => {    
    return (dispatch) => {
      httpGETRequest(
        API.FOI_GET_PROGRAMAREAS_FORUSER_API,
        {},
        UserService.getToken()
      )
        .then((res) => {
          if (res.data) {
            const foiProgramAreaList = res.data;
            let data = foiProgramAreaList.map((programArea) => {
              return { ...programArea, isChecked: false };
            });
            dispatch(setFOIProgramAreaList(data));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching program area master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching program area master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };
  
  
  export const fetchFOIAssignedToList = (requestType, status, bcgovcode) => {
    let apiUrlGETAssignedToList = API.FOI_GET_ASSIGNEDTO_INTAKEGROUP_LIST_API;
    if (requestType && status) {
      if (bcgovcode) {
      apiUrlGETAssignedToList = replaceUrl(replaceUrl(replaceUrl(
        API.FOI_GET_ASSIGNEDTOGROUPLIST_WITHGOVCODE_API,
        "<requesttype>",
        requestType
      ), "<curentstate>", status), "<bcgovcode>", bcgovcode);
      }     
    }
    return (dispatch) => {
      httpGETRequest(apiUrlGETAssignedToList, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const foiAssignedToList = res.data;
            let data = foiAssignedToList.map((assignedTo) => {
              return { ...assignedTo };
            });
            dispatch(setFOIAssignedToList(data));
            dispatch(setFOILoader(false));
          } else {
            console.log(`Error while fetching assigned to master data based on requestType ${requestType} and state ${status} `, res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching assigned to master data based on requestType ${requestType} and state ${status}", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchFOIProcessingTeamList = (requestType) => {
    let apiUrlGETAssignedToList = API.FOI_GET_ASSIGNEDTO_ALLGROUP_LIST_API;
    if (requestType) {
      apiUrlGETAssignedToList = replaceUrl(
        API.FOI_GET_PROCESSINGTEAMLIST_API,
        "<requesttype>",
        requestType
      );
    }
    return (dispatch) => {
      httpGETRequest(apiUrlGETAssignedToList, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const foiAssignedToList = res.data;
            let data = foiAssignedToList.map((assignedTo) => {
              return { ...assignedTo };
            });
            dispatch(setFOIProcessingTeamList(data));
            dispatch(setFOILoader(false));
          } else {
            console.log(
              `Error while fetching assigned to master data based on requestType ${requestType} `,
              res
            );
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log(
            `Error while fetching assigned to master data based on requestType ${requestType}`,
            error
          );
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchFOIFullAssignedToList = (...rest) => {
    let fullnameTeamArray = getFullnameTeamList();
    if (!fullnameTeamArray || !Array.isArray(fullnameTeamArray)) {
      fullnameTeamArray = [];
    }

    if (fullnameTeamArray.includes("iao")) {
      return (dispatch) => {
        dispatch(setFOIFullAssignedToList(getAssignToList("iao")));
        dispatch(setFOIAssignedToListLoader(false));
        dispatch(setCommentTagListLoader(false));
      };
    } else {
      const done = fnDone(rest);
      return (dispatch) => {
        httpGETRequest(
          API.FOI_GET_ASSIGNEDTO_ALLGROUP_LIST_API,
          {},
          UserService.getToken()
        )
          .then((res) => {
            if (res.data) {
              const foiFullAssignedToList = res.data;
              let data = foiFullAssignedToList.map((assignedTo) => {
                return { ...assignedTo };
              });
              addToFullnameList(data, "iao");
              dispatch(setFOIFullAssignedToList(data));
              dispatch(setFOIAssignedToListLoader(false));
              done(null, res.data);
            } else {
              console.log(
                "Error while fetching IAO assigned to master data",
                res
              );
              dispatch(serviceActionError(res));
              dispatch(setFOIAssignedToListLoader(false));
            }
            dispatch(setCommentTagListLoader(false));
          })
          .catch((error) => {
            console.log(
              "Error while fetching IAO assigned to master data",
              error
            );
            dispatch(serviceActionError(error));
            dispatch(setFOIAssignedToListLoader(false));
            dispatch(setCommentTagListLoader(false));
            done(error);
          });
      };
    }
  };
  
  export const fetchFOIMinistryAssignedToList = (govCode, ...rest) => {
  
    let fullnameTeamArray = getFullnameTeamList();
    if(!fullnameTeamArray || !Array.isArray(fullnameTeamArray)) {
      fullnameTeamArray = [];
    }
  
    if(fullnameTeamArray.includes(govCode.toLowerCase())) {
      return (dispatch) => {
        dispatch(setFOIMinistryAssignedToList(getAssignToList(govCode)));
        dispatch(setFOILoader(false));
      };
  
    } else {
      const done =fnDone(rest);
  
      const apiUrlGETAssignedToList = replaceUrl(
        API.FOI_GET_ASSIGNEDTO_MINISTRYGROUP_LIST_API,
        "<govcode>",
        govCode
      );
    
      return (dispatch) => {
        httpGETRequest(apiUrlGETAssignedToList, {}, UserService.getToken())
          .then((res) => {
            if (res.data) {
              const foiAssignedToList = res.data;
              let data = foiAssignedToList.map((assignedTo) => {
                return { ...assignedTo };
              });
              addToFullnameList(data, govCode);
              dispatch(setFOIMinistryAssignedToList(data));
              dispatch(setFOILoader(false));
              done(null, res.data);
            } else {
              console.log(`Error while fetching Ministry(${govCode}) assigned to master data`, res);
              dispatch(serviceActionError(res));
              dispatch(setFOILoader(false));
            }
          })
          .catch((error) => {
            console.log(`Error while fetching Ministry(${govCode}) assigned to master data`, error);
            dispatch(serviceActionError(error));
            dispatch(setFOILoader(false));
            done(error);
          });
      };
    }
  };
  
  export const fetchFOIDeliveryModeList = () => {
    const firstDeliveryMode = { "deliverymodeid": 0, "name": "Select Delivery Mode" };
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_DELIVERY_MODELIST, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const foiDeliveryModeList = res.data;
            let data = foiDeliveryModeList.map((deliveryMode) => {
              return { ...deliveryMode };
            });
            data.unshift(firstDeliveryMode);
            dispatch(setFOIDeliveryModeList(data));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching delivery mode master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching delivery mode master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };
  
  export const fetchFOIReceivedModeList = () => {
    const firstReceivedMode = { "receivedmodeid": 0, "name": "Select Received Mode" };
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_RECEIVED_MODELIST, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const foiReceivedModeList = res.data;
            let data = foiReceivedModeList.map((receivedMode) => {
              return { ...receivedMode };
            });
            data.unshift(firstReceivedMode);
  
            dispatch(setFOIReceivedModeList(data));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching received mode master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching received mode master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchClosingReasonList = () => {    
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_CLOSING_REASONS, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const closingReasons = res.data;
            dispatch(setClosingReasons(closingReasons));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching close request reason master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching close request reason master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchFOIMinistryDivisionalStages = (bcgovcode) => {
    const apiUrlgetdivisionalstages = replaceUrl(API.FOI_MINISTRY_DIVISIONALSTAGES, "<bcgovcode>", bcgovcode);
    return (dispatch) => {
      httpGETRequest(apiUrlgetdivisionalstages, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const foiMinistryDivisionalStages = res.data;
            dispatch(setFOIMinistryDivisionalStages({}));
            dispatch(setFOIMinistryDivisionalStages(foiMinistryDivisionalStages));
            dispatch(setFOILoader(false));
          } else {
            console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchFOIPersonalDivisionsAndSections = (bcgovcode) => {
    switch(bcgovcode) {
      case "MCF":
        const apiUrlMCF = replaceUrl(API.FOI_PERSONAL_SECTIONS, "<bcgovcode>", bcgovcode);
        return (dispatch) => {
          httpGETRequest(apiUrlMCF, {}, UserService.getToken())
            .then((res) => {
              if (res.data) {
                const foiPersonalSections = res.data;
                dispatch(setFOIPersonalSections({}));
                dispatch(setFOIPersonalSections(foiPersonalSections));
                dispatch(setFOILoader(false));
              } else {
                console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, res);
                dispatch(serviceActionError(res));
                dispatch(setFOILoader(false));
              }
            })
            .catch((error) => {
              console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, error);
              dispatch(serviceActionError(error));
              dispatch(setFOILoader(false));
            });
        };
      case "MSD":
        const apiUrlMSD = replaceUrl(API.FOI_PERSONAL_DIVISIONS_SECTIONS, "<bcgovcode>", bcgovcode);
        return (dispatch) => {
          httpGETRequest(apiUrlMSD, {}, UserService.getToken())
            .then((res) => {
              if (res.data) {
                const foiPersonalDivisionsAndSections = res.data;
                dispatch(setFOIPersonalDivisionsAndSections({}));
                dispatch(setFOIPersonalDivisionsAndSections(foiPersonalDivisionsAndSections));
                dispatch(setFOILoader(false));
              } else {
                console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, res);
                dispatch(serviceActionError(res));
                dispatch(setFOILoader(false));
              }
            })
            .catch((error) => {
              console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, error);
              dispatch(serviceActionError(error));
              dispatch(setFOILoader(false));
            });
        };
      default:
        break;
    }
  };

  export const fetchFOIPersonalDivisions = (bcgovcode) => {
    const apiUrl = replaceUrl(API.FOI_PERSONAL_DIVISIONS, "<bcgovcode>", bcgovcode);
    return (dispatch) => {
      httpGETRequest(apiUrl, {}, UserService.getToken())
      .then((res) => {
        if (res.data) {
          const foiMinistryDivisionalStages = res.data;
          dispatch(setFOIMinistryDivisionalStages({}));
          dispatch(setFOIMinistryDivisionalStages(foiMinistryDivisionalStages));
          dispatch(setFOILoader(false));
        } else {
          console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, res);
          dispatch(serviceActionError(res));
          dispatch(setFOILoader(false));
        }
      })
      .catch((error) => {
        console.log(`Error while fetching ministry(${bcgovcode}) divisional stage master data`, error);
        dispatch(serviceActionError(error));
        dispatch(setFOILoader(false));
      });
    };
  };

  export const fetchFOISubjectCodeList = () => {
    const firstSubjectCode = { "subjectcodeid": 0, "name": "Select Subject Code (if required)" };
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_SUBJECT_CODELIST, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const foiSubjectCodeList = res.data;
            let data = foiSubjectCodeList.map((subjectCode) => {
              return { ...subjectCode };
            });
            data.unshift(firstSubjectCode);
            dispatch(setFOISubjectCodeList(data));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching subject code master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching delivery mode master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchAllProgramAreasForAdmin = () => {    
    return (dispatch) => {
      httpGETRequest(
        API.FOI_GET_PROGRAMAREAS_API,
        {},
        UserService.getToken()
      )
        .then((res) => {
          if (res.data) {
            dispatch(setFOIAdminProgramAreaList(res.data));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching program area master data for admin dashboard", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching program area master data for admin dashboard", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const refreshRedisCacheForAdmin = (...rest) => {
    const done = fnDone(rest);
    return (dispatch) => {
      httpPOSTRequest(API.FOI_REFRESH_REDIS_CACHE,{}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            done(null, res.data);
          } else {
            dispatch(serviceActionError(res));
            throw new Error("Error Refreshing Cache");
          }
        })
        .catch((error) => {
          done(error);
          catchError(error, dispatch);
        });
    };
  };

  export const fetchOIPCOutcomes = () => {    
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_OIPC_OUTCOMES, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const oipcOutcomes = res.data;
            dispatch(setOIPCOutcomes(oipcOutcomes));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching OIPC outcomes master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching OIPC outcomes master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchOIPCStatuses = () => {    
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_OIPC_STATUSES, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const oipcStatuses = res.data;
            dispatch(setOIPCStatuses(oipcStatuses));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching OIPC statuses master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching OIPC statuses master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchOIPCReviewtypes = () => {    
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_OIPC_REVIEWTYPES, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const oipcReviewtypes = res.data;
            dispatch(setOIPCReviewtypes(oipcReviewtypes));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching OIPC reviewtypes master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching OIPC reviewtypes master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };

  export const fetchOIPCInquiryoutcomes = () => {    
    return (dispatch) => {
      httpGETRequest(API.FOI_GET_OIPC_INQUIRYOUTCOMES, {}, UserService.getToken())
        .then((res) => {
          if (res.data) {
            const oipcInquiryoutcomes = res.data;
            dispatch(setOIPCInquiryoutcomes(oipcInquiryoutcomes));
            dispatch(setFOILoader(false));
          } else {
            console.log("Error while fetching OIPC inqiuryoutcomes master data", res);
            dispatch(serviceActionError(res));
            dispatch(setFOILoader(false));
          }
        })
        .catch((error) => {
          console.log("Error while fetching OIPC inqiuryoutcomes master data", error);
          dispatch(serviceActionError(error));
          dispatch(setFOILoader(false));
        });
    };
  };
  