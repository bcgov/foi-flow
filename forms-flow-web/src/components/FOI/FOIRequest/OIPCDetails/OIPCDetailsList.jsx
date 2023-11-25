import OIPCItem from "./OIPCItem";
import Divider from '@material-ui/core/Divider';
import './oipcdetails.scss';

const OIPCDetailsList = (props) => {
    const {oipcData, removeOIPC, updateOIPC} = props;

    console.log("COMPONENT", oipcData)
    const OIPCItems = oipcData?.map((oipcObj, index) => {
        return (
            <>  
                <OIPCItem oipcObj={oipcObj} key={oipcObj.id} updateOIPC={updateOIPC} removeOIPC={removeOIPC} />
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