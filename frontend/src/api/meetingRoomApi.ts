import { apiClient } from "./client";
import type { MeetingRoom } from "../types/meetingRoom";

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