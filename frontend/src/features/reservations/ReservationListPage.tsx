import { FormEvent, useEffect, useMemo, useState } from "react";

import { fetchCurrentUser } from "../../api/authApi";
import { fetchMeetingRooms } from "../../api/meetingRoomApi";
import {
  createReservation,
  deactivateReservation,
  fetchReservations,
  updateReservation,
} from "../../api/reservationApi";
import { fetchUsers } from "../../api/userApi";
import type { CurrentUser } from "../../types/auth";
import type { MeetingRoom } from "../../types/meetingRoom";
import type { Reservation } from "../../types/reservation";
import type { User } from "../../types/user";



type DisplayMode = "list" | "calendar";

/**
 * 予約一覧画面コンポーネント。
 *
 * ログイン済みユーザーが予約一覧を確認し、新規予約を登録できる画面。
 * リスト表示とカレンダー表示を切り替えて予約情報を確認できる。
 */
export const ReservationListPage = () => {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [meetingRooms, setMeetingRooms] = useState<MeetingRoom[]>([]);
  const [users, setUsers] = useState<User[]>([]);

  const [displayMode, setDisplayMode] = useState<DisplayMode>("list");
  const [calendarMonth, setCalendarMonth] = useState(() => new Date());

  const [userId, setUserId] = useState<number | "">("");
  const [meetingRoomId, setMeetingRoomId] = useState<number | "">("");
  const [title, setTitle] = useState("");
  const [startAt, setStartAt] = useState("");
  const [endAt, setEndAt] = useState("");

  const [selectedReservation, setSelectedReservation] =
  useState<Reservation | null>(null);

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
    setSelectedReservation(null);
    setTitle("");
    setStartAt("");
    setEndAt("");

    if (currentUser?.role === "admin") {
      setUserId(users[0]?.id ?? "");
    } else {
      setUserId(currentUser?.id ?? "");
    }

    setMeetingRoomId(meetingRooms[0]?.id ?? "");
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
   * 日時文字列を画面表示用に整形する。
   *
   * @param value 日時文字列
   * @returns 表示用日時
   */
  const formatDateTime = (value: string) => {
    return value.replace("T", " ");
  };

  /**
   * 日付を YYYY-MM-DD 形式に変換する。
   *
   * @param date 変換対象の日付
   * @returns YYYY-MM-DD形式の日付文字列
   */
  const formatDateKey = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  };

  /**
   * 予約開始日時から日付キーを取得する。
   *
   * @param reservation 予約情報
   * @returns YYYY-MM-DD形式の日付文字列
   */
  const getReservationDateKey = (reservation: Reservation) => {
    return reservation.start_at.slice(0, 10);
  };

  /**
   * カレンダー表示用の日付配列を生成する。
   *
   * 月初の曜日に合わせて前方に空白日を追加し、
   * 月末の曜日に合わせて後方にも空白日を追加する。
   */
  const calendarDays = useMemo(() => {
    const year = calendarMonth.getFullYear();
    const month = calendarMonth.getMonth();

    const firstDate = new Date(year, month, 1);
    const lastDate = new Date(year, month + 1, 0);

    const firstDayOfWeek = firstDate.getDay();
    const daysInMonth = lastDate.getDate();

    const days: (Date | null)[] = [];

    for (let index = 0; index < firstDayOfWeek; index += 1) {
      days.push(null);
    }

    for (let day = 1; day <= daysInMonth; day += 1) {
      days.push(new Date(year, month, day));
    }

    while (days.length % 7 !== 0) {
      days.push(null);
    }

    return days;
  }, [calendarMonth]);

  /**
   * 表示中の月を1か月戻す。
   */
  const handlePreviousMonth = () => {
    setCalendarMonth(
      new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() - 1, 1),
    );
  };

  /**
   * 表示中の月を1か月進める。
   */
  const handleNextMonth = () => {
    setCalendarMonth(
      new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() + 1, 1),
    );
  };

  /**
   * 指定日付に紐づく予約一覧を取得する。
   *
   * @param date 対象日付
   * @returns 対象日付の予約一覧
   */
  const getReservationsByDate = (date: Date) => {
    const dateKey = formatDateKey(date);

    return reservations.filter(
      (reservation) =>
        reservation.is_active && getReservationDateKey(reservation) === dateKey,
    );
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  /**
   * ログイン中ユーザーが指定された予約を無効化できるか判定する。
   *
   * admin は全予約を無効化できる。
   * user は自分の予約のみ無効化できる。
   *
   * @param reservation 判定対象の予約
   * @returns 無効化可能な場合は true
   */
  const canDeactivateReservation = (reservation: Reservation) => {
    if (!reservation.is_active) {
      return false;
    }

    if (currentUser?.role === "admin") {
      return true;
    }

    return reservation.user_id === currentUser?.id;
  };

  /**
   * ログイン中ユーザーが指定された予約を更新できるか判定する。
   *
   * admin は全予約を更新できる。
   * user は自分の予約のみ更新できる。
   *
   * @param reservation 判定対象の予約
   * @returns 更新可能な場合は true
   */
  const canUpdateReservation = (reservation: Reservation) => {
    if (!reservation.is_active) {
      return false;
    }

    if (currentUser?.role === "admin") {
      return true;
    }

    return reservation.user_id === currentUser?.id;
  };

  /**
   * 更新対象の予約をフォームに反映する。
   *
   * @param reservation 編集対象の予約
   */
  const handleEditReservation = (reservation: Reservation) => {
    setSelectedReservation(reservation);
    setUserId(reservation.user_id);
    setMeetingRoomId(reservation.meeting_room_id);
    setTitle(reservation.title);
    setStartAt(reservation.start_at.slice(0, 16));
    setEndAt(reservation.end_at.slice(0, 16));
    setErrorMessage("");
    setSuccessMessage("");
  };

  /**
   * 予約登録・更新フォーム送信時の処理。
   *
   * 編集対象の予約がある場合は更新、ない場合は新規登録を行う。
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
      if (selectedReservation) {
        await updateReservation(selectedReservation.id, {
          user_id: Number(userId),
          meeting_room_id: Number(meetingRoomId),
          title,
          start_at: startAt,
          end_at: endAt,
          is_active: selectedReservation.is_active,
        });

        setSuccessMessage("予約を更新しました。");
      } else {
        await createReservation({
          user_id: Number(userId),
          meeting_room_id: Number(meetingRoomId),
          title,
          start_at: startAt,
          end_at: endAt,
        });

        setSuccessMessage("予約を登録しました。");
      }

      resetForm();
      await reloadReservations();
    } catch {
      setErrorMessage(
        "予約の保存に失敗しました。予約時間が重複している可能性があります。",
      );
    }
  };


  /**
   * 予約を無効化する。
   *
   * 対象予約を物理削除せず、バックエンド側で is_active=false に更新する。
   *
   * @param reservationId 無効化対象の予約ID
   */
  const handleDeactivateReservation = async (reservationId: number) => {
    setErrorMessage("");
    setSuccessMessage("");

    const confirmed = window.confirm("この予約を無効化しますか？");

    if (!confirmed) {
      return;
    }

    try {
      await deactivateReservation(reservationId);
      setSuccessMessage("予約を無効化しました。");
      await reloadReservations();
    } catch {
      setErrorMessage("予約の無効化に失敗しました。");
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

          <div className="display-mode-buttons">
            <button
              type="button"
              className={displayMode === "list" ? "" : "secondary"}
              onClick={() => setDisplayMode("list")}
            >
              リスト表示
            </button>
            <button
              type="button"
              className={displayMode === "calendar" ? "" : "secondary"}
              onClick={() => setDisplayMode("calendar")}
            >
              カレンダー表示
            </button>
          </div>
        </div>

        {errorMessage && <p className="error">{errorMessage}</p>}
        {successMessage && <p className="success">{successMessage}</p>}

        <form onSubmit={handleSubmit} className="room-form">
          <h2>{selectedReservation ? "予約更新" : "予約登録"}</h2>

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
                onChange={(event) => setMeetingRoomId(Number(event.target.value))}
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
            <button type="submit">
              {selectedReservation ? "更新する" : "予約する"}
            </button>

            {selectedReservation && (
              <button type="button" className="secondary" onClick={resetForm}>
                キャンセル
              </button>
            )}
          </div>
        </form>

        {displayMode === "list" && (
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
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {reservations.map((reservation) => (
                <tr key={reservation.id}>
                  <td>{reservation.id}</td>
                  <td>{reservation.title}</td>
                  <td>{getUserName(reservation.user_id)}</td>
                  <td>{getMeetingRoomName(reservation.meeting_room_id)}</td>
                  <td>{formatDateTime(reservation.start_at)}</td>
                  <td>{formatDateTime(reservation.end_at)}</td>
                  <td>{reservation.is_active ? "有効" : "無効"}</td>
                  <td>
                    <div className="table-actions">
                      {canUpdateReservation(reservation) && (
                        <button
                          type="button"
                          className="secondary"
                          onClick={() => handleEditReservation(reservation)}
                        >
                          編集
                        </button>
                      )}

                      {canDeactivateReservation(reservation) ? (
                        <button
                          type="button"
                          className="danger"
                          onClick={() => handleDeactivateReservation(reservation.id)}
                        >
                          無効化
                        </button>
                      ) : (
                        <span className="muted-text">操作不可</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {displayMode === "calendar" && (
          <div className="calendar-section">
            <div className="calendar-header">
              <button type="button" className="secondary" onClick={handlePreviousMonth}>
                前月
              </button>

              <h2>
                {calendarMonth.getFullYear()}年 {calendarMonth.getMonth() + 1}月
              </h2>

              <button type="button" className="secondary" onClick={handleNextMonth}>
                次月
              </button>
            </div>

            <div className="calendar-week-row">
              <div>日</div>
              <div>月</div>
              <div>火</div>
              <div>水</div>
              <div>木</div>
              <div>金</div>
              <div>土</div>
            </div>

            <div className="calendar-grid">
              {calendarDays.map((date, index) => {
                if (!date) {
                  return <div key={`empty-${index}`} className="calendar-day empty" />;
                }

                const dailyReservations = getReservationsByDate(date);

                return (
                  <div key={formatDateKey(date)} className="calendar-day">
                    <div className="calendar-day-number">{date.getDate()}</div>

                    <div className="calendar-reservations">
                      {dailyReservations.map((reservation) => (
                        <div key={reservation.id} className="calendar-reservation-card">
                          <strong>{reservation.title}</strong>
                          <span>
                            {reservation.start_at.slice(11, 16)} -{" "}
                            {reservation.end_at.slice(11, 16)}
                          </span>
                          <span>{getMeetingRoomName(reservation.meeting_room_id)}</span>

                          <div className="calendar-card-actions">
                            {canUpdateReservation(reservation) && (
                              <button
                                type="button"
                                className="calendar-secondary-button"
                                onClick={() => handleEditReservation(reservation)}
                              >
                                編集
                              </button>
                            )}

                            {canDeactivateReservation(reservation) && (
                              <button
                                type="button"
                                className="calendar-danger-button"
                                onClick={() => handleDeactivateReservation(reservation.id)}
                              >
                                無効化
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};