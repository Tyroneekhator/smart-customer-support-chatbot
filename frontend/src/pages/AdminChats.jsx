import { useEffect, useState } from "react";
import { deleteChatHistory, getChatHistory, getRecentChatSessions } from "../services/api";

function formatDate(value) {
  if (!value) {
    return "Not available";
  }

  return new Date(value).toLocaleString();
}

function AdminChats() {
  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadSessions() {
    setIsLoadingSessions(true);
    setError("");

    try {
      const data = await getRecentChatSessions();
      setSessions(data);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsLoadingSessions(false);
    }
  }

  async function loadHistory(sessionId) {
    setSelectedSessionId(sessionId);
    setIsLoadingMessages(true);
    setError("");
    setSuccess("");

    try {
      const data = await getChatHistory(sessionId);
      setMessages(data);
    } catch (caughtError) {
      setError(caughtError.message);
      setMessages([]);
    } finally {
      setIsLoadingMessages(false);
    }
  }

  async function handleDeleteSession() {
    if (!selectedSessionId) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await deleteChatHistory(selectedSessionId);
      setMessages([]);
      setSelectedSessionId("");
      setSessions((currentSessions) =>
        currentSessions.filter((session) => session.session_id !== selectedSessionId),
      );
      setSuccess("Chat history deleted successfully.");
    } catch (caughtError) {
      setError(caughtError.message);
    }
  }

  useEffect(() => {
    let shouldIgnore = false;

    async function loadInitialSessions() {
      try {
        const data = await getRecentChatSessions();

        if (!shouldIgnore) {
          setSessions(data);
        }
      } catch (caughtError) {
        if (!shouldIgnore) {
          setError(caughtError.message);
        }
      } finally {
        if (!shouldIgnore) {
          setIsLoadingSessions(false);
        }
      }
    }

    loadInitialSessions();

    return () => {
      shouldIgnore = true;
    };
  }, []);

  return (
    <main className="admin-page">
      <section className="admin-header">
        <div>
          <p className="eyebrow">Admin Area</p>
          <h1>Chat Sessions</h1>
          <p>Review recent chatbot conversations and delete history when needed.</p>
        </div>

        <div className="admin-actions">
          <button type="button" onClick={loadSessions}>
            Refresh Sessions
          </button>
        </div>
      </section>

      {error && <p className="error-text wide-message">{error}</p>}
      {success && <p className="success-text wide-message">{success}</p>}

      <section className="admin-grid-two chat-admin-grid">
        <article className="admin-panel">
          <h2>Recent Sessions</h2>

          {isLoadingSessions ? (
            <p className="status-message">Loading sessions...</p>
          ) : sessions.length === 0 ? (
            <p className="muted-text">No chat sessions yet.</p>
          ) : (
            <div className="session-list">
              {sessions.map((session) => (
                <button
                  key={session.session_id}
                  type="button"
                  className={
                    selectedSessionId === session.session_id
                      ? "session-card active-session-card"
                      : "session-card"
                  }
                  onClick={() => loadHistory(session.session_id)}
                >
                  <strong>{session.session_id}</strong>
                  <span>{session.total_messages} messages</span>
                  <p>{session.last_message}</p>
                  <small>{formatDate(session.last_message_time)}</small>
                </button>
              ))}
            </div>
          )}
        </article>

        <article className="admin-panel">
          <div className="panel-title-row">
            <h2>Conversation History</h2>
            {selectedSessionId && (
              <button type="button" className="danger-button" onClick={handleDeleteSession}>
                Delete History
              </button>
            )}
          </div>

          {!selectedSessionId ? (
            <p className="muted-text">Select a chat session to view its messages.</p>
          ) : isLoadingMessages ? (
            <p className="status-message">Loading messages...</p>
          ) : messages.length === 0 ? (
            <p className="muted-text">No messages found for this session.</p>
          ) : (
            <div className="history-list">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={
                    message.sender === "user"
                      ? "history-message history-user"
                      : "history-message history-bot"
                  }
                >
                  <div>
                    <strong>{message.sender}</strong>
                    {message.intent && <span>{message.intent}</span>}
                  </div>
                  <p>{message.message}</p>
                  <small>{formatDate(message.created_at)}</small>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </main>
  );
}

export default AdminChats;
