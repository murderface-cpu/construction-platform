import { create } from "zustand";

export type BookingStatus = "pending" | "accepted" | "rejected" | "cancelled" | "completed";

export interface Booking {
  id: string;
  contractor_id?: string;
  contractorId?: string;
  contractorName?: string;
  contractorAvatarUrl?: string;
  date?: string;
  timeSlot?: string;
  notes?: string;
  status: BookingStatus;
  createdAt?: string;
  created_at?: string;
  [key: string]: unknown;
}

interface BookingsState {
  bookings: Booking[];
  setBookings: (bookings: Booking[]) => void;
  addBooking: (b: Booking) => void;
  updateBooking: (id: string, patch: Partial<Booking>) => void;
  removeBooking: (id: string) => void;
}

export const useBookingsStore = create<BookingsState>()((set, get) => ({
  bookings: [],
  setBookings: (bookings) => set({ bookings }),
  addBooking: (booking) =>
    set({ bookings: [booking, ...get().bookings] }),
  updateBooking: (id, patch) =>
    set({
      bookings: get().bookings.map((b) =>
        b.id === id ? { ...b, ...patch } : b
      ),
    }),
  removeBooking: (id) =>
    set({ bookings: get().bookings.filter((b) => b.id !== id) }),
}));
