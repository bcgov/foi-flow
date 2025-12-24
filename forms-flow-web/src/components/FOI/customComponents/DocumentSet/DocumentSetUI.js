import React, { useState, useEffect } from "react";
import { Paper, Radio } from "@material-ui/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faFolder,
  faCirclePlus,
  faInfoCircle,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";

import "./DocumentSet.css";
import { useDispatch } from "react-redux";

import {
  createFOIRecordGroup,updateFOIRecordGroup,getFOIRecordGroup
} from "../../../../apiManager/services/FOI/foiRecordServices";

export default function DocumentSetUI({
                                        records,
                                        requestId,
                                        ministryId,
                                        onSave
                                      }) {
  const [documentSets, setDocumentSets] = useState([]);
  const [selectedSet, setSelectedSet] = useState(null);
  const dispatch = useDispatch();

  useEffect(() => {
    getFOIRecordGroup(requestId, ministryId)
      .then(groups => {
        const sets = transformGroupsToDocumentSets(groups);
        if (sets.length > 0) {
          setDocumentSets(sets);
          setSelectedSet(sets[0].id);
        } else {
          const newSet = { id: "new-1", label: "Document Set 1" };
          setDocumentSets([newSet]);
          setSelectedSet("new-1");
        }
      });
  }, [requestId, ministryId]);

  function transformGroupsToDocumentSets(groups) {
    if (!Array.isArray(groups)) return [];
    console.log(groups);
    return groups.map((g) => ({
      id: g.documentsetid,
      label: g.name,
      ministryId: g.ministryrequestid
    }));
  }

  const hasIncompatibleFiles = () => {
    if (!records || records.length === 0) {
      return false;
    }

    return records.some(
      (record) => record?.attributes?.incompatible === true
    );
  };

  const handleSave = () => {
    const recordIds = records?.map((r) =>
      r.recordid ||
      r.recordId ||
      r.id ||
      r?.file?.recordid ||
      r?.file?.id
    ).filter(Boolean) || [];

    const isExisting = Number.isInteger(selectedSet);

    if (isExisting) {
      const group_id = documentSets.find((s) => s.id === selectedSet)?.id;
      const payload = {
        name: documentSets.find((s) => s.id === selectedSet)?.label,
        records: recordIds,
      };

      dispatch(
        updateFOIRecordGroup(requestId, ministryId, group_id, payload, (err, res) => {
          if (!err && typeof onSave === "function") {
            onSave();
          }
      }));

    } else {

      const payload = {
        name: documentSets.find(s => s.id === selectedSet)?.label || "",
        records: recordIds,
      };
      dispatch(
      createFOIRecordGroup(requestId, ministryId, payload, (err, res) => {
        if (!err && typeof onSave === "function") {
          onSave();
        }
      }));

    }
  };

  window._saveDocumentSet = handleSave;

  const addSet = () => {
    const nextId = documentSets.length + 1;

    setDocumentSets([
      ...documentSets,
      { id: `new-${nextId}`, label: `Document Set ${nextId}` },
    ]);

    setSelectedSet(`new-${nextId}`);
  };

  return (
    <div className="ds-body">
      {/* Subtitle */}
      <div className="ds-subtitle">
        The records you selected will be grouped into a set:
      </div>

      {/* Document Sets */}
      <div className="ds-set-list">
        {documentSets.map((set) => (
          <div key={set.id} className="ds-set-row">
            <Radio
              checked={selectedSet === set.id}
              onChange={() => setSelectedSet(set.id)}
              color="primary"
            />

            <div className="ds-pill" onClick={() => setSelectedSet(set.id)}>
        <span className="ds-pill-icon">
          <FontAwesomeIcon icon={faFolder} size="sm" color="#38598A" />
        </span>
              {set.label}
            </div>
          </div>
        ))}
      </div>


      {/* Add Document Set */}
      <div className="ds-add" onClick={addSet}>
        <FontAwesomeIcon icon={faCirclePlus} /> Add another document set
      </div>

      {/* Info Box */}
      <Paper elevation={0} className="ds-info">
        <div className="ds-section-title">
          <FontAwesomeIcon icon={faInfoCircle} /> What this does:
        </div>

        <ul>
          <li>
            Groups selected records into a “Document Set” that loads separately
            in the redaction app.
          </li>
          <li>Only records in the current set will be visible.</li>
          <li>Redlines and response packages will be created per set.</li>
        </ul>

        <div className="ds-section-title" style={{ marginTop: 8 }}>
          <FontAwesomeIcon icon={faInfoCircle} /> When to use:
        </div>

        <div className="ds-muted">
          Recommended if you're experiencing performance issues or having
          trouble creating record packages.
        </div>
      </Paper>

      {/* Incompatible File Error Panel */}
      {hasIncompatibleFiles() && (
        <Paper elevation={0} className="ds-alert">
          <div className="ds-alert-title">
            <FontAwesomeIcon icon={faExclamationCircle} />
            Error: file not added to document set
          </div>
          <div className="ds-alert-text">
            We noticed an issue with one of the files you selected. It contains
            an error and will not be included in your document set.
          </div>
        </Paper>
      )}
    </div>
  );
}
