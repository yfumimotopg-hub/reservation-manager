export type User = {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
  is_active: boolean;
};