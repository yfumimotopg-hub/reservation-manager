import { apiClient } from "./client";
import type {
  Reservation,
  ReservationCreateRequest,
} from "../types/reservation";

/**
 * 予約一覧APIを呼び出す。
 *
 * ログイン済みユーザーが参照可能な予約情報を取得する。
 *
 * @returns 予約一覧
 */
export const fetchReservations = async (): Promise<Reservation[]> => {
  const response = await apiClient.get<Reservation[]>("/reservations");
  return response.data;
};

/**
 * 予約登録APIを呼び出す。
 *
 * 指定したユーザー、会議室、予約時間をもとに新規予約を作成する。
 *
 * @param request 予約登録リクエスト
 * @returns 登録された予約情報
 */
export const createReservation = async (
  request: ReservationCreateRequest,
): Promise<Reservation> => {
  const response = await apiClient.post<Reservation>("/reservations", request);
  return response.data;
};