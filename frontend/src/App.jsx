import { useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [documentReady, setDocumentReady] = useState(false);

  const sendMessage = async () => {
    if (!message.trim()) return;

    if (!documentReady) {
      alert("Please upload a PDF first.");
      return;
    }

    const userMessage = message;

    setChat((prev) => [...prev, { sender: "user", text: userMessage }]);
    setMessage("");
    setLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/ask-document", {
        question: userMessage,
      });

      setChat((prev) => [
        ...prev,
        { sender: "bot", text: response.data.answer },
      ]);
    } catch (error) {
      console.error(error);
      setChat((prev) => [
        ...prev,
        { sender: "bot", text: "Error generating document-based response" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const uploadPDF = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setDocumentReady(false);

      const response = await axios.post(
        "http://localhost:8000/upload-pdf",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        },
      );

      setDocumentReady(true);
      setChat([
        {
          sender: "bot",
          text: `${response.data.message}. You can now ask questions from this PDF.`,
        },
      ]);
    } catch (error) {
      console.error(error);
      alert("PDF upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !loading) {
      sendMessage();
    }
  };

  return (
    <div className="h-screen w-screen bg-[#071014] text-cyan-100 flex flex-col overflow-hidden">
      <header className="border-b border-cyan-500/20 px-8 py-5 flex items-center justify-between bg-[#0b161b]">
        <div>
          <h1 className="text-3xl font-bold tracking-wide text-cyan-300">
            AI PDF Document Analyzer
          </h1>

          <p className="text-cyan-500 text-sm mt-1">
            Retrieval-Augmented Generation using Hugging Face Transformers
          </p>
        </div>

        <div className="h-3 w-3 rounded-full bg-cyan-400 shadow-[0_0_18px_#22d3ee]" />
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-[320px] border-r border-cyan-500/20 bg-[#0b161b] p-6 flex flex-col">
          <h2 className="text-xl font-semibold text-cyan-200 mb-5">
            Upload PDF
          </h2>

          <label className="border border-dashed border-cyan-500/40 rounded-xl p-8 text-center cursor-pointer hover:bg-cyan-500/5 transition">
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={(e) => {
                setFile(e.target.files[0]);
                setDocumentReady(false);
                setChat([]);
              }}
            />

            <div className="text-5xl mb-3">📄</div>

            <p className="text-sm text-cyan-300">
              {file ? file.name : "Choose PDF File"}
            </p>
          </label>

          <button
            onClick={uploadPDF}
            disabled={loading || !file}
            className="mt-5 bg-cyan-500 text-black font-semibold py-3 rounded-xl hover:bg-cyan-400 transition disabled:opacity-50"
          >
            {loading ? "Processing..." : "Upload PDF"}
          </button>

          <div className="mt-6 border border-cyan-500/20 rounded-xl p-4 bg-[#071014]">
            <p className="text-sm text-cyan-500">STATUS</p>

            <p className="mt-2 font-medium">
              {documentReady ? (
                <span className="text-green-400">PDF Ready</span>
              ) : (
                <span className="text-yellow-400">Waiting for upload</span>
              )}
            </p>
          </div>
        </aside>

        <main className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-8 space-y-5">
            {chat.length === 0 && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="text-7xl mb-5">🤖</div>

                  <h2 className="text-2xl font-semibold text-cyan-200">
                    AI Document Assistant
                  </h2>

                  <p className="text-cyan-500 mt-2">
                    Upload a PDF and start asking questions.
                  </p>
                </div>
              </div>
            )}

            {chat.map((msg, index) => (
              <div
                key={index}
                className={`max-w-[75%] px-5 py-4 rounded-2xl leading-relaxed ${
                  msg.sender === "user"
                    ? "ml-auto bg-cyan-500 text-black"
                    : "bg-[#0b161b] border border-cyan-500/20 text-cyan-100"
                }`}
              >
                {msg.text}
              </div>
            ))}

            {loading && (
              <div className="bg-[#0b161b] border border-cyan-500/20 text-cyan-300 px-5 py-4 rounded-2xl max-w-[75%]">
                Thinking...
              </div>
            )}
          </div>

          <div className="border-t border-cyan-500/20 p-6 bg-[#0b161b]">
            <div className="flex gap-4">
              <input
                type="text"
                placeholder={
                  documentReady
                    ? "Ask questions from your PDF..."
                    : "Upload a PDF first..."
                }
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading || !documentReady}
                className="flex-1 bg-[#071014] border border-cyan-500/20 rounded-xl px-5 py-4 outline-none focus:border-cyan-400 text-cyan-100 placeholder:text-cyan-700"
              />

              <button
                onClick={sendMessage}
                disabled={loading || !documentReady}
                className="bg-cyan-500 text-black font-semibold px-8 rounded-xl hover:bg-cyan-400 transition disabled:opacity-50"
              >
                {loading ? "Sending..." : "Send"}
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
