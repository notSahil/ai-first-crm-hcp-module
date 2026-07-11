import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage(state, action: PayloadAction<Omit<Message, 'id' | 'timestamp'>>) {
      state.messages.push({
        ...action.payload,
        id: `${Date.now()}-${Math.random()}`,
        timestamp: new Date().toISOString(),
      });
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
    clearChat(state) {
      state.messages = [];
      state.error = null;
    },
  },
});

export const { addMessage, setLoading, setError, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
