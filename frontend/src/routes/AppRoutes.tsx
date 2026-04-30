import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { LoginPage } from "../features/auth/LoginPage";
import { MeetingRoomListPage } from "../features/meetingRooms/MeetingRoomListPage";
import { ReservationListPage } from "../features/reservations/ReservationListPage";
import { UserManagementPage } from "../features/users/UserManagementPage";

/**
 * アプリケーションのルーティングを定義するコンポーネント。
 *
 * ログイン画面、認証後の共通レイアウト、
 * 会議室一覧画面、予約一覧画面、ユーザー管理画面へのルートを管理する。
 */
export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />

      <Route element={<Layout />}>
        <Route path="/meeting-rooms" element={<MeetingRoomListPage />} />
        <Route path="/reservations" element={<ReservationListPage />} />
        <Route path="/users" element={<UserManagementPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};