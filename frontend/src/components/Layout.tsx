import { Link, Outlet, useNavigate } from "react-router-dom";

/**
 * アプリ全体の共通レイアウトコンポーネント。
 *
 * ヘッダー、ナビゲーション、ログアウトボタン、各ページの表示領域を提供する。
 */
export const Layout = () => {
  const navigate = useNavigate();

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
          <button type="button" onClick={handleLogout}>
            ログアウト
          </button>
        </nav>
      </header>

      <Outlet />
    </>
  );
};