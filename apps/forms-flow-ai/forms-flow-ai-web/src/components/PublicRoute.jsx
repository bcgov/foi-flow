import React, {useEffect} from 'react';
import { Route } from 'react-router-dom';
import { connect } from 'react-redux';
import { getForm } from 'react-formio';

import UserService from '../services/UserService';
import View from '../components/Form/Item/View';
import PublicEdit from '../components/Form/Item/Submission/Item/PublicEdit';
import NavBar from "../containers/NavBar";
import Footer from './Footer';
import NotFound from './NotFound';
 
const PublicRoute =({store})=>{

    useEffect(()=>{
        UserService.authenticateAnonymousUser(store)
    },[store])
    return (
          <div className="container">
              <NavBar/>
              {/* <Route path="/public/form/:formId/foirequest/:foiRequestId/ministryrequest/:ministryRequestId" component={View}/> */}
              <Route exact path="/public/form/:formId/submission/:submissionId/edit" component={PublicEdit}/>
              <Route exact path="/public/form/:formId/:notavailable" component={NotFound}/>
              <Footer/>
          </div>
       )
}

 
const mapDispatchToProps = (dispatch,ownProps) => {
    return {
        getForm: (id) => dispatch(getForm('form', id))
    };
};

export default connect(null, mapDispatchToProps)(PublicRoute);
