import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchCurrentUser } from "../../api/authApi";
import { fetchMeetingRooms } from "../../api/meetingRoomApi";
import { MeetingRoomListPage } from "./MeetingRoomListPage";

vi.mock("../../api/authApi", () => ({
  fetchCurrentUser: vi.fn(),
}));

vi.mock("../../api/meetingRoomApi", () => ({
  fetchMeetingRooms: vi.fn(),
  createMeetingRoom: vi.fn(),
  updateMeetingRoom: vi.fn(),
  deactivateMeetingRoom: vi.fn(),
}));

const mockedFetchCurrentUser = vi.mocked(fetchCurrentUser);
const mockedFetchMeetingRooms = vi.mocked(fetchMeetingRooms);

describe("MeetingRoomListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("会議室一覧でAPI結果が表示される", async () => {
    mockedFetchCurrentUser.mockResolvedValue({
      id: 1,
      name: "Admin User",
      email: "admin@example.com",
      role: "admin",
      is_active: true,
    });

    mockedFetchMeetingRooms.mockResolvedValue([
      {
        id: 1,
        name: "大会議室",
        capacity: 12,
        location: "5F",
        is_active: true,
      },
      {
        id: 2,
        name: "小会議室",
        capacity: 4,
        location: "3F",
        is_active: true,
      },
    ]);

    render(<MeetingRoomListPage />);

    expect(await screen.findByText("大会議室")).toBeInTheDocument();
    expect(screen.getByText("小会議室")).toBeInTheDocument();
    expect(screen.getByText("5F")).toBeInTheDocument();
    expect(screen.getByText("3F")).toBeInTheDocument();
  });
});