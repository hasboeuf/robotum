import React from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
} from '@material-ui/core';
import MenuIcon from '@material-ui/icons/Menu';
import { withStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';

const styles = theme => ({})

class Header extends React.Component {
  render() {
    const { classes } = this.props;
    return (<AppBar position="static">
      <Toolbar>
            <IconButton color="inherit" aria-label="Open drawer" onClick={this.props.toggleSidebar}>
              <MenuIcon/>
            </IconButton>
            <Typography variant="h6" color="inherit" noWrap>
              HOME
            </Typography>
          </Toolbar>
    </AppBar>
    );
  }
}

Header.propTypes = {
  classes: PropTypes.object.isRequired,
  toggleSidebar: PropTypes.func.isRequired
};

export default withStyles(styles)(Header);
