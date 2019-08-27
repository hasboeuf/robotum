import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import SwipeableDrawer from '@material-ui/core/SwipeableDrawer';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import HomeIcon from '@material-ui/icons/Home';
import DeveloperBoardIcon from '@material-ui/icons/DeveloperBoard';

const styles = {
  list: {
    width: 250,
  }
};

function ListItemLink(props) {
  return <ListItem button component="a" {...props} />;
}

class SwipeableTemporaryDrawer extends React.Component {
  render() {
    const { classes } = this.props;

    const sideList = (
      <div className={classes.list}>
        <List>
          <ListItemLink href="/">
            <ListItemIcon><HomeIcon /></ListItemIcon>
            <ListItemText primary="Home" />
          </ListItemLink>
          <ListItemLink href="/robotum">
            <ListItemIcon><DeveloperBoardIcon /></ListItemIcon>
            <ListItemText primary="Robotum" />
          </ListItemLink>
        </List>
      </div>
    );

    return (
      <div>
        <SwipeableDrawer
          open={this.props.showSidebar}
          onClose={this.props.toggleSidebar}
          onOpen={this.props.toggleSidebar}
        >
          <div
            tabIndex={0}
            role="button"
            onClick={this.props.toggleSidebar}
            onKeyDown={this.props.toggleSidebar}
          >
            {sideList}
          </div>
        </SwipeableDrawer>
      </div>
    );
  }
}

SwipeableTemporaryDrawer.propTypes = {
  classes: PropTypes.object.isRequired,
  showSidebar: PropTypes.bool.isRequired,
  toggleSidebar: PropTypes.func.isRequired
};

export default withStyles(styles)(SwipeableTemporaryDrawer);
