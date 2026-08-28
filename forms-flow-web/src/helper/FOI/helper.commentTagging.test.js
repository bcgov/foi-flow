import {
  addToFullnameList,
  getIAOTagList,
} from "./helper";

describe("FOI comment user tag lists", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  test("builds IAO Internal/Peer Review tag users from the IAO assigned-to list", () => {
    addToFullnameList(
      [
        {
          type: "iao",
          members: [
            {
              username: "analyst.one@idir",
              firstname: "Analyst",
              lastname: "One",
            },
            {
              username: "reviewer.two@idir",
              firstname: "Reviewer",
              lastname: "Two",
            },
          ],
        },
      ],
      "iao"
    );

    expect(getIAOTagList("iao")).toEqual([
      {
        username: "analyst.one@idir",
        firstname: "Analyst",
        lastname: "One",
        fullname: "One, Analyst",
        name: "One, Analyst",
      },
      {
        username: "reviewer.two@idir",
        firstname: "Reviewer",
        lastname: "Two",
        fullname: "Two, Reviewer",
        name: "Two, Reviewer",
      },
    ]);
  });

  test("builds Ministry Internal/Peer Review tag users from the ministry assigned-to list", () => {
    addToFullnameList(
      [
        {
          type: "ministry",
          members: [
            {
              username: "ministry.one@idir",
              firstname: "Ministry",
              lastname: "One",
            },
            {
              username: "ministry.two@idir",
              firstname: "Ministry",
              lastname: "Two",
            },
          ],
        },
      ],
      "EDUC"
    );

    expect(getIAOTagList("EDUC")).toEqual([
      {
        username: "ministry.one@idir",
        firstname: "Ministry",
        lastname: "One",
        fullname: "One, Ministry",
        name: "One, Ministry",
      },
      {
        username: "ministry.two@idir",
        firstname: "Ministry",
        lastname: "Two",
        fullname: "Two, Ministry",
        name: "Two, Ministry",
      },
    ]);
  });

  test("does not duplicate a user who belongs to multiple IAO teams", () => {
    addToFullnameList(
      [
        {
          type: "iao",
          members: [
            {
              username: "shared.user@idir",
              firstname: "Shared",
              lastname: "User",
            },
          ],
        },
        {
          type: "iao",
          members: [
            {
              username: "shared.user@idir",
              firstname: "Shared",
              lastname: "User",
            },
          ],
        },
      ],
      "iao"
    );

    expect(getIAOTagList("iao")).toEqual([
      {
        username: "shared.user@idir",
        firstname: "Shared",
        lastname: "User",
        fullname: "User, Shared",
        name: "User, Shared",
      },
    ]);
  });

  test("returns an empty tag list when no team code is supplied", () => {
    expect(getIAOTagList(null)).toEqual([]);
    expect(getIAOTagList(undefined)).toEqual([]);
  });
});
