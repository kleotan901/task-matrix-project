import { LANDING_PAGE_ROUTE, LOGIN_ROUTE, PROFILE_ROUTE, REGISTER_ROUTE } from './utils/const';
import LandingPage from './Pages/LandingPage/LandingPage';
import LoginPage from './Pages/LoginPage/LoginPage';
import ProfilePage from './Pages/ProfilePage/ProfilePage';
import RegisterPage from './Pages/RegisterPage/RegisterPage';

export const publicRoute = [
  {
    path: LANDING_PAGE_ROUTE,
    page: LandingPage,
    exact: true,    
  },
  {
    path: LOGIN_ROUTE,
    page: LoginPage,
    exact: true,
  }, 
  {
    path: REGISTER_ROUTE,
    page: RegisterPage,
    exact: true,
  }
];

export const privateRoute = [
  {
    path: PROFILE_ROUTE,
    page: ProfilePage,
    exact: true,
    requiresAuth: true,
  }
];