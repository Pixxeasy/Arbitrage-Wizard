import { Navigate, Outlet } from "react-router";

const ProtectedRoute = () => {
    return sessionStorage.getItem("token") ? <Outlet /> : <Navigate to={"/"} replace />;
};

export default ProtectedRoute;