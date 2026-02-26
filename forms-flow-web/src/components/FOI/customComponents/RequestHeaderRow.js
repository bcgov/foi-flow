import React from 'react';
import './requestheaderrow.scss';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCalendar } from '@fortawesome/free-regular-svg-icons';
import Link from '@material-ui/core/Link';

const RequestHeaderRow = ({ headerText, isProactiveDisclosure }) => {

    const preventDefault = (event) => event.preventDefault();

    return (
        <div className="row">
            {isProactiveDisclosure ? (
                <div className="col-lg-12">
                    <div className="foi-request-header-card">
                        <div className="foi-request-number-header-pd">
                            <h1 className="foi-request-number-text">{headerText}</h1>
                        </div>
                        <div className='foi-request-calendar'>
                            <button type="button" className="btn-calendar">
                                <FontAwesomeIcon icon={faCalendar} size="lg" /> Calendar
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="col-lg-12">
                    <div className="foi-request-review-header-col1-row axis-request-id">
                        <Link href="#" onClick={preventDefault}>
                            <h1 className="foi-review-request-text foi-ministry-requestheadertext">{headerText}</h1>
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RequestHeaderRow;
