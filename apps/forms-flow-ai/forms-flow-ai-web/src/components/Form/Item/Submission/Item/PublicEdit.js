import React, {useEffect} from 'react';
import {connect, useDispatch, useSelector} from 'react-redux'
import { getForm, getSubmission, selectRoot, saveSubmission, Form, selectError, Errors } from 'react-formio';
import Loading from '../../../../../containers/Loading'
import {setFormSubmissionError, setFormSubmissionLoading} from '../../../../../actions/formActions';
import SubmissionError from '../../../../../containers/SubmissionError';
import {useParams} from "react-router-dom";
import LoadingOverlay from "react-loading-overlay";

const PublicEdit = React.memo((props) => {
  const dispatch = useDispatch();
  const {formId, submissionId} = useParams();
  console.log(`formId: ${formId}, submissionId: ${submissionId}`)
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
  }, [dispatch, submissionId, formId, onFormSubmit ]);  

  if ((isFormActive ||  (isSubActive && !isFormSubmissionLoading))) {
      return <Loading />;
  }
  console.log(form) 
  return (
      <div className="container">
        <div className="main-header">
          <SubmissionError modalOpen={props.submissionError.modalOpen}
            message={props.submissionError.message}
            onConfirm={props.onConfirm}
          >
          </SubmissionError>
        </div>
        <Errors errors={errors} />
        <LoadingOverlay active={isFormSubmissionLoading} spinner text='Loading...' className="col-12">
          <div className="ml-4 mr-4">
        <Form
          form={form}
          submission={submission}
          url={url}
          hideComponents={hideComponents}
          onSubmit={(submission)=>onSubmit(submission,onFormSubmit,form._id)}
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
      console.log(`formId = ${formId}`)
      dispatch(setFormSubmissionLoading(true));
      dispatch(saveSubmission('submission', submission, onFormSubmit?formId: ownProps.match.params.formId, (err, submission) => {
        // if (!err) {
        //     // dispatch(resetSubmissions('submission'));
        //     dispatch(setFormSubmissionLoading(false));
        //     if(onFormSubmit){
        //     onFormSubmit();
        //   } else {
        //     toast.success("Submission Saved.");
        //     dispatch(push(`/public/form/${ownProps.match.params.formId}/submission/${submission._id}/edit`))
        //   }          
        // }
        // else {
        //   dispatch(setFormSubmissionLoading(false));
        //   const ErrorDetails = { modalOpen: true, message: "Submission cannot be done" }
        //   toast.error("Error while Submission.");
        //   dispatch(setFormSubmissionError(ErrorDetails))
        // }
      }));
    },
    onConfirm: () => {
      const ErrorDetails = { modalOpen: false, message: "" }
      dispatch(setFormSubmissionError(ErrorDetails))
    }
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(PublicEdit)
