import { FormEvent, useEffect, useState } from "react";

import { fetchCurrentUser } from "../../api/authApi";
import { fetchMeetingRooms } from "../../api/meetingRoomApi";
import { createReservation, fetchReservations } from "../../api/reservationApi";
import { fetchUsers } from "../../api/userApi";
import type { CurrentUser } from "../../types/auth";
import type { MeetingRoom } from "../../types/meetingRoom";
import type { Reservation } from "../../types/reservation";
import type { User } from "../../types/user";

/**
 * 予約一覧画面コンポーネント。
 *
 * ログイン済みユーザーが予約一覧を確認し、新規予約を登録できる画面。
 * adminの場合はユーザー一覧から予約者を選択し、userの場合は自分自身を予約者として扱う。
 */
export const ReservationListPage = () => {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [meetingRooms, setMeetingRooms] = useState<MeetingRoom[]>([]);
  const [users, setUsers] = useState<User[]>([]);

  const [userId, setUserId] = useState<number | "">("");
  const [meetingRoomId, setMeetingRoomId] = useState<number | "">("");
  const [title, setTitle] = useState("");
  const [startAt, setStartAt] = useState("");
  const [endAt, setEndAt] = useState("");

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const isAdmin = currentUser?.role === "admin";

  /**
   * 画面表示に必要なログイン中ユーザー、予約一覧、会議室一覧、ユーザー一覧を取得する。
   *
   * users API は admin 専用のため、一般ユーザーの場合はログイン中ユーザーのみを選択肢として扱う。
   */
  const loadInitialData = async () => {
    setErrorMessage("");

    try {
      const user = await fetchCurrentUser();
      const [reservationData, meetingRoomData] = await Promise.all([
        fetchReservations(),
        fetchMeetingRooms(),
      ]);

      setCurrentUser(user);
      setReservations(reservationData);
      setMeetingRooms(meetingRoomData.filter((room) => room.is_active));

      if (user.role === "admin") {
        const userData = await fetchUsers();
        const activeUsers = userData.filter((targetUser) => targetUser.is_active);

        setUsers(activeUsers);

        if (activeUsers.length > 0) {
          setUserId(activeUsers[0].id);
        }
      } else {
        setUsers([
          {
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role,
            is_active: user.is_active,
          },
        ]);
        setUserId(user.id);
      }

      const activeMeetingRoom = meetingRoomData.find((room) => room.is_active);

      if (activeMeetingRoom) {
        setMeetingRoomId(activeMeetingRoom.id);
      }
    } catch {
      setErrorMessage("予約情報の取得に失敗しました。");
    }
  };

  /**
   * 予約一覧を再取得する。
   *
   * 予約登録後に一覧表示を最新化するために使用する。
   */
  const reloadReservations = async () => {
    const reservationData = await fetchReservations();
    setReservations(reservationData);
  };

  /**
   * 予約登録フォームを初期化する。
   */
  const resetForm = () => {
    setTitle("");
    setStartAt("");
    setEndAt("");
  };

  /**
   * ユーザーIDからユーザー名を取得する。
   *
   * @param targetUserId 表示対象のユーザーID
   * @returns ユーザー名。見つからない場合はID表示。
   */
  const getUserName = (targetUserId: number) => {
    const user = users.find((targetUser) => targetUser.id === targetUserId);
    return user ? user.name : `ID: ${targetUserId}`;
  };

  /**
   * 会議室IDから会議室名を取得する。
   *
   * @param targetMeetingRoomId 表示対象の会議室ID
   * @returns 会議室名。見つからない場合はID表示。
   */
  const getMeetingRoomName = (targetMeetingRoomId: number) => {
    const meetingRoom = meetingRooms.find((room) => room.id === targetMeetingRoomId);
    return meetingRoom ? meetingRoom.name : `ID: ${targetMeetingRoomId}`;
  };

  /**
   * datetime-local の値をAPI送信用のISO文字列に変換する。
   *
   * @param value datetime-local入力値
   * @returns API送信用日時文字列
   */
  const toApiDateTime = (value: string) => {
    return value;
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  /**
   * 予約登録フォーム送信時の処理。
   *
   * 入力された予約者、会議室、時間帯をもとに予約登録APIを呼び出す。
   * 時間重複などの業務エラーは画面上に表示する。
   *
   * @param event フォーム送信イベント
   */
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!userId || !meetingRoomId) {
      setErrorMessage("予約者と会議室を選択してください。");
      return;
    }

    try {
      await createReservation({
        user_id: Number(userId),
        meeting_room_id: Number(meetingRoomId),
        title,
        start_at: toApiDateTime(startAt),
        end_at: toApiDateTime(endAt),
      });

      setSuccessMessage("予約を登録しました。");
      resetForm();
      await reloadReservations();
    } catch {
      setErrorMessage(
        "予約の登録に失敗しました。予約時間が重複している可能性があります。",
      );
    }
  };

  return (
    <div className="page">
      <div className="wide-card">
        <div className="page-title-row">
          <div>
            <h1>予約一覧</h1>
            <p className="description">
              ログイン中: {currentUser?.name}（{currentUser?.role}）
            </p>
          </div>
        </div>

        {errorMessage && <p className="error">{errorMessage}</p>}
        {successMessage && <p className="success">{successMessage}</p>}

        <form onSubmit={handleSubmit} className="room-form">
          <h2>予約登録</h2>

          <div className="form-grid reservation-form-grid">
            <label>
              予約者
              <select
                value={userId}
                onChange={(event) => setUserId(Number(event.target.value))}
                disabled={!isAdmin}
                required
              >
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              会議室
              <select
                value={meetingRoomId}
                onChange={(event) =>
                  setMeetingRoomId(Number(event.target.value))
                }
                required
              >
                {meetingRooms.map((meetingRoom) => (
                  <option key={meetingRoom.id} value={meetingRoom.id}>
                    {meetingRoom.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              タイトル
              <input
                type="text"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                required
              />
            </label>

            <label>
              開始日時
              <input
                type="datetime-local"
                value={startAt}
                onChange={(event) => setStartAt(event.target.value)}
                required
              />
            </label>

            <label>
              終了日時
              <input
                type="datetime-local"
                value={endAt}
                onChange={(event) => setEndAt(event.target.value)}
                required
              />
            </label>
          </div>

          <div className="button-row">
            <button type="submit">予約する</button>
          </div>
        </form>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>タイトル</th>
              <th>予約者</th>
              <th>会議室</th>
              <th>開始日時</th>
              <th>終了日時</th>
              <th>状態</th>
            </tr>
          </thead>
          <tbody>
            {reservations.map((reservation) => (
              <tr key={reservation.id}>
                <td>{reservation.id}</td>
                <td>{reservation.title}</td>
                <td>{getUserName(reservation.user_id)}</td>
                <td>{getMeetingRoomName(reservation.meeting_room_id)}</td>
                <td>{reservation.start_at.replace("T", " ")}</td>
                <td>{reservation.end_at.replace("T", " ")}</td>
                <td>{reservation.is_active ? "有効" : "無効"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};