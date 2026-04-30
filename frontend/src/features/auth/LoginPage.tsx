import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchCurrentUser, login } from "../../api/authApi";

/**
 * ログイン画面コンポーネント。
 *
 * メールアドレスとパスワードを入力し、ログイン成功時に
 * アクセストークンをlocalStorageへ保存して会議室一覧画面へ遷移する。
 */
export const LoginPage = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("password");
  const [errorMessage, setErrorMessage] = useState("");

  /**
   * ログインフォーム送信時の処理。
   *
   * ログインAPIを実行し、成功した場合はアクセストークンを保存して
   * ログイン中ユーザー情報を取得する。
   *
   * @param event フォーム送信イベント
   */
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage("");

    try {
      const token = await login({
        email,
        password,
      });

      localStorage.setItem("accessToken", token.access_token);

      await fetchCurrentUser();

      navigate("/meeting-rooms");
    } catch {
      setErrorMessage("メールアドレスまたはパスワードが正しくありません。");
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h1>Reservation Manager</h1>
        <p className="description">会議室予約管理システム</p>

        <form onSubmit={handleSubmit} className="form">
          <label>
            メールアドレス
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <label>
            パスワード
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {errorMessage && <p className="error">{errorMessage}</p>}

          <button type="submit">ログイン</button>
        </form>
      </div>
    </div>
  );
};