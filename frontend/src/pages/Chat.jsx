import { useState } from "react";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import { sendChatMessage } from "../services/api";

function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      text: "Hello! Welcome to CookieBot. Ask me about our menu, prices, opening hours, delivery, or orders.",
      intent: "greeting",
    },
  ]);

  const [sessionId, setSessionId] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSendMessage(userMessage) {
    const userChatMessage = {
      id: Date.now(),
      sender: "user",
      text: userMessage,
    };

    setMessages((previousMessages) => [...previousMessages, userChatMessage]);
    setIsLoading(true);

    try {
      const data = await sendChatMessage(userMessage, sessionId);

      if (!sessionId) {
        setSessionId(data.session_id);
      }

      const botMessage = {
        id: Date.now() + 1,
        sender: "bot",
        text: data.reply,
        intent: data.intent,
      };

      setMessages((previousMessages) => [...previousMessages, botMessage]);
    } catch {
      const errorMessage = {
        id: Date.now() + 2,
        sender: "bot",
        text: "Sorry, I could not connect to the backend. Please make sure the FastAPI server is running.",
        intent: "error",
      };

      setMessages((previousMessages) => [...previousMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  function clearChat() {
    setMessages([
      {
        id: 1,
        sender: "bot",
        text: "Chat cleared. How can I help you today?",
        intent: "greeting",
      },
    ]);

    setSessionId("");
  }

  return (
    <main className="chat-page">
      <section className="chat-container">
        <div className="chat-header">
          <div>
            <p className="eyebrow">Live Chat</p>
            <h1>CookieBot Assistant</h1>
          </div>

          <button className="clear-button" onClick={clearChat}>
            Clear Chat
          </button>
        </div>

        <ChatWindow messages={messages} isLoading={isLoading} />

        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />

        {sessionId && (
          <p className="session-text">
            Session ID: <span>{sessionId}</span>
          </p>
        )}
      </section>
    </main>
  );
}

export default Chat;
