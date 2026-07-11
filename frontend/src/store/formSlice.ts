import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface FormState {
  hcp_name: string;
  interaction_type: string;
  date: string;
  time: string;
  attendees: string;
  topics_discussed: string;
  sentiment: string;
  materials_shared: string[];
  summary: string;
}

const today = new Date();
const yyyy = today.getFullYear();
const mm = String(today.getMonth() + 1).padStart(2, '0');
const dd = String(today.getDate()).padStart(2, '0');

const hours = today.getHours();
const minutes = String(today.getMinutes()).padStart(2, '0');
const ampm = hours >= 12 ? 'PM' : 'AM';
const h12 = String(hours % 12 || 12).padStart(2, '0');

const initialState: FormState = {
  hcp_name: '',
  interaction_type: 'Meeting',
  date: `${yyyy}-${mm}-${dd}`,
  time: `${h12}:${minutes} ${ampm}`,
  attendees: '',
  topics_discussed: '',
  sentiment: '',
  materials_shared: [],
  summary: '',
};

const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    // Apply partial updates from the AI (only updates specified fields)
    applyFormUpdates(state, action: PayloadAction<Partial<FormState>>) {
      const updates = action.payload;
      if (updates.hcp_name !== undefined && updates.hcp_name !== '') state.hcp_name = updates.hcp_name;
      if (updates.interaction_type !== undefined && updates.interaction_type !== '') state.interaction_type = updates.interaction_type;
      if (updates.date !== undefined && updates.date !== '') state.date = updates.date;
      if (updates.time !== undefined && updates.time !== '') state.time = updates.time;
      if (updates.attendees !== undefined && updates.attendees !== '') state.attendees = updates.attendees;
      if (updates.topics_discussed !== undefined && updates.topics_discussed !== '') state.topics_discussed = updates.topics_discussed;
      if (updates.sentiment !== undefined && updates.sentiment !== '') state.sentiment = updates.sentiment;
      if (updates.materials_shared !== undefined && updates.materials_shared.length > 0) state.materials_shared = updates.materials_shared;
      if (updates.summary !== undefined && updates.summary !== '') state.summary = updates.summary;
    },
    // Reset the form
    resetForm() {
      return initialState;
    },
  },
});

export const { applyFormUpdates, resetForm } = formSlice.actions;
export default formSlice.reducer;
