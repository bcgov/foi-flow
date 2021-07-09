import FOI_ACTION_CONSTANTS from './foiActionConstants'

export const setFOILoader = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.IS_LOADING,
        payload:data
    })
}

export const setFOIUpdateLoader = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_IS_REQUEST_UPDATING,
        payload:data
    })
}

//TODO Update set to get on below cases

export const setFOIRequestList = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_LIST_REQUESTS,
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

export const serviceActionError = (data) => dispatch => {
   //TODO update to a common file
    dispatch({
      type: FOI_ACTION_CONSTANTS.ERROR,
      payload: 'Error Handling API'
    })
}

