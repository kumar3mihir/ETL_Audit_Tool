// /src/components/ResultPage/RightSide/ChatBox.tsx

import { useState } from "react";

interface Message {
  text: string;
  sender: "user" | "bot";
}

const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { text: "Hello! How can I assist you?", sender: "bot" },
  ]);
  const [input, setInput] = useState<string>("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to UI
    const userMessage: Message = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);

    // Clear input field
    setInput("");

    // Send to AI API (dummy response for now)
    const botResponse = await fetchBotResponse(input);
    setMessages((prev) => [...prev, { text: botResponse, sender: "bot" }]);
  };

  const fetchBotResponse = async (userInput: string): Promise<string> => {
    // Replace with actual AI API call (Hugging Face / OpenRouter)
    return new Promise((resolve) => {
      setTimeout(() => resolve("This is a placeholder response!"), 1000);
    });
  };

  return (
    <div className="w-full max-w-md p-4 bg-white rounded-lg shadow-md">
      {/* Chat Messages */}
      <div className="h-64 overflow-y-auto p-2 border border-gray-300 rounded">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 text-${msg.sender === "user" ? "right text-blue-600" : "left text-gray-700"}`}>
            <p className={`p-2 rounded-lg ${msg.sender === "user" ? "bg-blue-100" : "bg-gray-200"}`}>
              {msg.text}
            </p>
          </div>
        ))}
      </div>

      {/* Input Box */}
      <div className="mt-2 flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="w-full p-2 border rounded-l-md"
        />
        <button onClick={sendMessage} className="bg-blue-500 text-white p-2 rounded-r-md">
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;

