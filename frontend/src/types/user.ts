export type User = {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
  is_active: boolean;
};

export type UserCreateRequest = {
  name: string;
  email: string;
  role: "admin" | "user";
};

export type UserUpdateRequest = {
  name: string;
  email: string;
  role: "admin" | "user";
  is_active: boolean;
};