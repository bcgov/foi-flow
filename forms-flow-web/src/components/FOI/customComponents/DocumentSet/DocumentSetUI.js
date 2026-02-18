import React, { useState, useEffect } from "react";
import { Paper, Radio, Tooltip } from "@material-ui/core"; // Import Tooltip
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

const MAX_DOCUMENT_SETS = 20; // Define the maximum number of document sets allowed

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
    return groups.map((g) => ({
      id: g.documentsetid,
      label: g.name,
      ministryId: g.ministryrequestid
    }));
  }

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
    if (documentSets.length >= MAX_DOCUMENT_SETS) {
      console.warn(`Cannot add more than ${MAX_DOCUMENT_SETS} document sets.`);
      return;
    }

    const existingUnsavedSet = documentSets.find(set => typeof set.id === 'string' && set.id.startsWith('new-'));

    if (existingUnsavedSet) {
      setSelectedSet(existingUnsavedSet.id);
      return;
    }

    const nextId = documentSets.length + 1;
    const newSet = { id: `new-${nextId}`, label: `Document Set ${nextId}` };

    setDocumentSets([
      ...documentSets,
      newSet,
    ]);

    setSelectedSet(newSet.id);
  };

  const isLimitReached = documentSets.length >= MAX_DOCUMENT_SETS;

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
              onClick={() => setSelectedSet(set.id)}
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
      <Tooltip
        title={isLimitReached ? `Maximum of ${MAX_DOCUMENT_SETS} document sets reached` : 'Add another document set'}
        placement="right"
        componentsProps={{
          tooltip: {
            sx: {
              fontSize: "16px",
              padding: "10px 14px",
              maxWidth: "450px",
            },
          },
        }}
      >
        <div
          className={`ds-add ${isLimitReached ? 'ds-add-disabled' : ''}`}
          onClick={isLimitReached ? null : addSet}
        >
          <FontAwesomeIcon icon={faCirclePlus} /> Add another document set
        </div>
      </Tooltip>

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

        <div className="ds-muted">
          For optimal performance, it is recommended a document set not exceed:
        </div>
        <div className="ds-muted">
          <ul>
            <li>500 files</li>
            <li>1GB in total file size</li>
          </ul>
        </div>
      </Paper>
    </div>
  );
}
