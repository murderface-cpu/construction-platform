import axios from "axios";
import { useAuthStore } from "@/store/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let refreshQueue: Array<(token: string) => void> = [];

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err?.response?.status === 401 && !original._retry) {
      const state = useAuthStore.getState();
      const refreshToken = (state as any).refreshToken;
      if (!refreshToken) { state.logout(); return Promise.reject(err); }

      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push((newToken) => {
            original.headers.Authorization = `Bearer ${newToken}`;
            resolve(api(original));
          });
        });
      }

      original._retry = true;
      isRefreshing = true;
      try {
        const { data } = await axios.post(
          `${api.defaults.baseURL}/auth/token/refresh/`,
          { refresh: refreshToken }
        );
        const newAccess: string = data.access;
        (useAuthStore.getState() as any).setToken(newAccess);
        refreshQueue.forEach((cb) => cb(newAccess));
        refreshQueue = [];
        original.headers.Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch {
        state.logout();
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login/", { email, password }),
  register: (data: { email: string; password: string; password_confirm: string; name: string; role: string }) =>
    api.post("/auth/register/", data),
  logout: (refresh: string) =>
    api.post("/auth/logout/", { refresh }),
  me: () => api.get("/auth/me/"),
  updateMe: (data: Record<string, unknown>) =>
    api.patch("/auth/me/", data),
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post("/auth/change-password/", data),
};

export const contractorsApi = {
  list: (params?: Record<string, string>) =>
    api.get("/contractors/", { params }),
  get: (id: string) => api.get(`/contractors/${id}/`),
  me: () => api.get("/contractors/me/"),
  updateMe: (data: Record<string, unknown>) =>
    api.patch("/contractors/me/", data),
  portfolio: {
    list: () => api.get("/contractors/me/portfolio/"),
    add: (data: Record<string, unknown>) =>
      api.post("/contractors/me/portfolio/", data),
    update: (id: string, data: Record<string, unknown>) =>
      api.patch(`/contractors/me/portfolio/${id}/`, data),
    remove: (id: string) => api.delete(`/contractors/me/portfolio/${id}/`),
    uploadUrl: (id: string) =>
      api.post(`/contractors/me/portfolio/${id}/upload-url/`),
  },
};

export const bookingsApi = {
  list: () => api.get("/bookings/"),
  get: (id: string) => api.get(`/bookings/${id}/`),
  create: (data: Record<string, unknown>) => api.post("/bookings/", data),
  updateStatus: (id: string, status: string) =>
    api.patch(`/bookings/${id}/status/`, { status }),
  complete: (id: string) => api.post(`/bookings/${id}/complete/`),
  cancel: (id: string) => api.post(`/bookings/${id}/cancel/`),
  availability: {
    list: () => api.get("/bookings/availability/"),
    listForContractor: (cid: string) =>
      api.get(`/bookings/availability/${cid}/`),
    add: (data: Record<string, unknown>) =>
      api.post("/bookings/availability/", data),
  },
};

export const projectsApi = {
  list: () => api.get("/projects/"),
  get: (id: string) => api.get(`/projects/${id}/`),
  create: (data: Record<string, unknown>) => api.post("/projects/", data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/projects/${id}/`, data),
  assign: (id: string, data: Record<string, unknown>) =>
    api.post(`/projects/${id}/assign/`, data),
  milestones: {
    list: (pid: string) => api.get(`/projects/${pid}/milestones/`),
    add: (pid: string, data: Record<string, unknown>) =>
      api.post(`/projects/${pid}/milestones/`, data),
    update: (pid: string, mid: string, data: Record<string, unknown>) =>
      api.patch(`/projects/${pid}/milestones/${mid}/`, data),
    remove: (pid: string, mid: string) =>
      api.delete(`/projects/${pid}/milestones/${mid}/`),
  },
};

export const designsApi = {
  list: () => api.get("/designs/"),
  get: (id: string) => api.get(`/designs/${id}/`),
  save: (id: string) => api.post(`/designs/${id}/save/`),
  unsave: (id: string) => api.delete(`/designs/${id}/save/`),
  saved: () => api.get("/designs/saved/"),
};

export const reviewsApi = {
  list: (contractorId: string) =>
    api.get("/reviews/", { params: { contractor_id: contractorId } }),
  create: (data: Record<string, unknown>) => api.post("/reviews/", data),
};

export const notificationsApi = {
  list: (unreadOnly = false) =>
    api.get("/notifications/", { params: unreadOnly ? { unread: "true" } : {} }),
  markRead: (id: string) => api.patch(`/notifications/${id}/read/`),
  markAllRead: () => api.post("/notifications/mark-all-read/"),
  unreadCount: () => api.get("/notifications/unread-count/"),
};
