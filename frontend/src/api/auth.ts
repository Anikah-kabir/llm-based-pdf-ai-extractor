import api from "../lib/axios"; // Axios instance
import http from "../lib/http"; // Http instance

export interface RegisterPayload {
  full_name: string;
  username: string;
  email: string;
  phone: string;
  birthdate?: string;
  password: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  phone: string;
  birthdate?: string;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

//Fetch Current Logged-in User
export const fetchCurrentUser = async (): Promise<User> => {
  const res = await http.get<User>("/auth/me");
  return res;
};

//Register User
export const registerUser = async (data: RegisterPayload): Promise<{ msg: string }> => {
  const res = await http.post<{ msg: string }>("/auth/register", data);
  return res;
};

//Login User and Store Token
export const loginUser = async (username: string, password: string): Promise<LoginResponse> => {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);
  const res = await http.post<LoginResponse>("/auth/login", formData);
  const token = res.access_token
  localStorage.setItem("token", token);
  api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  return res;
};
