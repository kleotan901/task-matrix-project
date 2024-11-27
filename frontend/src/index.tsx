import React from 'react';
import ReactDOM from 'react-dom/client';
import { Root } from './Root';
import { app, auth, fireStore, Context } from './firebase';

import './style/main.scss';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <Context.Provider value={{
      app,
      auth,
      fireStore,
  }}>
      <Root />
  </Context.Provider>
);
