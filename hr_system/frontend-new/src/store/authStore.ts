import { create } from 'zustand';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('authToken'),
  isAuthenticated: !!localStorage.getItem('authToken'),
  
  login: async (email: string, password: string) => {
    try {
      // Mock login - replace with actual API call
      const mockResponse = {
        user: {
          id: '1',
          name: 'Admin User',
          email: email,
          role: 'admin',
          department: 'HR'
        },
        token: 'mock-jwt-token'
      };
      
      localStorage.setItem('authToken', mockResponse.token);
      set({
        user: mockResponse.user,
        token: mockResponse.token,
        isAuthenticated: true
      });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('authToken');
    set({
      user: null,
      token: null,
      isAuthenticated: false
    });
  },
  
  setUser: (user: User) => set({ user }),
  setToken: (token: string) => {
    localStorage.setItem('authToken', token);
    set({ token, isAuthenticated: !!token });
  }
}));
