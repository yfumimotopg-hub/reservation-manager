export type Reservation = {
  id: number;
  user_id: number;
  meeting_room_id: number;
  title: string;
  start_at: string;
  end_at: string;
  is_active: boolean;
};

export type ReservationCreateRequest = {
  user_id: number;
  meeting_room_id: number;
  title: string;
  start_at: string;
  end_at: string;
};

export type ReservationUpdateRequest = {
  user_id: number;
  meeting_room_id: number;
  title: string;
  start_at: string;
  end_at: string;
  is_active: boolean;
};