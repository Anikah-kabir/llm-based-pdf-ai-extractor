import type { AxiosRequestConfig, AxiosResponse } from "axios";
import api from './axios';

const token = localStorage.getItem("token");
if (token) {
  api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}

// Utility helper
const handleResponse = <T>(res: AxiosResponse<T>): T => res.data;

const http = {
  // GET
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const res = await api.get<T>(url, config);
    return handleResponse(res);
  },

  // POST
  post: async <T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const isFormData = data instanceof FormData;
    const headers = isFormData ? { "Content-Type": "multipart/form-data" } : {};
    const res = await api.post<T>(url, data, {
      ...config,
      headers: { ...headers, ...(config?.headers || {}) },
    });
    return handleResponse(res);
  },

  // PATCH
  patch: async <T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const isFormData = data instanceof FormData;
    const headers = isFormData ? { "Content-Type": "multipart/form-data" } : {};
    const res = await api.patch<T>(url, data, {
      ...config,
      headers: { ...headers, ...(config?.headers || {}) },
    });
    return handleResponse(res);
  },

  // DELETE
  del: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const res = await api.delete<T>(url, config);
    return handleResponse(res);
  },
};
export default http;
