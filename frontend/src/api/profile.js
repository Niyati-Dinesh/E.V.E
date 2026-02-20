// api/profile.js
import { apiFetch } from "./client";

export const getProfile = () => apiFetch("/api/profile");

export const updateProfile = (data) =>
  apiFetch("/api/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const uploadAvatar = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("http://localhost:8000/api/profile/avatar", {
    method: "POST",
    credentials: "include",
    body: formData,
    // No Content-Type header — browser sets it with boundary for multipart
  });

  if (!res.ok) {
    let message = "Upload failed";
    try {
      const err = await res.json();
      message = err.detail || err.message || message;
    } catch (_) {}
    throw new Error(message);
  }

  return res.json();
};