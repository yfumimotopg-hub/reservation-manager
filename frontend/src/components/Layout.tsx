import { useEffect, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";

import { fetchCurrentUser } from "../api/authApi";
import type { CurrentUser } from "../types/auth";

/**
 * アプリ全体の共通レイアウトコンポーネント。
 *
 * ヘッダー、ナビゲーション、ログアウトボタン、各ページの表示領域を提供する。
 * ログイン中ユーザーの権限に応じて、管理者向けメニューを出し分ける。
 */
export const Layout = () => {
  const navigate = useNavigate();

  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);

  /**
   * ログイン中ユーザー情報を取得し、ナビゲーションの表示制御に使用する。
   */
  const loadCurrentUser = async () => {
    try {
      const user = await fetchCurrentUser();
      setCurrentUser(user);
    } catch {
      localStorage.removeItem("accessToken");
      navigate("/");
    }
  };

  useEffect(() => {
    loadCurrentUser();
  }, []);

  /**
   * ログアウト処理。
   *
   * localStorageからアクセストークンを削除し、ログイン画面へ遷移する。
   */
  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    navigate("/");
  };

  return (
    <>
      <header className="header">
        <Link to="/meeting-rooms" className="logo">
          Reservation Manager
        </Link>

        <nav className="nav">
          <Link to="/meeting-rooms">会議室一覧</Link>
          <Link to="/reservations">予約一覧</Link>

          {currentUser?.role === "admin" && (
            <Link to="/users">ユーザー管理</Link>
          )}

          <button type="button" onClick={handleLogout}>
            ログアウト
          </button>
        </nav>
      </header>

      <Outlet />
    </>
  );
};