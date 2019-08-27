import React from 'react';
import { BrowserRouter, Route, Switch } from "react-router-dom"
import './App.css';
import HeaderContainer from './containers/HeaderContainer'
import Footer from './components/Footer'
import Home from './components/pages/Home'
import Login from './components/pages/Login'
import Robotum from './components/pages/Robotum'
import NoMatch from './components/pages/NoMatch'
import { PrivateRoute } from './components/PrivateRoute'
import SidebarContainer from './containers/SidebarContainer';


export const App = (store) => {
  return (
    <BrowserRouter>
      <div>
        <SidebarContainer />
        <HeaderContainer />
        <Switch>
          <PrivateRoute exact path="/" component={Home} />
          <Route path="/login" component={Login} />
          <PrivateRoute path="/robotum" component={Robotum} />
          <Route component={NoMatch} />
        </Switch>
        <Footer/>
      </div>
    </BrowserRouter>
  );
}

export default App;
