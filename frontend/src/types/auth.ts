export type LoginRequest = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type CurrentUser = {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
  is_active: boolean;
};