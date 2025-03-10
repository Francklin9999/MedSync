import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../scss/Chatbot.scss";
import Scene from "../Scene.jsx";
import axios from "axios";
import { Leva } from "leva";

const ChatbotFullScreen: React.FC = () => {
  const navigate = useNavigate();

  const inputRef = useRef<HTMLInputElement>(null);

  const [sceneData, setSceneData] = useState<any>(null);

  const closeChat = () => {
    // Navigate back to home (or your desired route)
    navigate("/home");
  };

  const handleSubmit = async () => {
    const inputValue = inputRef.current?.value;
    if (inputValue) {
      const data = await sendQuery(inputValue); 
      setSceneData(data); 
    }
  };

  async function sendQuery<T>(data: any): Promise<T> {
    const url = "http://127.0.0.1:5000/query_db";
    const response = await axios.post<T>(url, {
        query: data
    }, {
        headers: {
            'Content-Type': 'application/json',
        }
    });
    console.log(response.data);
    return response.data;
  }


  return (
    <div className="chatbot-fullscreen">
      <div className="chatbot-header">
        <button className="chatbot-close" onClick={closeChat}>
          ×
        </button>
          <h2 className={"chatbot-title"}>
              MediSync Virtual Assistant
          </h2>
      </div>
      <div className="chatbot-message">{sceneData?.message?.text}</div>
      <div className="chatbot-content">
        <Leva />
        <Scene data={sceneData} />
      </div>
      <div className="chatbot-messager">
        <input type="text" placeholder="Type a message..." ref={inputRef} />
          <button onClick={handleSubmit}>Send</button>
    </div>
    </div>
  );
};

export default ChatbotFullScreen;
