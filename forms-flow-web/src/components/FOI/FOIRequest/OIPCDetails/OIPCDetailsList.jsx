import OIPCItem from "./OIPCItem";

const OIPCDetailsList = (props) => {
    const {oipcData} = props;

    const OIPCItems = oipcData?.map((oipcObj, index) => {
        return (
            <OIPCItem oipcObj={oipcObj} key={index}/>
        );
    });

    return (
        <div>
            {OIPCItems}
        </div>
    );
}

export default OIPCDetailsList;