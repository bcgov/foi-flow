import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import {Row,Col} from 'react-bootstrap';
import './divisionaltracking.scss';


const DivisionalTracking = React.memo(({divisions}) => {

    const displayDivisions = divisions?.map((division, index) =>
        <Row key={index} className='divisions-row'>
            <Col className='text-right'>{division.divisionname}</Col>
            <Col>
              <div style={{display: 'inline-flex'}} className='arrow'>
                <div className='line'></div>
                <div className='point'></div>
             </div>
             </Col>
            <Col className='text-left'>{division.stagename}</Col>
        </Row>
    );

    return (
        <Card className="foi-details-card">            
        <label className="foi-details-label">DIVISIONAL TRACKING</label>
        <CardContent className='align-division'> 
        {displayDivisions}
        </CardContent>
    </Card>
    );
});
export default DivisionalTracking;