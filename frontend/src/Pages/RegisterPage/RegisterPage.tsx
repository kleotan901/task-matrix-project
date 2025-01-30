import { useContext, useEffect, useState } from "react";
import { signInWithPopup, User } from 'firebase/auth';
import { Context, googleAuthProvider } from "../../firebase";
import { NavLink, useNavigate } from "react-router-dom";
import { LANDING_PAGE_ROUTE, LOGIN_ROUTE, PROFILE_ROUTE } from "../../utils/const";
import { UserData } from "../../type/UserData";
import "../../style/register-page.scss";
import googleIcon from "../../icons/flat-color-icons_google.png";
import { Slider } from "../../Components/Slider";
import { postUserEmail, postUserGoodle } from "../../utils/api";
import { OrDivider } from "../../Components/OrDivider";

const RegisterPage: React.FC = () => {
  const firebaseContext = useContext(Context);
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<UserData>({
    email: '',
    full_name: '',
    password: undefined,
    verified_email: false 
  });

  const [isGoogleSignUp, setIsGoogleSignUp] = useState(false);
  const [isEmailSubmitted, setIsEmailSubmitted] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [nameError, setNameError] = useState('');

  useEffect(() => {
    if (!firebaseContext) return;

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

      setFormData(userData);
      setIsGoogleSignUp(true);
      setIsEmailSubmitted(true);

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

  // Обробка зміни полів форми
  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFormData(prevState => ({ ...prevState, [name]: value }));

    if (name === 'password' && passwordError) {
      if (validatePassword(value)) {
        setPasswordError('');
      }
    }

    if (name === 'email' && emailError) {
      if (validateEmail(value)) {
        setEmailError('');
      }
    }
  
    if (name === 'full_name' && nameError) {
      if (validateName(value)) {
        setNameError('');
      }
    }
  };

  const validatePassword = (password: string): boolean => {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  };

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };
  
  const validateName = (name: string): boolean => {
    return name.trim().length >= 2;
  };
  

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
  
    const { email, full_name, password } = formData;
  
    /* if (!email || !full_name) {
      alert("Будь ласка, заповніть усі обов'язкові поля.");
      return;
    }*/

    if (!validateEmail(email)) {
      setEmailError("Введіть коректний Email.");
      return;
    }
  
    // Перевірка імені
    if (!validateName(full_name)) {
      setNameError("Ім'я має містити щонайменше 2 символи.");
      return;
    }

    if (!validatePassword(password as string)) {
      setPasswordError("Пароль має бути не менше 8 символів і містити хоча б одну цифру, одну велику і малу літери, а також один спеціальний символ.");
      return;
    }
  
    const userData = isGoogleSignUp
      ? { email, full_name, avatar_url: formData.avatar_url, emailVerified: formData.verified_email }
      : { email, full_name, password: formData.password };
  
    localStorage.setItem('userData', JSON.stringify(userData));
    
    try {
      const response = await postUserEmail(userData);
   
      if (response.ok) {
          navigate(PROFILE_ROUTE);
      } else if (response.status === 400) {
        setEmailError("Такий акаунт уже існує.");
      } else {
          alert(response.result || `Код помилки: ${response.status}`);
      }
   } catch (error) {
      console.error("Помилка під час реєстрації:", error);
      alert("Сталася помилка. Спробуйте ще раз пізніше.");
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
          <label htmlFor="email" className={`register-page__label ${isEmailSubmitted ? 'register-page__label--disabled' : ''}`}>
            Email
          </label>
          <input
            className={`register-page__input register-page__input--email ${emailError ? 'register-page__input--error' : ''}`}
            type="email"
            id="email"
            placeholder="Введіть Email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            disabled={isEmailSubmitted}
          />
          {emailError && <p className="register-page__error">{emailError}</p>}
          {isEmailSubmitted && (
            <>
              <label htmlFor="full_name" className="register-page__label">Ім'я</label>
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
              {nameError && <p className="register-page__error">{nameError}</p>}
              {!isGoogleSignUp && (
                <>
                  <label htmlFor="password" className="register-page__label">Пароль</label>
                  <input
                    className={`register-page__input register-page__input--password ${passwordError ? 'register-page__input--error' : ''}`}
                    type="password"
                    placeholder="Вкажіть пароль"
                    name="password"
                    id="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                  {passwordError && <p className="register-page__error">{passwordError}</p>}
                </>
              )}
              <button type="submit" className="register-page__button register-page__button--submit">
                Зареєструватися
              </button>
            </>
          )}
          {!isEmailSubmitted && (
            <button 
              type="button" 
              onClick={() => setIsEmailSubmitted(true)} 
              className="register-page__button register-page__button--continue" 
              disabled={!formData.email}>
              Продовжити
            </button>
          )}
          <OrDivider />
          {!isGoogleSignUp && !isEmailSubmitted && (
            <button 
              type="button" 
              onClick={registerWithGoogle} 
              className="register-page__button register-page__button--google">
              <img src={googleIcon} alt="google" /> Продовжити з Google
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
      <div className="register-page__image-container">
        <Slider />
      </div>
    </div>
  );
};

export default RegisterPage;
