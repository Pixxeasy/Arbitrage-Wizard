import {Navigate, Outlet, useLocation} from "react-router";
import {useAuth} from "./util/useAuth"

const ProtectedRoute = () => {
    const auth = useAuth()
    const location = useLocation()

    return auth.token ? (
        <Outlet />
    ) : (
        <Navigate to="/" state={{ from: location }} />
    )
};

export default ProtectedRoute;