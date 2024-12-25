import React, { useContext, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { signInWithPopup, User } from 'firebase/auth';
import { Context, googleAuthProvider } from '../../firebase';
import { LANDING_PAGE_ROUTE, PROFILE_ROUTE } from '../../utils/const';
import googleIcon from "../../icons/flat-color-icons_google.png";
import { Slider } from '../../Components/Slider';
import { loginWithEmail, postUserGoodle } from '../../utils/api';
import { LoginData } from '../../type/LoginData';
import { UserData } from '../../type/UserData';

const LoginPage = () => {
  const firebaseContext = useContext(Context);
  const navigate = useNavigate();

  const [loginData, setLoginData] = useState<LoginData>({
    email: '',
    password: '',
  });

  const [rememberMe, setRememberMe] = useState(false);
  // const [isGoogleSignUp, setIsGoogleSignUp] = useState(false);

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

    const registerWithGoogle = async () => {
      if (!firebaseContext || !firebaseContext.auth) {
        console.error("Firebase context або auth не доступний");
        return;
      }
  
      try {
        const { auth } = firebaseContext;
        const result = await signInWithPopup(auth, googleAuthProvider);
        const user: User = result.user;
  
        const userData: UserData = {
          email: user.email || '',
          full_name: user.displayName || '',
          avatar_url: user.photoURL || '',
          verified_email: user.emailVerified
        };
  
        localStorage.setItem('userData', JSON.stringify(userData));
  
        const response = await postUserGoodle(userData); // Викликаємо функцію для реєстрації через email
      
        if (response.ok) {
          navigate(PROFILE_ROUTE);
        } else {
          alert(response.result || `Код помилки: ${response.status}`);
        }
        } catch (error) {
          console.error("Помилка під час реєстрації:", error);
          alert("Сталася помилка. Спробуйте ще раз пізніше.");
        }
    };

  // Логін через email та пароль
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const { email, password } = loginData;

    if (!email || !password) {
      alert("Будь ласка, заповніть усі поля.");
      return;
    }

    try {
      const response = await loginWithEmail(loginData); // Використовуємо loginData
      if (response.ok) {
        // Збереження даних користувача
        if (rememberMe) {
          localStorage.setItem('loginData', JSON.stringify(loginData));
        } else {
          sessionStorage.setItem('loginData', JSON.stringify(loginData));
        }
        navigate(PROFILE_ROUTE); // Перенаправляємо на сторінку профілю
      } else {
        alert('Щось пішло не так. Спробуйте ще раз.');
      }
    } catch (error) {
      console.error("Помилка при логіні:", error);
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
            onClick={registerWithGoogle}
            className="register-page__button register-page__button--google"
          >
            <img src={googleIcon} alt="google" />
            Продовжити з Google
          </button>
        </form>
      </div>
      <div className="register-page__image-container">
        <Slider />
      </div>
    </div>
  );
};

export default LoginPage;
