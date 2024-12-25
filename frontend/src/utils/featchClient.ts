const BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8080";

type RequestMethod = "GET" | "POST" | "PATCH" | "DELETE";

const apiRequest = async <T>(
  url: string,
  method: RequestMethod = "GET",
  data?: object
): Promise<{
  ok: boolean;
  status: number;
  result: T;
}> => {
  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${BASE_URL}${url}`, options);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Помилка відповіді сервера:", response.status, errorText);
      throw new Error(`Сервер повернув статус ${response.status}: ${errorText}`);
    }

    const contentType = response.headers.get("content-type");
    let result;

    if (contentType?.includes("application/json")) {
      result = await response.json();
    } else {
      result = await response.text();
    }

    return {
      ok: response.ok,
      status: response.status,
      result: result as T,
    };
  } catch (error: any) {
    console.error("API Error:", error);
    throw new Error("Не вдалося виконати запит до сервера: " + error.message);
  }
};

export const apiClient = {
  get: <T>(url: string) => apiRequest<T>(url, "GET"),
  post: <T>(url: string, data: object) => apiRequest<T>(url, "POST", data),
  patch: <T>(url: string, data: object) => apiRequest<T>(url, "PATCH", data),
  delete: <T>(url: string) => apiRequest<T>(url, "DELETE"),
};
