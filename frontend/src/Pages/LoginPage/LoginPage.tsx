import React, { useContext, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { signInWithPopup, User } from 'firebase/auth';
import { Context, googleAuthProvider } from '../../firebase';
import { LANDING_PAGE_ROUTE, PROFILE_ROUTE } from '../../utils/const';
import googleIcon from "../../icons/flat-color-icons_google.png";

const LoginPage = () => {
  const firebaseContext = useContext(Context);
  const navigate = useNavigate();
  
  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
  });

  const [rememberMe, setRememberMe] = useState(false); // Стан для чекбоксу "Запам'ятати мене"

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = event.target;
    if (type === "checkbox") {
      setRememberMe(checked);
    } else {
      setLoginData(prevState => ({
        ...prevState,
        [name]: value,
      }));
    }
  };

  // Обробка логіну через Google
  const loginWithGoogle = async () => {
    if (!firebaseContext || !firebaseContext.auth) {
      console.error("Firebase context або auth не доступний");
      return;
    }

    const { auth } = firebaseContext;

    try {
      const result = await signInWithPopup(auth, googleAuthProvider);
      const user: User = result.user;

      const userData = {
        email: user.email || '',
        full_name: user.displayName || '',
        avatar_url: user.photoURL || '',
        verified_email: user.emailVerified,
      };

      // Зберігаємо дані користувача у локальне сховище
      if (rememberMe) {
        localStorage.setItem('userData', JSON.stringify(userData));
      } else {
        sessionStorage.setItem('userData', JSON.stringify(userData));
      }

      // Надсилання POST-запиту до вашого серверу для логіну
      try {
        const response = await fetch('http://13.60.234.72/api/profile/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData),
        });

        if (response.ok) {
          navigate(PROFILE_ROUTE);
        } else {
          const result = await response.json();
          alert(result.message || 'Щось пішло не так');
        }
      } catch (error) {
        console.error('Error during login:', error);
      }
    } catch (error) {
      console.error('Error during sign in with popup:', error);
    }
  };

  // Обробка стандартного логіну через email та пароль
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const { email, password } = loginData;

    if (!email || !password) {
      alert("Будь ласка, заповніть усі поля.");
      return;
    }

    // Надсилання POST-запиту до вашого серверу для логіну
    try {
      const response = await fetch('http://13.60.234.72/api/profile/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        // Зберігаємо дані користувача відповідно до стану чекбоксу
        const userData = { email, password };

        if (rememberMe) {
          localStorage.setItem('userData', JSON.stringify(userData));
        } else {
          sessionStorage.setItem('userData', JSON.stringify(userData));
        }

        // Якщо логін успішний, перенаправляємо на профіль
        navigate(PROFILE_ROUTE);
      } else {
        const result = await response.json();
        alert(result.message || 'Щось пішло не так');
      }
    } catch (error) {
      console.error('Error during login:', error);
      alert('Щось пішло не так. Будь ласка, спробуйте пізніше.');
    }
  };


  return (
    <div className="register-page">
      <div className="register-page__container">
        <div className="register-page__logo">
          <div className="logo">
            <NavLink to={LANDING_PAGE_ROUTE} className="logo__link">
              Quatrix
            </NavLink>
          </div>
        </div>
        <h2 className="register-page__title">Вхід</h2>
        <form onSubmit={handleSubmit} className="register-page__form">
          <label htmlFor="emailForLogin" className="register-page__label">
            Email
          </label>
          <input
            className="register-page__input register-page__input--email"
            type="text"
            id="emailForLogin"
            placeholder="Введіть Email"
            name="email"
            value={loginData.email}
            onChange={handleChange}
            required
          />
          <label htmlFor="passwordForLogin" className="register-page__label">
            Пароль
          </label>
          <input
            className="register-page__input register-page__input--password"
            type="password"
            id="passwordForLogin"
            placeholder="Введіть пароль"
            name="password"
            value={loginData.password}
            onChange={handleChange}
            required
          />
          
          {/* Чекбокс "Запам'ятати мене" */}
          <div className="register-page__checkbox">
            <div className="register-page__checkbox-container">
              <input
                className="register-page__checkbox-input"
                type="checkbox"
                id="rememberMe"
                checked={rememberMe}
                onChange={handleChange}
              />
              <label htmlFor="rememberMe" className="register-page__label--small">
                Запам'ятати мене
              </label>
            </div>
            <div className="register-page__forgot-password">
              <NavLink to="/" className="register-page__url">
                Забули пароль?
              </NavLink>
            </div>
          </div>

          <button
            type="submit"
            className="register-page__button register-page__button--continue"
          >
            Продовжити
          </button>
          <button
            type="button"
            onClick={loginWithGoogle}
            className="register-page__button register-page__button--google"
          >
            <img src={googleIcon} alt="google" />
            Продовжити з Google
          </button>
        </form>
      </div>
      <div></div>
    </div>
  );
};

export default LoginPage;
