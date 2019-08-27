import { AuthService } from '../services';

export const userActions = {
    login,
    logout
};

function login(username, password) {
    return dispatch => {
        dispatch(request({ username }));

        AuthService.login(username, password)
            .then(
                user => { 
                    dispatch(success(user));
                    history.push('/');
                },
                error => {
                    dispatch(failure(error.toString()));
                }
            );
    };

    function request(user) { return { type: "LOGIN_REQUEST", user } }
    function success(user) { return { type: "LOGIN_SUCCESS", user } }
    function failure(error) { return { type: "LOGIN_FAILURE", error } }
}

function logout() {
    AuthService.logout();
    return { type: userConstants.LOGOUT };
}
