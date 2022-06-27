import FOI_ACTION_CONSTANTS from './foiActionConstants'
export const setFOINotifications = (data) => dispatch =>{
    dispatch({
        type:FOI_ACTION_CONSTANTS.FOI_NOTIFICATIONS,
        payload:data
    })
}