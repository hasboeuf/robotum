import { combineReducers } from 'redux'
import view from './ViewReducer'
import auth from './AuthReducer'

export default combineReducers({
  view,
  auth
})