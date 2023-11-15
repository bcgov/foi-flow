const OIPCDetailsList = (props) => {
    const {oipcData} = props;
    const OIPCItems = oipcData?.map((oipcObj, index) => {
        return oipcObj.oipcNumber;
    })

    return (
        <>
            {OIPCItems}
        </>
    );
}

export default OIPCDetailsList;