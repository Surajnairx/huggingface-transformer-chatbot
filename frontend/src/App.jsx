import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message;

    setChat((prev) => [...prev, { sender: "user", text: userMessage }]);

    setMessage("");
    setLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/chat", {
        message: userMessage,
      });

      setChat((prev) => [
        ...prev,
        {
          sender: "bot",
          text: response.data.response,
        },
      ]);
    } catch (error) {
      console.error(error);

      setChat((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Error generating response",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <h1>Hugging Face Transformer Chatbot</h1>

      <div className="chat-container">
        {chat.map((msg, index) => (
          <div
            key={index}
            className={msg.sender === "user" ? "message user" : "message bot"}
          >
            {msg.text}
          </div>
        ))}

        {loading && <div className="message bot">Typing...</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />

        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
