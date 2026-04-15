export interface User {
  id: string;
  email: string;
  role: "admin" | "user";
  company_id: string;
  is_active?: boolean;
  created_at?: string;
}

export interface Company {
  id: string;
  name: string;
  created_at?: string;
}

export interface AuthContextType {
  user: User | null;
  company: Company | null;
  isLoading: boolean;
  login: (email: string, password: string, company_name: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    company_name: string
  ) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

export interface ApiResponse<T> {
  success?: boolean;
  data?: T;
  error?: string;
  detail?: string;
  user?: User;
  company?: Company;
  access_token?: string;
  refresh_token?: string;
}
