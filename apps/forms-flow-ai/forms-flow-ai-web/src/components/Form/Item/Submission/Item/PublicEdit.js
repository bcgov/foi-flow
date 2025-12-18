import React, {useEffect} from 'react';
import {connect, useDispatch, useSelector} from 'react-redux'
import { getForm, getSubmission, selectRoot, saveSubmission, Form, selectError, Errors } from 'react-formio';
import Loading from '../../../../../containers/Loading'
import {setFormSubmissionError, setFormSubmissionLoading} from '../../../../../actions/formActions';
import SubmissionError from '../../../../../containers/SubmissionError';
import {useParams} from "react-router-dom";
import LoadingOverlay from "react-loading-overlay";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
  publicstyle: {
    display: "none !important",
    height: "0px !important",
    marginTop: "0px !important",
    marginBottom: "0px !important",
  },
}));

const PublicEdit = React.memo((props) => {
  const dispatch = useDispatch();
  const {formId, submissionId} = useParams();
  const classes = useStyles();
  const {
    hideComponents,
    onSubmit,
    options,
    errors,
    onFormSubmit,
    onCustomEvent,
    form: { form, isActive: isFormActive },
    submission: { submission, isActive: isSubActive, url }
  } = props;
 
  const isFormSubmissionLoading = useSelector(state=>state.formDelete.isFormSubmissionLoading);
  useEffect(() => {
    dispatch(getForm('form',formId));
    dispatch(getSubmission('submission', submissionId, formId));
    dispatch(setFormSubmissionLoading(false));
  }, [dispatch, submissionId, formId]);  

  if ((isFormActive ||  (isSubActive && !isFormSubmissionLoading))) {
      return <Loading />;
  }
  
  return (
      <div className="container overflow-y-auto">
        <div className={`main-header ${classes.publicstyle}`}>
          <SubmissionError modalOpen={errors?.includes("Token Expired")}
            errors={errors}
            onConfirm={props.onConfirm}
          >
          </SubmissionError>
        </div>
        {/* <Errors errors={errors} /> */}
        <LoadingOverlay active={isFormSubmissionLoading} spinner text='Loading...' className="col-12">
          <div className="ml-4 mr-4">
        <Form
          form={form}
          submission={submission}
          url={url}
          hideComponents={hideComponents}
          onSubmit={(_submission)=>onSubmit(_submission, onFormSubmit, form._id)}
          options={{ ...options }}
          onCustomEvent={onCustomEvent}
        />
          </div>
        </LoadingOverlay>
      </div>
    );
})

PublicEdit.defaultProps = {
  onCustomEvent: ()=>{}
};

const mapStateToProps = (state) => {
  return {
    user: state.user.userDetail,
    form: selectRoot('form', state),
    submission: selectRoot('submission', state),
    isAuthenticated: state.user.isAuthenticated,
    errors: [
      selectError('form', state),
      selectError('submission', state),
    ],
    options: {
      noAlerts: false,
      i18n: {
        en: {
          error: "Please fix the errors before submitting again.",
        },
      }
    },
    submissionError: selectRoot('formDelete', state).formSubmissionError,
  }
}

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmit: (submission, onFormSubmit, formId) => {
      dispatch(setFormSubmissionLoading(true));
      dispatch(saveSubmission('submission', submission, onFormSubmit?formId: ownProps.match.params.formId));
    },
    onConfirm: () => {
      window.location.reload();
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(PublicEdit)
