import { apiClient } from "./client";
import type {
  Reservation,
  ReservationCreateRequest,
  ReservationUpdateRequest,
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

/**
 * 予約更新APIを呼び出す。
 *
 * 指定した予約IDの予約内容を更新する。
 *
 * @param reservationId 更新対象の予約ID
 * @param request 予約更新リクエスト
 * @returns 更新後の予約情報
 */
export const updateReservation = async (
  reservationId: number,
  request: ReservationUpdateRequest,
): Promise<Reservation> => {
  const response = await apiClient.put<Reservation>(
    `/reservations/${reservationId}`,
    request,
  );

  return response.data;
};

/**
 * 予約無効化APIを呼び出す。
 *
 * 予約を物理削除せず、is_active=false に更新する。
 *
 * @param reservationId 無効化対象の予約ID
 * @returns 無効化後の予約情報
 */
export const deactivateReservation = async (
  reservationId: number,
): Promise<Reservation> => {
  const response = await apiClient.delete<Reservation>(
    `/reservations/${reservationId}`,
  );

  return response.data;
};