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
    yearText: {
        fontSize: '18px',
        fontWeight: 'bold',
        margin: '0 20px',
        color: '#000000CC',
    },
    monthCard: {
        cursor: 'pointer',
        height: '100%',
        textAlign: 'center',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.3s',
        border: '1px solid #E0E0E0',
        boxShadow: 'none',
        borderRadius: '0px',
        minHeight: '65px',
    },
    monthCardSelected: {
        backgroundColor: '#fff',
        //border: '2px solid #000 !important',
        zIndex: 1,
    },
    monthCardUnselected: {
        backgroundColor: '#E7E7E7',
        color: '#000',
        '&:hover': {
            //borderColor: '#000',
            backgroundColor: '#fff',
        }
    },
    monthText: {
        fontSize: '14px',
        fontWeight: '500',
    },
    monthContainer: {
        padding: '0px 15px 15px 15px'
    }
}));

const months = [
    { shortName: 'Jan', fullName: 'January' },
    { shortName: 'Feb', fullName: 'February' },
    { shortName: 'Mar', fullName: 'March' },
    { shortName: 'Apr', fullName: 'April' },
    { shortName: 'May', fullName: 'May' },
    { shortName: 'Jun', fullName: 'June' },
    { shortName: 'Jul', fullName: 'July' },
    { shortName: 'Aug', fullName: 'August' },
    { shortName: 'Sep', fullName: 'September' },
    { shortName: 'Oct', fullName: 'October' },
    { shortName: 'Nov', fullName: 'November' },
    { shortName: 'Dec', fullName: 'December' },
];

const MonthSelector = ({ date, selectedMonth, onUpdate }) => {
    const classes = useStyles();

    const getYearFromDate = (dateStr) => {
        if (!dateStr) return new Date().getFullYear();
        return Number(dateStr.slice(0, 4))
    };

    const [year, setYear] = useState(getYearFromDate(date));

    useEffect(() => {
        if (date) {
            setYear(getYearFromDate(date));
        }
    }, [date]);

    const handleYearChange = (increment) => {
        const newYear = year + increment;
        setYear(newYear);
        if (selectedMonth) {
            updateDateForMonth(selectedMonth, newYear);
        }
    };

    const updateDateForMonth = (monthName, yearVal) => {
        const monthIndex = months.findIndex(m => m.fullName === monthName || m.shortName === monthName);
        if (monthIndex === -1) return;

        const monthStr = (monthIndex + 1).toString().padStart(2, '0');
        const newDate = `${yearVal}-${monthStr}-01`;

        onUpdate(newDate, `${months[monthIndex].fullName} ${yearVal}`);
    };

    const handleMonthClick = (m) => {
        updateDateForMonth(m.fullName, year);
    };

    return (
        <div className={classes.root}>
            <div className={classes.header}>
                <IconButton onClick={() => handleYearChange(-1)} size="small">
                    <ArrowBackIosIcon fontSize="small" />
                </IconButton>

                <Typography className={classes.yearText}>
                    {year}
                </Typography>

                <IconButton onClick={() => handleYearChange(1)} size="small">
                    <ArrowForwardIosIcon fontSize="small" />
                </IconButton>
            </div>

            <Grid container spacing={0} className={classes.monthContainer}>
                {months.map((m) => {
                    const isSelected = selectedMonth === m.fullName || selectedMonth === m.shortName || selectedMonth === `${m.fullName} ${year}` || selectedMonth === `${m.shortName} ${year}`;
                    return (
                        <Grid item xs={4} key={m.shortName}>
                            <Card
                                className={`${classes.monthCard} ${isSelected ? classes.monthCardSelected : classes.monthCardUnselected}`}
                                onClick={() => handleMonthClick(m)}
                            >
                                <CardContent style={{ padding: '0px', width: '100%', display: 'flex', justifyContent: 'center' }}>
                                    <Typography className={classes.monthText}>
                                        {m.shortName}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    );
                })}
            </Grid>
        </div>
    );
};

MonthSelector.propTypes = {
    date: PropTypes.string,
    selectedMonth: PropTypes.string,
    onUpdate: PropTypes.func.isRequired,
};

export default MonthSelector;
