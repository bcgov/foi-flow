import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/styles';
import IconButton from '@material-ui/core/IconButton';
import ArrowBackIosIcon from '@material-ui/icons/ArrowBackIos';
import ArrowForwardIosIcon from '@material-ui/icons/ArrowForwardIos';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        padding: '0px',
    },
    header: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: '10px',
        padding: '5px 0',
    },
    yearNavigation: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
    },
    yearText: {
        fontSize: '20px',
        fontWeight: 'bold',
        margin: '0 15px',
        color: '#333',
    },
    yearTextSecondary: {
        fontSize: '14px',
        color: '#999',
        margin: '0 10px',
        fontWeight: 'normal',
    },
    qCard: {
        cursor: 'pointer',
        textAlign: 'center',
        transition: 'all 0.3s',
        border: '1px solid #E0E0E0',
        boxShadow: 'none',
        borderRadius: '0px',
        height: '145px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
    },
    qCardSelected: {
        backgroundColor: '#fff',
        //borderColor: '#000',
    },
    qCardUnselected: {
        backgroundColor: '#E7E7E7',
        '&:hover': {
            //borderColor: '#000',
            backgroundColor: '#fff',
        }
    },
    titleSection: {
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    qTitle: {
        fontSize: '18px',
        fontWeight: 'normal',
        color: '#333',
    },
    qMonths: {
        display: 'flex',
        //backgroundColor: '#F7F7F7',
        borderTop: '1px solid #E0E0E0',
    },
    monthBox: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        flex: 1,
        borderRight: '1px solid #E0E0E0',
        padding: '10px 0',
        '&:last-child': {
            borderRight: 'none',
        }
    },
    monthName: {
        fontWeight: 'bold',
        fontSize: '11px',
        color: '#000000CC',
    },
    monthYear: {
        fontSize: '10px',
        color: '#000000CC',
        marginTop: '2px',
    },
    quarterContainer: {
        padding: '0px 15px 15px 15px'
    },
    noPadding: {
        padding: '0px !important',
    }
}));

const QuarterSelector = ({ date, selectedQuarter, onUpdate }) => {
    const classes = useStyles();

    const getFiscalYearFromDate = (dateStr) => {
        if (!dateStr) return new Date().getFullYear();
        const [year, month] = dateStr.split('-').map(Number);
        return month < 4 ? year - 1 : year;
    };

    const [fiscalYear, setFiscalYear] = useState(getFiscalYearFromDate(date));

    useEffect(() => {
        if (date) {
            setFiscalYear(getFiscalYearFromDate(date));
        }
    }, [date]);

    const handleYearChange = (increment) => {
        const newYear = fiscalYear + increment;
        setFiscalYear(newYear);
        if (selectedQuarter) {
            updateDateForQuarter(selectedQuarter, newYear);
        }
    };

    const quarters = [
        { name: 'Quarter 1', months: ['Apr', 'May', 'Jun'], monthIndices: [3, 4, 5], startMonth: 3 },
        { name: 'Quarter 2', months: ['Jul', 'Aug', 'Sep'], monthIndices: [6, 7, 8], startMonth: 6 },
        { name: 'Quarter 3', months: ['Oct', 'Nov', 'Dec'], monthIndices: [9, 10, 11], startMonth: 9 },
        { name: 'Quarter 4', months: ['Jan', 'Feb', 'Mar'], monthIndices: [0, 1, 2], startMonth: 0, nextYear: true },
    ];

    const updateDateForQuarter = (qName, year) => {
        const q = quarters.find(x => x.name === qName);
        if (!q) return;

        let dateYear = year;
        if (q.nextYear) dateYear += 1;

        const monthStr = (q.startMonth + 1).toString().padStart(2, '0');
        const newDate = `${dateYear}-${monthStr}-01`;

        onUpdate(newDate, `${qName} ${year}`);
    };

    const handleQuarterClick = (q) => {
        updateDateForQuarter(q.name, fiscalYear);
    };

    const renderMonth = (monthName, idx, q) => {
        let mYear = fiscalYear;
        if (q.nextYear) mYear += 1;

        return (
            <div key={idx} className={classes.monthBox}>
                <span className={classes.monthName}>{monthName}</span>
                <span className={classes.monthYear}>{mYear}</span>
            </div>
        )
    };

    return (
        <div className={classes.root}>
            <div className={classes.header}>
                <IconButton onClick={() => handleYearChange(-1)} size="small">
                    <ArrowBackIosIcon fontSize="small" style={{ color: '#999' }} />
                </IconButton>

                <Typography className={classes.yearText}>
                    {fiscalYear}-{(fiscalYear + 1).toString().slice(2)}
                </Typography>

                <IconButton onClick={() => handleYearChange(1)} size="small">
                    <ArrowForwardIosIcon fontSize="small" style={{ color: '#999' }} />
                </IconButton>
            </div>

            <Grid container spacing={1} className={classes.quarterContainer}>
                {quarters.map((q) => {
                    const isSelected = selectedQuarter === q.name || selectedQuarter === `${q.name} ${fiscalYear}`;
                    return (
                        <Grid item xs={6} key={q.name} className={classes.noPadding}>
                            <Card
                                className={`${classes.qCard} ${isSelected ? classes.qCardSelected : classes.qCardUnselected}`}
                                onClick={() => handleQuarterClick(q)}
                            >
                                <div className={classes.titleSection}>
                                    <Typography className={classes.qTitle}>
                                        {q.name}
                                    </Typography>
                                </div>
                                <div className={classes.qMonths}>
                                    {q.months.map((m, i) => renderMonth(m, i, q))}
                                </div>
                            </Card>
                        </Grid>
                    );
                })}
            </Grid>
        </div>
    );
};

QuarterSelector.propTypes = {
    date: PropTypes.string,
    selectedQuarter: PropTypes.string,
    onUpdate: PropTypes.func.isRequired,
};

export default QuarterSelector;
