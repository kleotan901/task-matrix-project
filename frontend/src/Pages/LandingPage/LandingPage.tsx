import { NavLink } from "react-router-dom"
import { Header } from "../../Components/Header"
import { REGISTER_ROUTE } from "../../utils/const";
import { Footer } from "../../Components/Footer";

import "../../style/top-content.scss";
import "../../style/goal.scss";
import "../../style/coach.scss";
import "../../style/action.scss";


import projects from "../../icons/projects.png";
import taskdone from "../../icons/task-done.png";
import portret from "../../icons/portret.png";
import taskslist from "../../icons/tasks-list.png";
import delegate from "../../icons/deligate.png";
import old_cards from "../../icons/old_cards.png";

const LandingPage = () => {
  return (
    <div>
      <Header />
      <main>
        <section className="top-content">
          <div className="wrapper">        
            <h1 className="top-content__title title">Розумна організація робочих <br /> та особистих завдань</h1>
            <p className="top-content__description">Структуруйте свій день, визначайте пріорітети <br /> та оптимізуйте свій час завдяки матриці Ейзенхауера</p>
              <div className="top-content__button">
                <NavLink to={REGISTER_ROUTE} className="button button--softBluePurple button--padding-139 link link--text-white">
                  Почати
                </NavLink>
              </div>
            <div className="top-content__pictures">
              <div className="top-content__picture top-content__picture--skyBlue">
                <div className="top-content__picture--inner-square">
                </div>
              </div>
              <div className="top-content__picture top-content__picture--padding-for-circle top-content__picture--sunYellow">
                <div className="top-content__picture--inner-circle top-content__picture--softBluePurple-2">
                </div>
              </div>
              <div className="top-content__picture top-content__picture--padding-for-checkmark top-content__picture--softBluePurple">
                <div className="top-content__picture--inner-checkmark">
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="goal">
          <div className="wrapper">
            <h1 className="goal__title title">Quatrix</h1>
            <div className="goal__description">
              <p className="goal__text text">Створений для того, щоб допомогти вам впорядкувати ваші завдання, визначити пріоритети та досягти максимальних результатів.</p>
              <p className="goal__text text">Основою нашого підходу є матриця Ейзенхауера – потужний інструмент для розподілу завдань за важливістю та терміновістю.</p>
            </div>
            <button className="goal__button button button--softBluePurple button--padding-114">
              <NavLink to={REGISTER_ROUTE} className="link link--text-white">
                Почати
              </NavLink>
            </button>
            <div className="goal__carts">
              <div className="cart cart--softRose">
                <h3 className="cart__title">Матриця <br /> Ейзенхауера</h3>
                <p className="cart__description">Створюй та організовуй завдання <br /> відповідно до Матриці Ейзенхауера, що дозволяє легко розподіляти справи за важливістю та терміновості.</p>
                <div className="cart__illustration">
                  <p className="cart__illustration--text">
                    <div className="cart__illustration--img  cart__illustration--img-one"></div>
                    Важливо і терміново
                  </p>
                  <p className="cart__illustration--active">
                    <div className="cart__illustration--img cart__illustration--img-two"></div>
                    Важливо, але не терміново
                  </p>
                  <p className="cart__illustration--text">
                    <div className="cart__illustration--img cart__illustration--img-three"></div>
                    Не важливо, але терміново
                  </p>
                  <p className="cart__illustration--text">
                    <div className="cart__illustration--img cart__illustration--img-four"></div>
                    Не важливо і не терміново
                  </p>
                </div>
              </div>
              <div className="cart cart--skyBlue cart--white">
                <h3 className="cart__title">Статистика та <br /> аналітика</h3>
                <p className="cart__description">Отримуйте звіти про свою <br /> продуктивність: кількість виконаних завдань, прогрес, порівняно з минулим місяцем.</p>
                <img src={old_cards} alt="old cards" className="cart__photos" />
              </div>
              <div className="cart cart--softRose">
                <h3 className="cart__title">Робочий <br /> та особистий фокус</h3>
                <p className="cart__description cart__description--margin-bottom-37">Організуйте роботу і особисті справи: додавайте завдання, пріоритезуйте їх, і тримайте все під контролем у зручному форматі.</p>
                <div className="cart__photo-block">
                  <img src={projects} alt="projects" className="cart__photo" />
                </div>
              </div>
              <div className="cart cart--span-2 cart--softBluePurple cart--white">
                <h3 className="cart__title">Персональний коучинг</h3>
                <div className="cart__description cart__description--margin-bottom-30 cart__description--block">
                  <p>Отримуйте підтримку коуча для організації та досягнення ваших цілей, покращуючи ефективність роботи та життя.</p>
                  <p>Коуч підтримає вас на кожному етапі, допомагаючи організувати простір і досягати важливих цілей.</p>
                </div>
                <div className="cart__block-photo">
                  <img src={portret} alt="portret" className="cart__portret" />
                  <img src={taskslist} alt="tasks list" className="cart__photo-list"/>
                </div>
                <div className="cart__block-photo--2">
                <img src={taskdone} alt="task done" className="cart__img" />
                </div>
              </div>
              <div className="cart cart--sunYellow">
                <h3 className="cart__title">Розподіл <br /> відповідальності</h3>
                <p className="cart__description cart__description--margin-bottom-25">Призначайте відповідальних або додавайте помічників, щоб працювати разом і швидше досягати результатів.</p>
                <div className="cart__photo-block">
                  <img src={delegate} alt="delegate" className="cart__photo-delegate" />
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="coach">
          <div className="wrapper">
            <h2 className="coach__title title">
              Професійна підтримка
            </h2>
            <div className="coach__description">
              <p className="coach__text">Коуч допоможе вам грамотно використовувати матрицю Ейзенхауера для досягнення результату</p>
              <p className="coach__text">Знайдіть оптимальний план для своїх потреб: від базових функцій до преміум можливостей.</p>
            </div>
            <div className="coach__price-items">
              <div 
                className="coach__price-item price-item"
              >
                <h4 
                  className="price-item__title price-item__title--white"
                >
                  Базовий
                </h4>
                <p className="price-item__description">
                  Отримайте доступ до основних функцій безкоштовно. Пріоритизуйте свої завдання
                </p>
                <h3 className="price-item__price price-item__price">
                  0 грн/міс
                </h3>
                <NavLink to={REGISTER_ROUTE} className="price-item__button button button--white button--padding-139 link link--text-black">
                  Обрати
                </NavLink>

                <ul className="price-item__features">
                  <li className="price-item__feature">Пріоретизація завдань</li>
                  <li className="price-item__feature">Статистика</li>
                  <li className="price-item__feature">Організація простору</li>
                  <li className="price-item__feature">Без фінансових вкладень</li>
                </ul>
              </div>
              <div 
                className="coach__price-item price-item"
              >
                <h4 
                  className="price-item__title price-item__title--skyBlue"
                >
                  Преміум
                </h4>
                <p className="price-item__description">
                  Для тих, хто хоче зробити значний прогрес у впорядкуванні свого простору
                </p>
                <h3 className="price-item__price price-item__price--skyBlue">
                  399 грн/міс
                </h3>
                <button className="price-item__button button button--skyBlue button--width-100">
                  <NavLink to="/" className="link link--text-white">
                    Обрати
                  </NavLink>
                </button>
                <ul className="price-item__features">
                  <li className="price-item__feature">Доступ до закритих вебінарів</li>
                  <li className="price-item__feature">6 консультації на місяць</li>
                  <li className="price-item__feature">Пріорітетна підтримка 24/7</li>
                  <li className="price-item__feature">Необмежина кількість проєктів</li>
                </ul>
              </div>
              <div 
                className="coach__price-item price-item"
              >
                <h4 
                  className="price-item__title price-item__title--softBluePurple"
                >
                  Профі
                </h4>
                <p className="price-item__description">
                  Отримайте максимум підтримки та інструментів для досягнення ваших цілей
                </p>
                <h3 className="price-item__price price-item__price--softBluePurple">
                  699 грн/міс
                </h3>
                <button className="price-item__button button button--softBluePurple button--padding-139">
                  <NavLink to="/" className="link link--text-white">
                    Обрати
                  </NavLink>
                </button>
                <ul className="price-item__features">
                  <li className="price-item__feature">До 20 консультацій на місяць</li>
                  <li className="price-item__feature">Розширений план дій з постійним коригуванням</li>
                  <li className="price-item__feature">Індивідуальні щотижневі тренінги</li>
                  <li className="price-item__feature">Управління завданнями та аналітика коучем. </li>
                </ul>
              </div>
            </div>
          </div>
        </section>
        <section className="action">
          <div className="wrapper">
            <h1 className="action__title title title--white title--center">
              Почни працювати над своїми <br /> цілями вже сьогодні!
            </h1>
            <div className="action__button">
              <NavLink to={REGISTER_ROUTE} className="button button--forStart button--padding-114 button--border-white link link--text-white">
                Почати
              </NavLink>
            </div>
          </div>
        </section>
        <Footer />    
      </main>      
    </div>
  )
}
export default LandingPage;