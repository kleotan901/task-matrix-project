import React from "react";
import { Sidebar } from "../../Components/Sidebar";

import "../../style/profile-page.scss";

const ProfilePage: React.FC = () => {

  return (
    <div className="profile-page">
      <div>
        <Sidebar />
      </div>
      <div>
        <h1>Профіль</h1>
      </div>
      
    </div>
  );
};

export default ProfilePage;
