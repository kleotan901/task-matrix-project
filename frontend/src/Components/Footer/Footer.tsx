import { NavLink } from "react-router-dom";
import { LANDING_PAGE_ROUTE } from "../../utils/const";

import "../../style/Footer.scss";

export const Footer = () => {
  return (
    <footer className="footer">
      <div className="wrapper">
        <div className="footer__content">
          <div className="footer__logo logo">
           <NavLink to={LANDING_PAGE_ROUTE} className="logo__link">
            Quatrix
          </NavLink>
          </div>
          <div className="footer__menu">
            <ul className="footer__list">
              <li className="footer__item">
                <a href="/" className="footer__link">Безпека</a>
              </li>
              <li className="footer__item">
                <a href="/" className="footer__link">Конфіденційність</a>
              </li>
              <li className="footer__item">
                <a href="/" className="footer__link">Умови</a>
              </li>
            </ul>
          </div>
        </div>
        
      </div>
    </footer>
  )
}