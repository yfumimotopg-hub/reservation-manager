import { FormEvent, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { fetchCurrentUser } from "../../api/authApi";
import { createUser, deactivateUser, fetchUsers, updateUser } from "../../api/userApi";
import type { CurrentUser } from "../../types/auth";
import type { User } from "../../types/user";

/**
 * ユーザー管理画面コンポーネント。
 *
 * 管理者ユーザーがユーザー一覧の確認、登録、更新、無効化を行うための画面。
 */
export const UserManagementPage = () => {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"admin" | "user">("user");
  const [isActive, setIsActive] = useState(true);

  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const isAdmin = currentUser?.role === "admin";

  /**
   * 画面表示に必要なログイン中ユーザー情報とユーザー一覧を取得する。
   */
  const loadInitialData = async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const user = await fetchCurrentUser();
      setCurrentUser(user);

      if (user.role === "admin") {
        const userData = await fetchUsers();
        setUsers(userData);
      }
    } catch {
      setErrorMessage("ユーザー情報の取得に失敗しました。");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * ユーザー一覧を再取得する。
   *
   * 登録・更新・無効化後に画面表示を最新化するために使用する。
   */
  const reloadUsers = async () => {
    const userData = await fetchUsers();
    setUsers(userData);
  };

  /**
   * 入力フォームを初期状態に戻す。
   */
  const resetForm = () => {
    setSelectedUser(null);
    setName("");
    setEmail("");
    setRole("user");
    setIsActive(true);
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  /**
   * ユーザー登録・更新フォーム送信時の処理。
   *
   * 選択中のユーザーがある場合は更新、ない場合は新規登録を行う。
   *
   * @param event フォーム送信イベント
   */
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    try {
      if (selectedUser) {
        await updateUser(selectedUser.id, {
          name,
          email,
          role,
          is_active: isActive,
        });

        setSuccessMessage("ユーザーを更新しました。");
      } else {
        await createUser({
          name,
          email,
          role,
        });

        setSuccessMessage("ユーザーを登録しました。");
      }

      resetForm();
      await reloadUsers();
    } catch {
      setErrorMessage("ユーザーの保存に失敗しました。メールアドレスが重複している可能性があります。");
    }
  };

  /**
   * 更新対象のユーザーをフォームに反映する。
   *
   * @param user 編集対象のユーザー
   */
  const handleEdit = (user: User) => {
    setSelectedUser(user);
    setName(user.name);
    setEmail(user.email);
    setRole(user.role);
    setIsActive(user.is_active);
    setErrorMessage("");
    setSuccessMessage("");
  };

  /**
   * ユーザーを無効化する。
   *
   * 対象ユーザーを物理削除せず、バックエンド側で is_active=false に更新する。
   *
   * @param userId 無効化対象のユーザーID
   */
  const handleDeactivate = async (userId: number) => {
    setErrorMessage("");
    setSuccessMessage("");

    const confirmed = window.confirm("このユーザーを無効化しますか？");

    if (!confirmed) {
      return;
    }

    try {
      await deactivateUser(userId);
      setSuccessMessage("ユーザーを無効化しました。");
      await reloadUsers();
    } catch {
      setErrorMessage("ユーザーの無効化に失敗しました。");
    }
  };

  if (isLoading) {
    return (
      <div className="page">
        <div className="wide-card">
          <p>読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return <Navigate to="/meeting-rooms" replace />;
  }

  return (
    <div className="page">
      <div className="wide-card">
        <div className="page-title-row">
          <div>
            <h1>ユーザー管理</h1>
            <p className="description">
              ログイン中: {currentUser?.name}（{currentUser?.role}）
            </p>
          </div>
        </div>

        {errorMessage && <p className="error">{errorMessage}</p>}
        {successMessage && <p className="success">{successMessage}</p>}

        <form onSubmit={handleSubmit} className="room-form">
          <h2>{selectedUser ? "ユーザー更新" : "ユーザー登録"}</h2>

          <div className="form-grid user-form-grid">
            <label>
              ユーザー名
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
              />
            </label>

            <label>
              メールアドレス
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </label>

            <label>
              権限
              <select
                value={role}
                onChange={(event) => setRole(event.target.value as "admin" | "user")}
                required
              >
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
            </label>

            {selectedUser && (
              <label>
                状態
                <select
                  value={isActive ? "active" : "inactive"}
                  onChange={(event) => setIsActive(event.target.value === "active")}
                  required
                >
                  <option value="active">有効</option>
                  <option value="inactive">無効</option>
                </select>
              </label>
            )}
          </div>

          <div className="button-row">
            <button type="submit">
              {selectedUser ? "更新する" : "登録する"}
            </button>

            {selectedUser && (
              <button type="button" className="secondary" onClick={resetForm}>
                キャンセル
              </button>
            )}
          </div>
        </form>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>ユーザー名</th>
              <th>メールアドレス</th>
              <th>権限</th>
              <th>状態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{user.is_active ? "有効" : "無効"}</td>
                <td>
                  <div className="table-actions">
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => handleEdit(user)}
                    >
                      編集
                    </button>

                    <button
                      type="button"
                      className="danger"
                      onClick={() => handleDeactivate(user.id)}
                      disabled={!user.is_active}
                    >
                      無効化
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};