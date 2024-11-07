import { useContext, useEffect, useState } from "react";
import { signInWithPopup, User } from 'firebase/auth';
import { Context, googleAuthProvider } from "../../firebase";
import { NavLink, useNavigate } from "react-router-dom";
import { LANDING_PAGE_ROUTE, LOGIN_ROUTE, PROFILE_ROUTE } from "../../utils/const";
import { UserData } from "../../type/UserData";

import "../../style/register-page.scss";
import googleIcon from "../../icons/flat-color-icons_google.png";

const RegisterPage: React.FC = () => {
  const firebaseContext = useContext(Context);
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<UserData>({
    email: '',
    full_name: '',
    password: '',
    verified_email: false 
  });

  const [isGoogleSignUp, setIsGoogleSignUp] = useState(false);
  const [isEmailSubmitted, setIsEmailSubmitted] = useState(false);

  useEffect(() => {
    if (!firebaseContext) {
      return;
    }

    const storedUserData = localStorage.getItem('userData');
    if (storedUserData) {
      const parsedUserData: UserData = JSON.parse(storedUserData);
      setFormData(parsedUserData);
      navigate(PROFILE_ROUTE);
    }
  }, [firebaseContext, navigate]);

  // Реєстрація через Google
  const registerWithGoogle = async () => {
    if (!firebaseContext || !firebaseContext.auth) {
      console.error("Firebase context або auth не доступний");
      return;
    }

    const { auth } = firebaseContext;

    try {
      const result = await signInWithPopup(auth, googleAuthProvider);
      const user: User = result.user;

      setFormData({
        email: user.email || '',
        full_name: user.displayName || '',
        password: '',
        avatar_url: user.photoURL || '',
        verified_email: user.emailVerified
      });

      setIsGoogleSignUp(true);
      setIsEmailSubmitted(true);

      const userData: UserData = {
        email: user.email || '',
        full_name: user.displayName || '',
        avatar_url: user.photoURL || '',
        verified_email: user.emailVerified
      };

      localStorage.setItem('userData', JSON.stringify(userData));

      // Надсилання POST-запиту до вашого серверу
      try {
        const response = await fetch('http://13.60.234.72/api/profile/google/', {
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
        console.error('Error during registration:', error);
      }

    } catch (error) {
      console.error('Error during sign in with popup:', error);
    }
  };

  // Функція обробки змін полів форми
  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  // Стандартна реєстрація через email
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const { email, full_name } = formData;

    if (!email || !full_name) {
      alert("Будь ласка, заповніть усі обов'язкові поля.");
      return;
    }

    const userData = isGoogleSignUp
      ? {
          email,
          full_name,
          avatar_url: formData.avatar_url,
          emailVerified: formData.verified_email
        }
      : {
          email,
          full_name,
          password: formData.password 
        };

    localStorage.setItem('userData', JSON.stringify(userData));

    try {
      const response = await fetch('http://13.60.234.72/api/profile/register/', {
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
      console.error('Error during registration:', error);
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
        <h2 className="register-page__title">
          Зареєструйся і почни <br />працювати безкоштовно
        </h2>
        <form onSubmit={handleSubmit} className="register-page__form">
          {/* Поле для введення Email */}
          <label 
            htmlFor="email" 
            className={`register-page__label ${isEmailSubmitted ? 'register-page__label--disabled' : ''}`}
          >
            Email
          </label>
          <input
            className="register-page__input register-page__input--email"
            type="text"
            id="email"
            placeholder="Введіть Email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            disabled={isEmailSubmitted}
          />

          {/* Показувати додаткові поля після введення Email */}
          {isEmailSubmitted && (
            <>
              <label htmlFor="full_name" className="register-page__label">
                Ім'я
              </label>
              <input
                className="register-page__input register-page__input--name"
                type="text"
                placeholder="Ваше ім'я"
                name="full_name"
                id="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
              />

              {/* Пароль не потрібен для Google SignUp */}
              {!isGoogleSignUp && (
                <>
                <label htmlFor="password" className="register-page__label">
                  Пароль
                </label>
                <input
                  className="register-page__input register-page__input--password"
                  type="password"
                  placeholder="Вкажіть пароль"
                  name="password"
                  id="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
                </>
              )}

              {/* Попередження для Google реєстрації, якщо email не підтверджений */}
              {isGoogleSignUp && (
                <p className="register-page__warning">{!formData.verified_email && 'Email не підтверджено'}</p>
              )}

              {/* Кнопка реєстрації */}
              <button 
                type="submit" 
                className="register-page__button register-page__button--submit"
                disabled={!formData.full_name || !formData.password}
              >
                Зареєструватися
              </button>
            </>
          )}

          {/* Кнопка для продовження після введення Email */}
          {!isEmailSubmitted && (
            <button 
              type="button" 
              onClick={() => setIsEmailSubmitted(true)}
              className="register-page__button register-page__button--continue"
              disabled={!formData.email}
            >
              Продовжити
            </button>
          )}

          {/* Кнопка для реєстрації через Google */}
          {!isGoogleSignUp && !isEmailSubmitted && (
            <button 
              type="button" 
              onClick={registerWithGoogle}
              className="register-page__button register-page__button--google"
            >
              <img src={googleIcon} alt="google" />
              Продовжити з Google
            </button>
          )}
        </form>
        <p className="register-page__terms">
          By creating an account, you are agreeing to our 
          <a href="/" className="register-page__url"> Terms of Service</a> 
          <br/>
          and acknowledging receipt of our 
          <a href="/" className="register-page__url"> Privacy Policy</a> 
        </p>
        <p className="register-page__login">
          Вже зареєстровані? 
          <NavLink to={LOGIN_ROUTE} className="register-page__url">
             Вхід
          </NavLink>
        </p>
      </div>
      <div className="register-page__image-container"></div>
    </div>
  );
};

export default RegisterPage;
