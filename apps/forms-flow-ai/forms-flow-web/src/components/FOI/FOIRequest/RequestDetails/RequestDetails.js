import React, { useState } from "react";
import { ActionProvider } from "./ActionContext";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import TextField from "@material-ui/core/TextField";
import Input from "@material-ui/core/Input";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import { StateEnum } from "../../../../constants/FOI/statusEnum";

const RequestDetailsBox = React.memo(({ requestDetails }) => {
  const { modalOpen, setModalOpen } = useContext(ActionContext);

  useEffect(() => {
    console.log(modalOpen);
  }, [modalOpen]);

  return (
    <ActionProvider>
      <Card className="foi-details-card">
        <div className="row foi-details-row">
          <div className="col-lg-8 foi-details-col ">
            <label className="foi-details-label">REQUEST DETAILS</label>
          </div>
          <div className="col-lg-4 foi-details-col ">
            <button onClick={() => setModalOpen(modalOpen)}>
              <a href="#" className="foi-floatright foi-link">
                New Extension
              </a>
            </button>
          </div>
        </div>
        <CardContent>
          <div className="row foi-details-row">
            <div className="col-lg-6 foi-details-col">
              <TextField
                id="requestType"
                label="Request Type"
                InputLabelProps={{ shrink: true }}
                select
                // value={selectedRequestType}
                // onChange={handleRequestTypeChange}
                input={<Input />}
                variant="outlined"
                fullWidth
                required
                // disabled={disableInput}
                // error={selectedRequestType.toLowerCase().includes("select")}
              >
                {requestTypes}
              </TextField>
              <TextField
                id="receivedMode"
                label="Received Mode"
                InputLabelProps={{ shrink: true }}
                select
                // value={selectedReceivedMode}
                // onChange={handleReceivedModeChange}
                input={<Input />}
                variant="outlined"
                fullWidth
                required
                // error={selectedReceivedMode.toLowerCase().includes("select")}
              >
                {/* {receivedModes} */}
              </TextField>
              <TextField
                id="deliveryMode"
                label="Delivery Mode"
                InputLabelProps={{ shrink: true }}
                select
                // value={selectedDeliveryMode}
                // onChange={handleDeliveryModeChange}
                input={<Input />}
                variant="outlined"
                fullWidth
                required
                // disabled={disableInput}
                error={selectedDeliveryMode.toLowerCase().includes("select")}
              >
                {/* {deliveryModes} */}
              </TextField>
            </div>
            <div className="col-lg-6 foi-details-col">
              <TextField
                label="Received Date"
                type="date"
                // value={receivedDateText || ""}
                // onChange={handleReceivedDateChange}
                InputLabelProps={{
                  shrink: true,
                }}
                variant="outlined"
                required
                // error={
                //   receivedDateText === undefined || receivedDateText === ""
                // }
                fullWidth
              />
              <TextField
                label="Start Date"
                type="date"
                // value={startDateText || ""}
                // onChange={handleStartDateChange}
                InputLabelProps={{
                  shrink: true,
                }}
                InputProps={{ inputProps: { min: receivedDateText } }}
                variant="outlined"
                required
                // error={startDateText === undefined || startDateText === ""}
                fullWidth
                // disabled={!!ministryId || disableInput}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </ActionProvider>
  );
});

export default RequestDetailsBox;
