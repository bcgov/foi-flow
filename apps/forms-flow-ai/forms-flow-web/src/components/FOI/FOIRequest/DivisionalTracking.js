import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import {Row,Col} from 'react-bootstrap';
import './divisionaltracking.scss';


const DivisionalTracking = React.memo(({requestDetails}) => {

    const displayDivisions = requestDetails.divisions.map((division, index) =>
        <Row key={index} className='divisions-row'>
            <Col className='text-right'>{division.divisionname}</Col>
            <Col>
              <span className='arrow'>
                <span className='line'></span>
                <span className='point'></span>
             </span>
             </Col>
            <Col className='text-left'>{division.stagename}</Col>
        </Row>
    );

    return (
        <Card className="foi-details-card">            
        <label className="foi-details-label">DIVISIONAL TRACKING</label>
        <CardContent className='align-division'> 
        {(requestDetails != undefined && requestDetails.divisions.length >0) ?
             displayDivisions : "No divisions to display"}
            
        </CardContent>
    </Card>
    );
});
export default DivisionalTracking;