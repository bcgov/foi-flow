import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { useSelector } from "react-redux";
import RequestDetails from "./RequestDetails";

jest.mock("react-redux", () => ({ useSelector: jest.fn() }));
jest.mock("./utils", () => ({
  shouldDisableFieldForMinistryRequests: () => false,
  findRequestState: () => "Intake in Progress",
}));
jest.mock("../customComponents/MinistriesCanvassed/MinistriesCanvassed", () => () => null);

const state = {
  foiRequests: {
    foiRequestTypeList: [{ requesttypeid: 1, name: "general" }],
    foiReceivedModeList: [{ receivedmodeid: 1, name: "Online Form" }],
    foiDeliveryModeList: [{ deliverymodeid: 1, name: "Secure File Transfer" }],
  },
};

beforeEach(() => useSelector.mockImplementation((selector) => selector(state)));

test.each([
  ["2026-11-02T23:29:00Z", "2026-11-02"],
  ["2026-11-02T23:30:59Z", "2026-11-02"],
  ["2026-11-02T23:31:00Z", "2026-11-03"],
  ["2026-11-03T07:30:00Z", "2026-11-03"],
  ["2026-11-02 16:30:00.000000", "2026-11-02"],
  ["2026-11-02 16:31:00.000000", "2026-11-03"],
  ["2025-01-15T00:30:00Z", "2025-01-14"],
  ["2026-11-02", "2026-11-02"],
])("Request Details receives %s as business date %s", (receivedDateUF, expected) => {
  const handleRequestDetailsInitialValue = jest.fn();
  render(
    <RequestDetails
      requestDetails={{
        requestType: "general",
        receivedMode: "Online Form",
        deliveryMode: "Secure File Transfer",
        currentState: "Intake in Progress",
        requeststatuslabel: "Intake in Progress",
        receivedDateUF,
        dueDate: "2027-02-01",
        originalDueDate: "2027-02-01",
      }}
      requestStatus="intakeinprogress"
      requestExtensions={[]}
      saveRequestObject={{}}
      handleRequestDetailsValue={jest.fn()}
      handleRequestDetailsInitialValue={handleRequestDetailsInitialValue}
      createSaveRequestObject={jest.fn()}
    />
  );

  expect(screen.getByLabelText(/Received Date/)).toHaveValue(expected);
  expect(handleRequestDetailsInitialValue).toHaveBeenCalledWith(
    expect.objectContaining({ receivedDate: expected, dueDate: "2027-02-01" })
  );
  expect(screen.getByLabelText(/Legislated Due Date/, { selector: "#dueDate" })).toHaveValue("2027-02-01");
});

test("Request Details retains a date-only closed date", () => {
  render(
    <RequestDetails
      requestDetails={{
        requestType: "general",
        receivedMode: "Online Form",
        deliveryMode: "Secure File Transfer",
        currentState: "Closed",
        receivedDateUF: "2026-10-01",
        closedate: "2026-11-07",
        dueDate: "2026-11-09",
      }}
      requestStatus="closed"
      requestExtensions={[]}
      saveRequestObject={{}}
      handleRequestDetailsValue={jest.fn()}
      handleRequestDetailsInitialValue={jest.fn()}
      createSaveRequestObject={jest.fn()}
    />
  );
  // The detail view displays the saved closure date; the dashboard's existing
  // cutoff-derived display is a separate contract.
  expect(screen.getByLabelText(/Closed Date/)).toHaveValue("2026-11-07");
});

test("editing a received calendar date keeps the existing weekend policy", () => {
  const handleRequestDetailsValue = jest.fn();
  render(
    <RequestDetails
      requestDetails={{
        requestType: "general",
        receivedMode: "Online Form",
        deliveryMode: "Secure File Transfer",
        currentState: "Intake in Progress",
        receivedDateUF: "2026-11-02",
        dueDate: "2027-02-01",
      }}
      requestStatus="intakeinprogress"
      requestExtensions={[]}
      saveRequestObject={{}}
      handleRequestDetailsValue={handleRequestDetailsValue}
      handleRequestDetailsInitialValue={jest.fn()}
      createSaveRequestObject={jest.fn()}
    />
  );
  fireEvent.change(screen.getByLabelText(/Received Date/), {
    target: { value: "2026-11-07" },
  });
  expect(screen.getByLabelText(/Received Date/)).toHaveValue("2026-11-09");
  expect(handleRequestDetailsValue).toHaveBeenCalledWith("2026-11-09", "receivedDate");
});

test.each([
  ["2026-11-02T23:30:00Z", "2026-11-02", "2026-12-15"],
  ["2026-11-02T23:31:00Z", "2026-11-03", "2026-12-16"],
])("a new request at %s starts %s and keeps the 30-business-day LDD %s", (receivedDateUF, startDate, dueDate) => {
  const handleRequestDetailsInitialValue = jest.fn();
  render(
    <RequestDetails
      requestDetails={{
        requestType: "general",
        receivedMode: "Online Form",
        deliveryMode: "Secure File Transfer",
        currentState: "Intake in Progress",
        receivedDateUF,
      }}
      requestStatus="intakeinprogress"
      requestExtensions={[]}
      saveRequestObject={{}}
      handleRequestDetailsValue={jest.fn()}
      handleRequestDetailsInitialValue={handleRequestDetailsInitialValue}
      createSaveRequestObject={jest.fn()}
    />
  );
  expect(screen.getByLabelText(/Start Date/)).toHaveValue(startDate);
  expect(screen.getByLabelText(/Legislated Due Date/, { selector: "#dueDate" })).toHaveValue(dueDate);
  expect(handleRequestDetailsInitialValue).toHaveBeenCalledWith(
    expect.objectContaining({ receivedDate: startDate, requestStartDate: startDate, dueDate })
  );
});

test("a start-date edit retains approved extensions across the winter holidays", () => {
  const handleRequestDetailsValue = jest.fn();
  render(
    <RequestDetails
      requestDetails={{
        requestType: "general",
        receivedMode: "Online Form",
        deliveryMode: "Secure File Transfer",
        currentState: "Intake in Progress",
        receivedDateUF: "2026-11-02",
        originalDueDate: "2026-12-15",
        dueDate: "2026-12-31",
      }}
      requestStatus="intakeinprogress"
      requestExtensions={[
        { extensionstatus: "Approved", extendedduedays: "10" },
        { extensionstatus: "Pending", extendedduedays: "99" },
      ]}
      saveRequestObject={{}}
      handleRequestDetailsValue={handleRequestDetailsValue}
      handleRequestDetailsInitialValue={jest.fn()}
      createSaveRequestObject={jest.fn()}
    />
  );
  fireEvent.change(screen.getByLabelText(/Start Date/), {
    target: { value: "2026-11-03" },
  });
  // The existing original-date input shares the LDD aria-labelledby value.
  expect(screen.getByDisplayValue("2026-12-16")).toHaveAttribute("id", "originalDueDate");
  expect(screen.getByLabelText(/Legislated Due Date/, { selector: "#dueDate" })).toHaveValue("2027-01-04");
  expect(handleRequestDetailsValue).toHaveBeenCalledWith("2026-11-03", "requestStartDate", "2027-01-04");
});
