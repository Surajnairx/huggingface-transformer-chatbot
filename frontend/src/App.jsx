import { useState, useEffect, useRef } from "react";
import axios from "axios";

const API = "http://localhost:8000";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [pdfs, setPdfs] = useState([]);
  const chatEndRef = useRef(null);

  const documentReady = pdfs.length > 0;

  useEffect(() => {
    fetchPdfs();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, loading]);

  const fetchPdfs = async () => {
    try {
      const res = await axios.get(`${API}/list-pdfs`);
      setPdfs(res.data.pdfs);
    } catch {
      // backend not ready yet
    }
  };

  const uploadPDF = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      setLoading(true);
      const res = await axios.post(`${API}/upload-pdf`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setChat((prev) => [...prev, { sender: "bot", text: res.data.message }]);
      setFile(null);
      await fetchPdfs();
    } catch {
      alert("PDF upload failed");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || !documentReady) return;
    const userMessage = message;
    setChat((prev) => [...prev, { sender: "user", text: userMessage }]);
    setMessage("");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/ask-document`, {
        question: userMessage,
      });
      const { answer, similarity_scores, sources } = res.data;
      setChat((prev) => [
        ...prev,
        {
          sender: "bot",
          text: answer,
          score: similarity_scores?.[0],
          source: sources?.[0],
        },
      ]);
    } catch {
      setChat((prev) => [
        ...prev,
        { sender: "bot", text: "Error generating response." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-[#071014] text-cyan-100 flex flex-col overflow-hidden">
      {/* Header */}
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
        {/* Sidebar */}
        <aside className="w-75 border-r border-cyan-500/20 bg-[#0b161b] flex flex-col">
          {/* Upload section */}
          <div className="p-5 border-b border-cyan-500/20">
            <h2 className="text-base font-semibold text-cyan-200 mb-3">
              Upload PDF
            </h2>
            <label className="border border-dashed border-cyan-500/40 rounded-xl p-5 text-center cursor-pointer hover:bg-cyan-500/5 transition flex flex-col items-center gap-2">
              <input
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(e) => setFile(e.target.files[0])}
              />
              <span className="text-3xl">📄</span>
              <span className="text-xs text-cyan-400 truncate max-w-full px-2">
                {file ? file.name : "Choose PDF file"}
              </span>
            </label>
            <button
              onClick={uploadPDF}
              disabled={loading || !file}
              className="mt-3 w-full bg-cyan-500 text-black font-semibold py-2.5 rounded-xl hover:bg-cyan-400 transition disabled:opacity-40 text-sm"
            >
              {loading ? "Processing..." : "Upload PDF"}
            </button>
          </div>

          {/* Indexed PDFs list */}
          <div className="flex-1 overflow-y-auto p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-cyan-200">
                Indexed PDFs
              </h2>
              <span className="text-xs bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full">
                {pdfs.length}
              </span>
            </div>

            {pdfs.length === 0 ? (
              <p className="text-xs text-cyan-700 text-center mt-6">
                No PDFs indexed yet.
              </p>
            ) : (
              <ul className="space-y-2">
                {pdfs.map((name) => (
                  <li
                    key={name}
                    className="flex items-center gap-3 bg-[#071014] border border-cyan-500/15 rounded-xl px-3 py-2.5"
                  >
                    <span className="text-lg shrink-0">📄</span>
                    <span className="text-xs text-cyan-300 truncate">
                      {name}
                    </span>
                    <span className="ml-auto shrink-0 h-1.5 w-1.5 rounded-full bg-green-400" />
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Status */}
          <div className="p-5 border-t border-cyan-500/20">
            <p className="text-xs text-cyan-600">STATUS</p>
            <p className="mt-1 text-sm font-medium">
              {documentReady ? (
                <span className="text-green-400">
                  Ready — {pdfs.length} PDF{pdfs.length > 1 ? "s" : ""} loaded
                </span>
              ) : (
                <span className="text-yellow-400">Waiting for upload</span>
              )}
            </p>
          </div>
        </aside>

        {/* Chat */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-8 space-y-4">
            {chat.length === 0 && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="text-7xl mb-5">🤖</div>
                  <h2 className="text-2xl font-semibold text-cyan-200">
                    AI Document Assistant
                  </h2>
                  <p className="text-cyan-500 mt-2">
                    {documentReady
                      ? "Your PDFs are loaded. Ask anything."
                      : "Upload a PDF to get started."}
                  </p>
                </div>
              </div>
            )}

            {chat.map((msg, i) => (
              <div
                key={i}
                className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className={`max-w-[75%] px-5 py-4 rounded-2xl leading-relaxed text-sm ${
                    msg.sender === "user"
                      ? "bg-cyan-500 text-black"
                      : "bg-[#0b161b] border border-cyan-500/20 text-cyan-100"
                  }`}
                >
                  {msg.text}
                </div>
                {msg.sender === "bot" && msg.source && (
                  <p className="text-[11px] text-cyan-700 mt-1 px-1">
                    {msg.source} &nbsp;·&nbsp; similarity{" "}
                    {(msg.score * 100).toFixed(1)}%
                  </p>
                )}
              </div>
            ))}

            {loading && (
              <div className="bg-[#0b161b] border border-cyan-500/20 text-cyan-300 px-5 py-4 rounded-2xl max-w-[75%] text-sm">
                Thinking...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-cyan-500/20 p-5 bg-[#0b161b]">
            <div className="flex gap-3">
              <input
                type="text"
                placeholder={
                  documentReady
                    ? "Ask questions from your PDFs..."
                    : "Upload a PDF first..."
                }
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" && !loading && sendMessage()
                }
                disabled={loading || !documentReady}
                className="flex-1 bg-[#071014] border border-cyan-500/20 rounded-xl px-5 py-4 outline-none focus:border-cyan-400 text-cyan-100 placeholder:text-cyan-700 text-sm"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !documentReady}
                className="bg-cyan-500 text-black font-semibold px-7 rounded-xl hover:bg-cyan-400 transition disabled:opacity-40 text-sm"
              >
                {loading ? "..." : "Send"}
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
