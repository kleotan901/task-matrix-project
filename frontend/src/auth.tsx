import { useEffect, useState } from 'react';
import { getAuth, signInWithPopup, User } from 'firebase/auth';
import { app, googleAuthProvider } from './firebase';

export const AuthProvider = () => {
  const auth = getAuth(app);
  const [user, setUser] = useState<User | null>(auth.currentUser);

  useEffect(() => {
    const unsub = auth.onAuthStateChanged((maybeUser) => {
      if (maybeUser !== null) {
        return setUser(maybeUser);
      }

      signInWithPopup(auth, googleAuthProvider)
        .then((credentials => setUser(credentials.user)))
        .catch((error) => console.error(error as string));
    })

    return unsub;
  }, [auth])

  return user != null ? <>{user.displayName}</> : <>loading</>
}