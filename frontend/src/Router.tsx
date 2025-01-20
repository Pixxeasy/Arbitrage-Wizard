import { Routes, Route } from "react-router";
import Dashboard from "./pages/Dashboard";
import LoginForm from "./components/LoginForm";

import ProtectedRoute from "./ProtectedRoute";

function Router() {
    return (
        <Routes>
            <Route path="/" element={<LoginForm />} />
            <Route element={<ProtectedRoute/>}>
                <Route path="/dashboard" element={<Dashboard />} />
            </Route>
        </Routes>
    );
}

export default Router;