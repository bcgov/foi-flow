import React /*{useEffect}*/ from "react";
import {NavDropdown} from "react-bootstrap";
import {useDispatch, useSelector} from "react-redux";
import {setSelectedBPMFilter, setSelectedTaskID} from "../../../actions/bpmTaskActions";
import {Link} from "react-router-dom";
/*import {Link} from "react-router-dom";*/


const ServiceFlowFilterListDropDown = React.memo(() => {
  const dispatch= useDispatch();
  const filterList = useSelector(state=> state.bpmTasks.filterList);
  const isFilterLoading = useSelector(state=> state.bpmTasks.isFilterLoading);
  const selectedFilter=useSelector(state=>state.bpmTasks.selectedFilter);

  const changeFilterSelection = (filter)=>{
    dispatch(setSelectedBPMFilter(filter));
    dispatch(setSelectedTaskID(null));
  }


  const renderFilterList = () => {
    if (filterList.length) {
      return (
        <>
          {filterList.map((filter,index)=> (
            <NavDropdown.Item
              // There are 6 other links in the Navigation Bar; index starts at 0; Hence index + 7
              eventKey={index + 7}
              as={Link} to='/task' className={`main-nav nav-item ${filter?.id === selectedFilter?.id ? "dropdown-option-selected" : ""}`}
                              key={index} onClick={()=>changeFilterSelection(filter)}>
              <span
                className={`
                  ${filter?.id === selectedFilter?.id ? "dropdown-option-selected" : "black-text"}
                `}
                >
                  {filter?.name}
                  {`(${ filter.itemCount || 0})`}
                </span>
            </NavDropdown.Item>
            )
          )}
        </>
      )
    } else {
      return (
          <NavDropdown.Item className="not-selected mt-2 ml-1">
            <i className="fa fa-info-circle mr-2 mt-1"/>
            No Filters Found
          </NavDropdown.Item>
      )
    }
  }
  return  <>
    {isFilterLoading? <NavDropdown.Item>Loading...</NavDropdown.Item>: renderFilterList()}
    </>
});

export default ServiceFlowFilterListDropDown;
