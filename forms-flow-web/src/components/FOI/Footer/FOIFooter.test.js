import { render, screen } from '@testing-library/react';
import FOIFooter from "./FOIFooter";
import { shallow, mount } from "enzyme";

it("FOI Footer Rendering Unit test", () => {
    shallow(<FOIFooter />);
  });

  it("FOI Footer Rendering Unit test with element", () => {
    const wrapper = shallow(<FOIFooter />);
    const appleheader = <li><a href="#">Help</a></li>;
    expect(wrapper.contains(appleheader)).toEqual(true);
  });

test('FOI Footer Rendering Unit test with text check', () => {
    render(<FOIFooter />);
    const linkElement = screen.getByText('Disclaimer');    
    expect(linkElement).toBeInTheDocument()
  });
  