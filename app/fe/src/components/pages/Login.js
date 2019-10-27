import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import { userActions } from "../../actions/AuthActions"


const styles = theme => ({
  content: {
  	 ...theme.mixins.gutters(),
    backgroundColor: theme.palette.background.paper,
    paddingTop: theme.spacing.unit * 2,
    paddingBottom: theme.spacing.unit * 2,
     
  }
});


function Login(props) {
  const { classes } = props;

  const handleSubmit = (e) => {
    e.preventDefault();

    // this.setState({ submitted: true });
    const { username, password } = this.state;
    const { dispatch } = this.props;
    if (username && password) {
        dispatch(userActions.login(username, password));
    }
  }

  return (
    <div className={classes.content}>
        <Typography variant="h5" component="h3">
          Welcome Login!
        </Typography>

        <form className={classes.container} noValidate autoComplete="off" onClick={handleSubmit}>
          <TextField
            required
            id="standard-required"
            label="Required"
            defaultValue="Username"
            className={classes.textField}
            margin="normal"
          />
          <TextField
            id="standard-password-input"
            label="Password"
            className={classes.textField}
            type="password"
            autoComplete="current-password"
            margin="normal"
          />
          <Button variant="contained" className={classes.button}>
            Login
          </Button>
        </form>
    </div>
  );
}

Login.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Login);
