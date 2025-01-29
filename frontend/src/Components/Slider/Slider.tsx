import '../../style/slider.scss';
import photo1 from '../../icons/pexels-c.png';

export const Slider = () => {
  return (
    <div className='slider__block'>
      <img src={photo1} alt="" className='slider__photo' />
    </div>
  )
};
