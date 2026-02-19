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
    yearCard: {
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
    yearCardSelected: {
        backgroundColor: '#fff',
        //border: '2px solid #000 !important',
        zIndex: 1,
    },
    yearCardUnselected: {
        backgroundColor: '#E7E7E7',
        color: '#000000CC',
        '&:hover': {
            //borderColor: '#000',
            backgroundColor: '#fff',
        }
    },
    yearCardText: {
        fontSize: '14px',
        fontWeight: '500',
    },
    yearContainer: {
        padding: '0px 15px 15px 15px'
    }
}));

const YearSelector = ({ date, selectedYear, onUpdate }) => {
    const classes = useStyles();

    const getYearFromDate = (dateStr) => {
        if (!dateStr) return new Date().getFullYear();
        return Number(dateStr.slice(0, 4));
    };

    const [startYear, setStartYear] = useState(getYearFromDate(date) - 5);

    useEffect(() => {
        if (date) {
            const y = getYearFromDate(date);
            if (y < startYear || y > startYear + 11) {
                setStartYear(y - 5);
            }
        }
    }, [date]);

    const handleRangeChange = (increment) => {
        setStartYear(startYear + (increment * 12));
    };

    const handleYearClick = (y) => {
        onUpdate(null, y.toString());
    };

    const years = Array.from({ length: 12 }, (_, i) => startYear + i);

    return (
        <div className={classes.root}>
            <div className={classes.header}>
                <IconButton onClick={() => handleRangeChange(-1)} size="small">
                    <ArrowBackIosIcon fontSize="small" />
                </IconButton>

                <Typography className={classes.yearText}>
                    {startYear}-{startYear + 11}
                </Typography>

                <IconButton onClick={() => handleRangeChange(1)} size="small">
                    <ArrowForwardIosIcon fontSize="small" />
                </IconButton>
            </div>

            <Grid container spacing={0} className={classes.yearContainer}>
                {years.map((y) => {
                    const isSelected = selectedYear === y.toString();

                    return (
                        <Grid item xs={4} key={y}>
                            <Card
                                className={`${classes.yearCard} ${isSelected ? classes.yearCardSelected : classes.yearCardUnselected}`}
                                onClick={() => handleYearClick(y)}
                            >
                                <CardContent style={{ padding: '0px', width: '100%', display: 'flex', justifyContent: 'center' }}>
                                    <Typography className={classes.yearCardText}>
                                        {y}
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

YearSelector.propTypes = {
    date: PropTypes.string,
    selectedYear: PropTypes.string,
    onUpdate: PropTypes.func.isRequired,
};

export default YearSelector;
