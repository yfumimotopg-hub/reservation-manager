import { useEffect, useState } from "react";

import { fetchMeetingRooms } from "../../api/meetingRoomApi";
import type { MeetingRoom } from "../../types/meetingRoom";

/**
 * 会議室一覧画面コンポーネント。
 *
 * ログイン済みユーザーが参照可能な会議室一覧をAPIから取得して表示する。
 */
export const MeetingRoomListPage = () => {
  const [meetingRooms, setMeetingRooms] = useState<MeetingRoom[]>([]);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    /**
     * 会議室一覧を取得する。
     *
     * API通信に成功した場合は一覧をstateへ保存し、
     * 失敗した場合はエラーメッセージを表示する。
     */
    const loadMeetingRooms = async () => {
      try {
        const data = await fetchMeetingRooms();
        setMeetingRooms(data);
      } catch {
        setErrorMessage("会議室一覧の取得に失敗しました。");
      }
    };

    loadMeetingRooms();
  }, []);

  return (
    <div className="page">
      <div className="wide-card">
        <h1>会議室一覧</h1>

        {errorMessage && <p className="error">{errorMessage}</p>}

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>会議室名</th>
              <th>定員</th>
              <th>場所</th>
              <th>状態</th>
            </tr>
          </thead>
          <tbody>
            {meetingRooms.map((meetingRoom) => (
              <tr key={meetingRoom.id}>
                <td>{meetingRoom.id}</td>
                <td>{meetingRoom.name}</td>
                <td>{meetingRoom.capacity}</td>
                <td>{meetingRoom.location}</td>
                <td>{meetingRoom.is_active ? "有効" : "無効"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};