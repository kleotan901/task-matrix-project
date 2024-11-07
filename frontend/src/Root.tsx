import React, { Suspense } from 'react';
import {
  HashRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import App from './App';
import LandingPage from './Pages/LandingPage/LandingPage';
import LoginPage from './Pages/LoginPage/LoginPage';
import RegisterPage from './Pages/RegisterPage/RegisterPage';
import { LANDING_PAGE_ROUTE, LOGIN_ROUTE, PROFILE_ROUTE, REGISTER_ROUTE } from './utils/const';
import ProfilePage from './Pages/ProfilePage/ProfilePage';

export const Root = () => {
  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path={LANDING_PAGE_ROUTE} element={<App />}>
            <Route index element={<LandingPage />} />
            <Route path="home" element={<Navigate to={LANDING_PAGE_ROUTE} replace />} />
            <Route path={LOGIN_ROUTE} element={<LoginPage />} />
            <Route path={REGISTER_ROUTE} element={<RegisterPage />} />
            <Route path={PROFILE_ROUTE} element={<ProfilePage />} />
          </Route>
        </Routes>
      </Suspense>
    </Router>

  )
}