import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { useDispatch, useSelector } from "react-redux";
import OpenInfo from "./OpenInfo";

jest.mock("react-redux", () => ({ useDispatch: jest.fn(), useSelector: jest.fn() }));
jest.mock("../../../../apiManager/services/FOI/foiOpenInfoRequestServices", () => ({}));
jest.mock("./OpenInfoHeader", () => () => null);
jest.mock("./OpenInfoTab", () => () => null);
jest.mock("./Exemption/IAOOpenInfoPublishing", () => () => null);
jest.mock("./Publication/OpenInfoPublication", () => ({
  handleOIDataChange, confirmModal, oiPublicationData,
}: any) => (
  <>
    <input
      aria-label="Publication date"
      type="date"
      value={oiPublicationData.publicationdate || ""}
      onChange={(event) => handleOIDataChange(event.target.value, "publicationdate")}
    />
    {confirmModal.show && <div role="alert">{confirmModal.description}</div>}
  </>
));

const state = {
  foiRequests: {
    foiFullAssignedToList: [],
    foiOpenInfoAdditionalFiles: [],
    foiOpenInfoRequest: { oipublicationstatus_id: 1, publicationdate: null },
    oiPublicationStatuses: [
      { name: "Publish", oipublicationstatusid: 1 },
      { name: "Do Not Publish", oipublicationstatusid: 2 },
    ],
  },
};

beforeEach(() => {
  (useDispatch as jest.Mock).mockReturnValue(jest.fn());
  (useSelector as jest.Mock).mockImplementation((selector) => selector(state));
});

test.each([
  ["2026-11-23", true], // Nine business days after Nov 9, excluding Remembrance Day.
  ["2026-11-24", false], // The tenth business day requires no early-publication warning.
])("publication date %s has early-date warning %s", (publicationDate, warn) => {
  render(<OpenInfo requestDetails={{ closedate: "2026-11-09" }} isOITeam />);
  fireEvent.change(screen.getByLabelText("Publication date"), {
    target: { value: publicationDate },
  });
  if (warn) {
    expect(screen.getByRole("alert")).toHaveTextContent("within 10 business days");
    expect(screen.getByLabelText("Publication date")).toHaveValue("");
  } else {
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.getByLabelText("Publication date")).toHaveValue(publicationDate);
  }
});
