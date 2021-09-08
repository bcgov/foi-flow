import { render, screen } from '@testing-library/react';
import Loading from "./Loading";
import { shallow, mount } from "enzyme";

it("renders without crashing", () => {
    shallow(<Loading />);
  });

  it("renders with  header", () => {
    const wrapper = shallow(<Loading />);
    const appleheader = <div className="col-12">Loading...</div>;
    expect(wrapper.contains(appleheader)).toEqual(true);
  });

test('check myform', () => {
    render(<Loading />);
    const linkElement = screen.getByText('Loading...');    
    expect(linkElement).toBeInTheDocument()
  });
  