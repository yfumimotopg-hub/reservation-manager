import { apiClient } from "./client";
import type { CurrentUser, LoginRequest, TokenResponse } from "../types/auth";

/**
 * ログインAPIを呼び出し、JWTアクセストークンを取得する。
 *
 * @param request ログインに使用するメールアドレスとパスワード
 * @returns アクセストークン情報
 */
export const login = async (request: LoginRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>("/auth/login", request);
  return response.data;
};

/**
 * ログイン中ユーザー情報を取得する。
 *
 * AuthorizationヘッダーのBearer Tokenをもとに、
 * バックエンド側で現在のユーザーを判定する。
 *
 * @returns ログイン中ユーザー情報
 */
export const fetchCurrentUser = async (): Promise<CurrentUser> => {
  const response = await apiClient.get<CurrentUser>("/auth/me");
  return response.data;
};