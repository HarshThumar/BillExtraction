'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const processInvoice = async () => {
    if (!file) return;
    setIsProcessing(true);
    setMessage('Extracting data with Docling engine...');
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Extraction failed');
      
      const data = await response.json();
      setExtractedData(data);
      setMessage('Extraction complete! Please review.');
    } catch (error) {
      console.error(error);
      setMessage('Error extracting data. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const saveToSheet = async () => {
    setIsSaving(true);
    setMessage('Saving to Google Sheet...');
    try {
      const response = await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(extractedData),
      });

      if (!response.ok) throw new Error('Save failed');
      
      setMessage('Data successfully saved to Google Sheet! ✨');
      // Reset after success
      setTimeout(() => {
        setExtractedData(null);
        setFile(null);
        setMessage('');
      }, 3000);
    } catch (error) {
      console.error(error);
      setMessage('Error saving to sheet. Check your credentials.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <main className="h-screen bg-[#0a0a0c] text-white font-[family-name:var(--font-geist-sans)] p-4 flex flex-col items-center justify-center overflow-hidden">
      <div className="w-full max-w-5xl space-y-4">
        {/* Header */}
        <header className="space-y-1 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent"
          >
            Bill Genius
          </motion.h1>
          <p className="text-zinc-500 text-xs">
            Fast invoice extraction with Docling AI.
          </p>
        </header>

        {/* Upload Section */}
        <section className="relative px-4">
          <div className="absolute inset-x-0 top-0 h-48 bg-blue-500/5 blur-[80px] rounded-full pointer-events-none" />
          
          <div className="relative bg-zinc-900/40 backdrop-blur-2xl border border-zinc-800/50 rounded-2xl p-6 shadow-2xl overflow-hidden">
            {!extractedData ? (
              <div className="space-y-4">
                <div className="flex flex-col items-center justify-center border border-dashed border-zinc-700/50 rounded-xl p-8 transition-colors hover:border-blue-500/30 group bg-zinc-950/30">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center space-y-2 text-center">
                    <div className="w-10 h-10 bg-blue-500/10 rounded-full flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="space-y-0.5">
                      <p className="text-sm font-medium">{file ? file.name : 'Choose a PDF invoice'}</p>
                      <p className="text-[10px] text-zinc-500">Drag and drop or click to browse</p>
                    </div>
                  </label>
                </div>

                <div className="flex justify-center">
                  <button
                    disabled={!file || isProcessing}
                    onClick={processInvoice}
                    className="px-8 py-2.5 bg-blue-600 rounded-lg font-bold text-xs hover:bg-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <span>Extract Details</span>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(extractedData).map(([key, value]: [string, any]) => (
                    <div key={key} className="space-y-0.5">
                      <label className="text-[9px] font-bold uppercase tracking-widest text-zinc-500 pl-0.5">{key.replace('_', ' ')}</label>
                      <input
                        type="text"
                        value={value || ''}
                        onChange={(e) => setExtractedData({ ...extractedData, [key]: e.target.value })}
                        className="w-full bg-zinc-950/50 border border-zinc-800 rounded px-2.5 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all text-zinc-200"
                      />
                    </div>
                  ))}
                </div>

                <div className="flex justify-between items-center pt-4 border-t border-zinc-800">
                  <button 
                    onClick={() => setExtractedData(null)}
                    className="text-[10px] text-zinc-500 hover:text-zinc-300 font-medium transition-colors"
                  >
                    ← Cancel
                  </button>
                  <button
                    disabled={isSaving}
                    onClick={saveToSheet}
                    className="px-8 py-2.5 bg-emerald-600 rounded-lg font-bold text-xs hover:bg-emerald-500 transition-all disabled:opacity-50 flex items-center space-x-2"
                  >
                    {isSaving ? (
                      <>
                        <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                        <span>Saving...</span>
                      </>
                    ) : (
                      <span>Save to Sheet</span>
                    )}
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </section>

        {/* Status Message */}
        <div className="h-4">
          <AnimatePresence>
            {message && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className={`text-center text-[10px] font-medium ${message.includes('Error') ? 'text-red-400' : 'text-blue-400'}`}
              >
                {message}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </main>
  );
}
