import { useState } from 'react';
import '../../style/slider.scss';

import katerynasyshchenko from '../../icons/pexels-c.png';
import cristianrojas from '../../icons/pexels-cristian-rojas.png';
import karolinagrabowska from '../../icons/pexels-karolina-grabowska.png';
import olenkabohovyk from '../../icons/pexels-olenkabohovyk.png';

const images = [
  katerynasyshchenko,
  cristianrojas,
  karolinagrabowska,
  olenkabohovyk
];

export const Slider = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev === 0 ? images.length - 1 : prev - 1));
  };

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev === images.length - 1 ? 0 : prev + 1));
  };

  return (
    <div className='slider__block'>
      <img src={images[currentIndex]} alt='' className='slider__photo' />
      <div className='slider__controls'>
        <button className='slider__button' onClick={prevSlide}>&lt;</button>
        <button className='slider__button' onClick={nextSlide}>&gt;</button>
      </div>
    </div>
  );
};
