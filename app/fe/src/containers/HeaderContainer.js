import React from "react";
import {bindActionCreators} from "redux";
import { connect } from "react-redux";
import toggleSidebar from "../actions/ViewActions";
import Header from "../components/Header";

const HeaderContainer = (props) => <Header {...props}/>;
 
function mapStateToProps(state) {
    return {
        showSidebar: state.view.showSidebar
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({toggleSidebar}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(HeaderContainer);
