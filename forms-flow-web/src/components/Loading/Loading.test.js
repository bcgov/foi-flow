import { render, screen } from '@testing-library/react';
import Loading from "./Loading";
import { shallow, mount } from "enzyme";

it("FOI Loading Rendering Unit test", () => {
    shallow(<Loading />);
  });

  it("FOI Loading Rendering Unit test with element", () => {
    const wrapper = shallow(<Loading />);
    const appleheader = <div className="col-12">Loading...</div>;
    expect(wrapper.contains(appleheader)).toEqual(true);
  });

test('FOI Loading Rendering Unit test with text check', () => {
    render(<Loading />);
    const linkElement = screen.getByText('Loading...');    
    expect(linkElement).toBeInTheDocument()
  });
  