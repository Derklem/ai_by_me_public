import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Mic, Send } from "lucide-react";

export default function AiByMeInterface() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [listening, setListening] = useState(false);
  
  useEffect(() => {
    if (!listening) return;
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.start();
    
    recognition.onresult = (event) => {
      setInput(event.results[0][0].transcript);
    };

    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);
  }, [listening]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { text: input, sender: "user" }];
    setMessages(newMessages);

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();
      setMessages([...newMessages, { text: data.response, sender: "ai" }]);
    } catch (error) {
      console.error("Error connecting to AI:", error);
    }

    setInput("");
  };

  return (
    <div className="flex flex-col items-center w-full h-full p-4 bg-black text-white">
      <Card className="w-full max-w-lg p-4 border border-gray-700">
        <CardContent>
          <div className="flex flex-col gap-2">
            <div className="overflow-y-auto h-64 border-b border-gray-600 pb-2">
              {messages.map((msg, idx) => (
                <div key={idx} className={`text-${msg.sender === "user" ? "right" : "left"} p-2`}>
                  {msg.text}
                </div>
              ))}
            </div>
            <div className="flex gap-2 items-center">
              <Input 
                className="flex-grow bg-gray-800 text-white" 
                placeholder="Type or speak..." 
                value={input} 
                onChange={(e) => setInput(e.target.value)} 
              />
              <Button onClick={() => setListening(true)}>
                <Mic size={20} />
              </Button>
              <Button onClick={sendMessage}>
                <Send size={20} />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
