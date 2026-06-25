import MessageBubble from "./MessageBubble";

function ChatWindow({ messages, isLoading }) {
  return (
    <div className="chat-window">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="message-row bot-row">
          <div className="message-bubble bot-bubble">
            <p>CookieBot is typing...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatWindow;
