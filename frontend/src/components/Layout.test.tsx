import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fetchCurrentUser } from "../api/authApi";
import { Layout } from "./Layout";

vi.mock("../api/authApi", () => ({
  fetchCurrentUser: vi.fn(),
}));

const mockedFetchCurrentUser = vi.mocked(fetchCurrentUser);

/**
 * LayoutをReact Router配下で描画する。
 */
const renderLayout = () => {
  render(
    <MemoryRouter initialEntries={["/meeting-rooms"]}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/meeting-rooms" element={<div>会議室ページ</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
};

describe("Layout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("adminの場合、ユーザー管理リンクが表示される", async () => {
    mockedFetchCurrentUser.mockResolvedValue({
      id: 1,
      name: "Admin User",
      email: "admin@example.com",
      role: "admin",
      is_active: true,
    });

    renderLayout();

    expect(await screen.findByText("会議室ページ")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole("link", { name: "ユーザー管理" })).toBeInTheDocument();
    });
  });

  it("userの場合、ユーザー管理リンクが表示されない", async () => {
    mockedFetchCurrentUser.mockResolvedValue({
      id: 2,
      name: "General User",
      email: "user@example.com",
      role: "user",
      is_active: true,
    });

    renderLayout();

    expect(await screen.findByText("会議室ページ")).toBeInTheDocument();

    await waitFor(() => {
      expect(mockedFetchCurrentUser).toHaveBeenCalled();
    });

    expect(screen.queryByRole("link", { name: "ユーザー管理" })).not.toBeInTheDocument();
  });
});