import { NavLink } from "react-router-dom"
import { LANDING_PAGE_ROUTE } from "../../utils/const"

import "../../style/sidebar.scss"
export const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="sidebar-wrapper">
        <header>
          <div className="header__logo logo">
            <NavLink to={LANDING_PAGE_ROUTE} className="logo__link">
              Quatrix
            </NavLink>
          </div>
        </header>
        <nav>

        </nav>
        <div className="sidebar__profile">          

        </div>
      </div>
    </div>
  )
}