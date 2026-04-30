import { apiClient } from "./client";
import type {
  MeetingRoom,
  MeetingRoomCreateRequest,
  MeetingRoomUpdateRequest,
} from "../types/meetingRoom";

/**
 * 会議室一覧APIを呼び出す。
 *
 * ログイン済みユーザーが参照可能な会議室情報を取得する。
 *
 * @returns 会議室一覧
 */
export const fetchMeetingRooms = async (): Promise<MeetingRoom[]> => {
  const response = await apiClient.get<MeetingRoom[]>("/meeting-rooms");
  return response.data;
};

/**
 * 会議室登録APIを呼び出す。
 *
 * 管理者ユーザーが新しい会議室を登録するために使用する。
 *
 * @param request 会議室登録リクエスト
 * @returns 登録された会議室情報
 */
export const createMeetingRoom = async (
  request: MeetingRoomCreateRequest,
): Promise<MeetingRoom> => {
  const response = await apiClient.post<MeetingRoom>("/meeting-rooms", request);
  return response.data;
};

/**
 * 会議室更新APIを呼び出す。
 *
 * 管理者ユーザーが既存の会議室情報を更新するために使用する。
 *
 * @param meetingRoomId 更新対象の会議室ID
 * @param request 会議室更新リクエスト
 * @returns 更新後の会議室情報
 */
export const updateMeetingRoom = async (
  meetingRoomId: number,
  request: MeetingRoomUpdateRequest,
): Promise<MeetingRoom> => {
  const response = await apiClient.put<MeetingRoom>(
    `/meeting-rooms/${meetingRoomId}`,
    request,
  );

  return response.data;
};

/**
 * 会議室無効化APIを呼び出す。
 *
 * 管理者ユーザーが会議室を物理削除せず、無効状態にするために使用する。
 *
 * @param meetingRoomId 無効化対象の会議室ID
 * @returns 無効化後の会議室情報
 */
export const deactivateMeetingRoom = async (
  meetingRoomId: number,
): Promise<MeetingRoom> => {
  const response = await apiClient.delete<MeetingRoom>(
    `/meeting-rooms/${meetingRoomId}`,
  );

  return response.data;
};