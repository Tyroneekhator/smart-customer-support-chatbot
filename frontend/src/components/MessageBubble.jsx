function MessageBubble({ message }) {
  const isUser = message.sender === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "bot-row"}`}>
      <div
        className={`message-bubble ${isUser ? "user-bubble" : "bot-bubble"}`}
      >
        <p>{message.text}</p>

        {message.intent && !isUser && (
          <span className="intent-label">Intent: {message.intent}</span>
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
