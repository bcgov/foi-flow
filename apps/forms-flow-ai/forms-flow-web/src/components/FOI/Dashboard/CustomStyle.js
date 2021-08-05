
import { createMuiTheme , darken, lighten } from '@material-ui/core/styles';
import { makeStyles } from '@material-ui/styles';

function getThemePaletteMode(palette) {
  return palette.type || palette.mode;
}

const defaultTheme = createMuiTheme();
const useStyles = makeStyles(
  (theme) => {    
    const getBackgroundColor = (color) =>
      getThemePaletteMode(theme.palette) === 'dark'
        ? darken(color, 0.94)
        : lighten(color, 0.94);

    const getHoverBackgroundColor = (color) =>
      getThemePaletteMode(theme.palette) === 'dark'
        ? darken(color, 0.9)
        : lighten(color, 0.9);

    return {
      root: {
        '& .super-app-theme--unopened': {
          backgroundColor: '#cfd7e3', 
          '&:hover': {
            backgroundColor: getHoverBackgroundColor(theme.palette.info.main),
          },
        },
        '& .super-app-theme--intakeinprogress': {
          backgroundColor: '#FFFFF',
          '&:hover': {
            backgroundColor: '#f1f1f1',
          },
        },
        '& .super-app-theme--PartiallyFilled': {
          backgroundColor: getBackgroundColor(theme.palette.warning.main),
          '&:hover': {
            backgroundColor: getHoverBackgroundColor(theme.palette.warning.main),
          },
        },
        '& .super-app-theme--Rejected': {
          backgroundColor: getBackgroundColor(theme.palette.error.main),
          '&:hover': {
            backgroundColor: getHoverBackgroundColor(theme.palette.error.main),
          },
        },        
      },
    };
  },
  { defaultTheme },
);

export default useStyles;