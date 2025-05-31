import React, { createContext, useState, useEffect } from "react";
import { loginUser, registerUser } from "../api";
import { jwtDecode } from "jwt-decode";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem("authToken"));
  const [currentUser, setCurrentUser] = useState(() => {
    const token = localStorage.getItem("authToken");
    return token ? jwtDecode(token) : null;
  });

  useEffect(() => {
    if (authToken) {
      localStorage.setItem("authToken", authToken);
      setCurrentUser(jwtDecode(authToken));
    } else {
      localStorage.removeItem("authToken");
      setCurrentUser(null);
    }
  }, [authToken]);

  const login = async (email, password) => {
    try {
      const response = await loginUser(email, password);
      setAuthToken(response.data.access);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data || "Login failed" };
    }
  };

  const register = async (userData) => {
    try {
      await registerUser(userData);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data || "Registration failed" };
    }
  };

  const logout = () => {
    setAuthToken(null);
    setCurrentUser(null);
    localStorage.removeItem("authToken");
  };

  return (
    <AuthContext.Provider value={{ currentUser, authToken, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
