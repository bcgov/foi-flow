import FOI_ACTION_CONSTANTS from './foiActionConstants'

export const setFOILoader = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.IS_LOADING,
        payload:data
    })
}

export const setFOIAssignedToListLoader = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.IS_ASSIGNEDTOLIST_LOADING,
        payload:data
    })
}

export const setFOIUpdateLoader = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_IS_REQUEST_UPDATED,
        payload:data
    })
}

export const setFOIRequestList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS,
        payload:data
    })
}

export const setFOIMinistryRequestList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_MINISTRY_REQUESTSLIST,
        payload:data
    })
}

export const setFOIRequestCount = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_REQUESTS_COUNT,
        payload:data
    })
}
export const setFOIRequestDetail = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_REQUEST_DETAIL,
        payload:data
    })
}

export const setFOIMinistryViewRequestDetail = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_MINISTRYVIEW_REQUEST_DETAIL,
        payload:data
    })
}

export const serviceActionError = (data) => dispatch => {
   //TODO update to a common file
    dispatch({
      type: FOI_ACTION_CONSTANTS.ERROR,
      payload: 'Error Handling API'
    })
}

export const setFOICategoryList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_CATEGORYLIST,
        payload:data
    })
}
export const setFOICountryList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_COUNTRYLIST,
        payload:data
    })
}
export const setFOIProvinceList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_PROVINCELIST,
        payload:data
    })
}
export const setFOIRequestTypeList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_REQUEST_TYPELIST,
        payload:data
    })
}
export const setFOIReceivedModeList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_RECEIVED_MODELIST,
        payload:data
    })
}
export const setFOIDeliveryModeList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_DELIVERY_MODELIST,
        payload:data
    })
}
export const setFOIAssignedToList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_ASSIGNED_TOLIST,
        payload:data
    })
}

export const setFOIFullAssignedToList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_FULL_ASSIGNED_TOLIST,
        payload:data
    })
}

export const setFOIMinistryAssignedToList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_MINISTRY_ASSIGNED_TOLIST,
        payload:data
    })
}

export const setFOIProgramAreaList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_PROGRAM_AREALIST,
        payload:data
    })
}
export const clearRequestDetails = (data) => dispatch => {
    dispatch({
        type:FOI_ACTION_CONSTANTS.CLEAR_REQUEST_DETAILS,
        payload:data      
    })
}


export const clearMinistryViewRequestDetails = (data) => dispatch => {
    dispatch({
        type:FOI_ACTION_CONSTANTS.CLEAR_MINISTRYVIEWREQUEST_DETAILS,
        payload:data      
    })
}

export const setFOIRequestDescriptionHistory = (data) => dispatch => {
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_REQUEST_DESCRIPTION_HISTORY,
        payload:data      
    })
}
