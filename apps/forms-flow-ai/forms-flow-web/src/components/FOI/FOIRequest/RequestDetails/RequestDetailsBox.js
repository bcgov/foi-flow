import React, { useState, useEffect, useContext } from "react";
import { ActionContext } from "./ActionContext";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import TextField from "@material-ui/core/TextField";
import Input from "@material-ui/core/Input";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import { StateEnum } from "../../../../constants/FOI/statusEnum";
import AddExtensionModal from "./AddExtensionModal"

const RequestDetailsBox = React.memo(() => {
  const { modalOpen, setModalOpen } = useContext(ActionContext);
  return (
    <>
      <Card className="foi-details-card">
        <div className="row foi-details-row">
          <div className="col-lg-8 foi-details-col ">
            <label className="foi-details-label">REQUEST DETAILS</label>
          </div>
          <div className="col-lg-4 foi-details-col ">
            <a
              href="#"
              className="foi-floatright foi-link"
              onClick={(e) => {
                e.preventDefault();
                setModalOpen(true);
              }}
            >
              New Extension
            </a>
          </div>
        </div>
        <CardContent>
          <div className="row foi-details-row">
            <div className="col-lg-6 foi-details-col"></div>
            <div className="col-lg-6 foi-details-col"></div>
          </div>
        </CardContent>
      </Card>
      <AddExtensionModal/>
    </>
  );
});

export default RequestDetailsBox;
