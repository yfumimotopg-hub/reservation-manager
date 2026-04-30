export type MeetingRoom = {
  id: number;
  name: string;
  capacity: number;
  location: string;
  is_active: boolean;
};

export type MeetingRoomCreateRequest = {
  name: string;
  capacity: number;
  location: string;
};

export type MeetingRoomUpdateRequest = {
  name: string;
  capacity: number;
  location: string;
  is_active: boolean;
};