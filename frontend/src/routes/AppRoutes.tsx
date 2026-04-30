import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { LoginPage } from "../features/auth/LoginPage";
import { MeetingRoomListPage } from "../features/meetingRooms/MeetingRoomListPage";

/**
 * アプリケーションのルーティングを定義するコンポーネント。
 *
 * ログイン画面、認証後の共通レイアウト、会議室一覧画面へのルートを管理する。
 */
export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />

      <Route element={<Layout />}>
        <Route path="/meeting-rooms" element={<MeetingRoomListPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};