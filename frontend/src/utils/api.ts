const BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8080";

export const apiPost = async (url: string, data: object) => {
  try {
    const response = await fetch(`${BASE_URL}${url}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return await response.json();
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};
