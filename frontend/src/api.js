import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

// Add a request interceptor to include JWT token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const loginUser = (email, password) =>
  api.post("/accounts/login/", { email, password });

export const registerUser = (userData) =>
  api.post("/accounts/register/", userData);

export const refreshToken = (refresh) =>
  api.post("/accounts/login/refresh/", { refresh });

export default api;
