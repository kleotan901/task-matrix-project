import { NavLink } from "react-router-dom"
import { LANDING_PAGE_ROUTE, LOGIN_ROUTE, REGISTER_ROUTE } from "../../utils/const"

import '../../style/Header.scss';

export const Header = () => {
  return (
    <div className="header">
      <div className="wrapper">
        <div className="header__content">
          <div className="header__logo logo">
            <NavLink to={LANDING_PAGE_ROUTE} className="logo__link">
              Quatrix
            </NavLink>
          </div>
          <div className="header__button">
            <NavLink to={LOGIN_ROUTE} className="button button--white link link--text-black">
              Вхід
            </NavLink>
            <NavLink to={REGISTER_ROUTE} className="button button--softBluePurple link link--text-white">
              Почати
            </NavLink>
          </div>
        </div>
      </div>
    </div>
  )
}