import axios from "axios";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const api = axios.create({
  baseURL: apiBaseUrl,
  withCredentials: true
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail ?? error.message;
    return Promise.reject(new Error(message));
  }
);

export default api;
