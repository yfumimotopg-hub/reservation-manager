import { FormEvent, useEffect, useState } from "react";

import { fetchCurrentUser } from "../../api/authApi";
import {
  createMeetingRoom,
  deactivateMeetingRoom,
  fetchMeetingRooms,
  updateMeetingRoom,
} from "../../api/meetingRoomApi";
import type { CurrentUser } from "../../types/auth";
import type { MeetingRoom } from "../../types/meetingRoom";

/**
 * 会議室一覧画面コンポーネント。
 *
 * ログイン済みユーザーが参照可能な会議室一覧を表示し、
 * 管理者ユーザーの場合は会議室の登録・更新・無効化を行えるようにする。
 */
export const MeetingRoomListPage = () => {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [meetingRooms, setMeetingRooms] = useState<MeetingRoom[]>([]);
  const [selectedMeetingRoom, setSelectedMeetingRoom] =
    useState<MeetingRoom | null>(null);

  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState(1);
  const [location, setLocation] = useState("");

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const isAdmin = currentUser?.role === "admin";

  /**
   * 画面表示に必要なログイン中ユーザー情報と会議室一覧を取得する。
   */
  const loadInitialData = async () => {
    try {
      const [user, rooms] = await Promise.all([
        fetchCurrentUser(),
        fetchMeetingRooms(),
      ]);

      setCurrentUser(user);
      setMeetingRooms(rooms);
    } catch {
      setErrorMessage("会議室一覧の取得に失敗しました。");
    }
  };

  /**
   * 会議室一覧を再取得する。
   *
   * 登録・更新・無効化後に画面表示を最新化するために使用する。
   */
  const reloadMeetingRooms = async () => {
    const rooms = await fetchMeetingRooms();
    setMeetingRooms(rooms);
  };

  /**
   * 入力フォームを初期状態に戻す。
   */
  const resetForm = () => {
    setSelectedMeetingRoom(null);
    setName("");
    setCapacity(1);
    setLocation("");
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  /**
   * 会議室登録・更新フォーム送信時の処理。
   *
   * 選択中の会議室がある場合は更新、ない場合は新規登録を行う。
   *
   * @param event フォーム送信イベント
   */
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    try {
      if (selectedMeetingRoom) {
        await updateMeetingRoom(selectedMeetingRoom.id, {
          name,
          capacity,
          location,
          is_active: selectedMeetingRoom.is_active,
        });

        setSuccessMessage("会議室を更新しました。");
      } else {
        await createMeetingRoom({
          name,
          capacity,
          location,
        });

        setSuccessMessage("会議室を登録しました。");
      }

      resetForm();
      await reloadMeetingRooms();
    } catch {
      setErrorMessage("会議室の保存に失敗しました。");
    }
  };

  /**
   * 更新対象の会議室をフォームに反映する。
   *
   * @param meetingRoom 編集対象の会議室
   */
  const handleEdit = (meetingRoom: MeetingRoom) => {
    setSelectedMeetingRoom(meetingRoom);
    setName(meetingRoom.name);
    setCapacity(meetingRoom.capacity);
    setLocation(meetingRoom.location);
    setErrorMessage("");
    setSuccessMessage("");
  };

  /**
   * 会議室を無効化する。
   *
   * 対象会議室を物理削除せず、バックエンド側でis_active=falseに更新する。
   *
   * @param meetingRoomId 無効化対象の会議室ID
   */
  const handleDeactivate = async (meetingRoomId: number) => {
    setErrorMessage("");
    setSuccessMessage("");

    const confirmed = window.confirm("この会議室を無効化しますか？");

    if (!confirmed) {
      return;
    }

    try {
      await deactivateMeetingRoom(meetingRoomId);
      setSuccessMessage("会議室を無効化しました。");
      await reloadMeetingRooms();
    } catch {
      setErrorMessage("会議室の無効化に失敗しました。");
    }
  };

  return (
    <div className="page">
      <div className="wide-card">
        <div className="page-title-row">
          <div>
            <h1>会議室一覧</h1>
            <p className="description">
              ログイン中: {currentUser?.name}（{currentUser?.role}）
            </p>
          </div>
        </div>

        {errorMessage && <p className="error">{errorMessage}</p>}
        {successMessage && <p className="success">{successMessage}</p>}

        {isAdmin && (
          <form onSubmit={handleSubmit} className="room-form">
            <h2>{selectedMeetingRoom ? "会議室更新" : "会議室登録"}</h2>

            <div className="form-grid">
              <label>
                会議室名
                <input
                  type="text"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  required
                />
              </label>

              <label>
                定員
                <input
                  type="number"
                  min={1}
                  value={capacity}
                  onChange={(event) => setCapacity(Number(event.target.value))}
                  required
                />
              </label>

              <label>
                場所
                <input
                  type="text"
                  value={location}
                  onChange={(event) => setLocation(event.target.value)}
                  required
                />
              </label>
            </div>

            <div className="button-row">
              <button type="submit">
                {selectedMeetingRoom ? "更新する" : "登録する"}
              </button>

              {selectedMeetingRoom && (
                <button type="button" className="secondary" onClick={resetForm}>
                  キャンセル
                </button>
              )}
            </div>
          </form>
        )}

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>会議室名</th>
              <th>定員</th>
              <th>場所</th>
              <th>状態</th>
              {isAdmin && <th>操作</th>}
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
                {isAdmin && (
                  <td>
                    <div className="table-actions">
                      <button
                        type="button"
                        className="secondary"
                        onClick={() => handleEdit(meetingRoom)}
                      >
                        編集
                      </button>

                      <button
                        type="button"
                        className="danger"
                        onClick={() => handleDeactivate(meetingRoom.id)}
                        disabled={!meetingRoom.is_active}
                      >
                        無効化
                      </button>
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};