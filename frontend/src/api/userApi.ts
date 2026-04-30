import { apiClient } from "./client";
import type { User, UserCreateRequest, UserUpdateRequest } from "../types/user";

/**
 * ユーザー一覧APIを呼び出す。
 *
 * 管理者ユーザーがユーザー管理画面や予約登録時の選択肢として使用する。
 *
 * @returns ユーザー一覧
 */
export const fetchUsers = async (): Promise<User[]> => {
  const response = await apiClient.get<User[]>("/users");
  return response.data;
};

/**
 * ユーザー登録APIを呼び出す。
 *
 * 管理者ユーザーが新規ユーザーを登録するために使用する。
 *
 * @param request ユーザー登録リクエスト
 * @returns 登録されたユーザー情報
 */
export const createUser = async (
  request: UserCreateRequest,
): Promise<User> => {
  const response = await apiClient.post<User>("/users", request);
  return response.data;
};

/**
 * ユーザー更新APIを呼び出す。
 *
 * 管理者ユーザーが既存ユーザー情報を更新するために使用する。
 *
 * @param userId 更新対象のユーザーID
 * @param request ユーザー更新リクエスト
 * @returns 更新後のユーザー情報
 */
export const updateUser = async (
  userId: number,
  request: UserUpdateRequest,
): Promise<User> => {
  const response = await apiClient.put<User>(`/users/${userId}`, request);
  return response.data;
};

/**
 * ユーザー無効化APIを呼び出す。
 *
 * 管理者ユーザーがユーザーを物理削除せず、無効状態にするために使用する。
 *
 * @param userId 無効化対象のユーザーID
 * @returns 無効化後のユーザー情報
 */
export const deactivateUser = async (userId: number): Promise<User> => {
  const response = await apiClient.delete<User>(`/users/${userId}`);
  return response.data;
};