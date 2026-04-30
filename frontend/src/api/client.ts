import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

/**
 * バックエンドAPIと通信するための共通axiosインスタンス。
 *
 * APIのbaseURL設定と、共通リクエスト設定を集約する。
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * APIリクエスト前にJWTアクセストークンをAuthorizationヘッダーへ設定する。
 *
 * localStorageに保存されたアクセストークンが存在する場合、
 * Bearer TokenとしてAPIへ送信する。
 */
apiClient.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("accessToken");

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});