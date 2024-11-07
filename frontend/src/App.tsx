import React from 'react';
import { Outlet } from 'react-router-dom';

import './style/main.scss';

function App() {
  return (
    <div>
      <Outlet />
    </div>
  );
}

export default App;
