import { apiClient } from "./client";
import type { User } from "../types/user";

/**
 * ユーザー一覧APIを呼び出す。
 *
 * 管理者ユーザーが予約登録時のユーザー選択肢として使用する。
 *
 * @returns ユーザー一覧
 */
export const fetchUsers = async (): Promise<User[]> => {
  const response = await apiClient.get<User[]>("/users");
  return response.data;
};