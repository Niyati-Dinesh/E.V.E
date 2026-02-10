//api/auth.js

import { apiFetch } from "./client";


export const login = (email, password) =>
  apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const register = (email, password) =>
  apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const getMe = () =>
  apiFetch("/auth/me");

export const logout = () =>
  apiFetch("/auth/logout", { method: "POST" });