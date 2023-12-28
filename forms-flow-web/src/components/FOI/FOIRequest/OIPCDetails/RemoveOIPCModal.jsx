import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import useOIPCHook from './oipcHook';
import { deleteOIPCDetails } from '../../../../apiManager/services/FOI/foiRequestServices';
import { useDispatch } from 'react-redux';
import { toast } from "react-toastify";
import { useParams } from "react-router-dom";

const RemoveOIPCModal= ({
    showModal,
    removeOIPC,
    setShowModal,
    oipc,
}) =>{ 
    const dispatch = useDispatch();
    const { requestId, ministryId } = useParams();
    const { setIsOIPCReview, removeAllOIPCs } = useOIPCHook();
    const saveOIPCNoReview = () => {
        const toastID = toast.loading("Saving request with removed OIPC review...")
        removeAllOIPCs();
        setIsOIPCReview(false);
        dispatch(
            deleteOIPCDetails(
                requestId,
                ministryId,
                (err, _res) => {
                if(!err) {
                toast.update(toastID, {
                    type: "success",
                    render: "Removal of OIPC review has been saved successfully.",
                    position: "top-right",
                    isLoading: false,
                    autoClose: 3000,
                    hideProgressBar: true,
                    closeOnClick: true,
                    pauseOnHover: true,
                    draggable: true,
                    progress: undefined,
                });
                } else {
                toast.error(
                    "Temporarily unable to save the request with removed OIPC review. Please try again in a few minutes.",
                    {
                    position: "top-right",
                    autoClose: 3000,
                    hideProgressBar: true,
                    closeOnClick: true,
                    pauseOnHover: true,
                    draggable: true,
                    progress: undefined,
                    }
                );}
            })
        )
    }

    const handleSave = () => {
        setShowModal(false);
        removeOIPC(oipc.id)
        saveOIPCNoReview();
    };
    const handleClose = () => {
        setShowModal(false);
    };

    return (  
        <div className="state-change-dialog">
            <Dialog
            open={showModal}
            onClose={handleClose}
            maxWidth={'md'}
            fullWidth={true}
            >
            <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">Remove OIPC</h2>
              <IconButton className="title-col3" onClick={handleClose}>
                <i className="dialog-close-button">Close</i>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent>
                <DialogContentText component={'span'}>
                    <span className="confirmation-message" style={{display: "flex", flexDirection: "row", justifyContent: "center", color: "black"}}>
                        Are you sure you want to delete this OIPC Review? The request will be saved automatically if you continue.
                    </span>
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <button
                className={`btn-bottom btn-save btn`}
                onClick={handleSave}
                >
                Continue
                </button>
                <button className="btn-bottom btn-cancel" onClick={handleClose}>
                Cancel
                </button>
            </DialogActions>
            </Dialog>
        </div>
    );
};

export default RemoveOIPCModal;
