import {TOGGLE_SIDEBAR} from "../actions/ViewActions";


const initialState = {
    showSidebar: false
};

export default function (state = initialState, action) {
    switch (action.type) {
        case TOGGLE_SIDEBAR:
            return {...state, showSidebar: !state.showSidebar};
        default:
            return state
    }
}
