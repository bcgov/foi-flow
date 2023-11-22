import OIPCItem from "./OIPCItem";
import Divider from '@material-ui/core/Divider';
import './oipcdetails.scss';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash } from '@fortawesome/free-solid-svg-icons';

const OIPCDetailsList = (props) => {
    const {oipcData, removeOIPC, updateOIPC} = props;

    const OIPCItems = oipcData?.map((oipcObj, index) => {
        return (
            <>
                <div style={{display: "flex", flexDirection: "row", justifyContent: "flex-end"}}>
                    <button onClick={() => removeOIPC(oipcObj.id)} style={{ border: "none", background: "none" }}>
                        <FontAwesomeIcon icon={faTrash} color="#38598A" />
                    </button>
                </div>
                <OIPCItem oipcObj={oipcObj} key={oipcObj.id} updateOIPC={updateOIPC} />
                {index !== (oipcData.length - 1)  && <Divider/>}
            </>
        );
    });

    return (
        <div>
            {OIPCItems}
        </div>
    );
}

export default OIPCDetailsList;