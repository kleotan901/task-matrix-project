import { LoginData } from '../type/LoginData';
import { UserData } from '../type/UserData';
import { apiClient } from './featchClient';

export const postUserEmail = async (data: UserData) => {
  try {
    const response = await apiClient.post('/api/profile/register/', data);
    return response;
  } catch (error: any) {
    console.error("Помилка при реєстрації через email:", error);

    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Не вдалося зареєструвати користувача через email.");
    }
  }
};

export const postUserGoodle = async (data: UserData) => {
  try {
    const response = await apiClient.post('/api/profile/google/', data);
    return response;
  } catch (error: any) {
    console.error("Помилка при реєстрації через Google:", error);

    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Не вдалося зареєструвати користувача через Google.");
    }
  }
};

export const loginWithEmail = async (data: LoginData) => {
  try {
    const response = await apiClient.post('/api/profile/login/', data);
    return response;
  } catch (error: any) {
    console.error("Помилка при логіні через email:", error);

    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Не вдалося увійти через email.");
    }
  }
};
