import OIPCItem from "./OIPCItem";
import Divider from '@material-ui/core/Divider';
import './oipcdetails.scss';
import Button from '@material-ui/core/Button';

const OIPCDetailsList = (props) => {
    const {oipcData, removeOIPC} = props;
    console.log("TEST THIS", oipcData);

    const OIPCItems = oipcData?.map((oipcObj, index) => {
        return (
            <>
                <OIPCItem oipcObj={oipcObj} key={oipcObj.oipcNumber} removeOIPC={removeOIPC} />
                <Button size="small" onClick={() => removeOIPC(oipcObj.oipcNumber)} style={{color: "red"}}>Delete</Button>
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