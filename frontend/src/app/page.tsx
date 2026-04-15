'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface InvoiceRecord {
  buyer_name: string;
  buyer_address: string;
  gst_no: string;
  mobile_no: string;
  bill_no: string;
  date: string;
  total_amount: string;
  status?: 'pending' | 'processing' | 'done' | 'error';
  error?: string;
  id?: string;
}

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [records, setRecords] = useState<InvoiceRecord[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState<'upload' | 'review'>('upload');

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
      setActiveTab('upload');
      setRecords([]);
      setMessage(`${e.target.files.length} files selected.`);
    }
  };

  const processInvoices = async () => {
    if (files.length === 0) return;
    setIsProcessing(true);
    setActiveTab('review');
    setRecords([]);
    
    setMessage(`Starting parallel extraction of ${files.length} files...`);

    try {
      const extractionPromises = files.map(async (file) => {
        try {
          const formData = new FormData();
          formData.append('file', file);

          const response = await fetch(`${backendUrl}/extract`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Extraction failed');
          }
          
          const data = await response.json();
          return { ...data, status: 'done', id: Math.random().toString(36).substr(2, 9) };
        } catch (error: any) {
          console.error(`Error processing ${file.name}:`, error);
          return {
            buyer_name: file.name,
            buyer_address: '',
            gst_no: '',
            mobile_no: '',
            bill_no: '',
            date: '',
            total_amount: '',
            status: 'error',
            error: error.message || 'Processing failed',
            id: Math.random().toString(36).substr(2, 9)
          } as InvoiceRecord;
        }
      });

      const results = await Promise.all(extractionPromises);
      setRecords(results);
      setMessage(`Processed ${files.length} files. Review and save.`);
    } catch (error: any) {
      console.error('Batch processing error:', error);
      setMessage(`Batch error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const saveToSheet = async () => {
    if (records.length === 0) return;
    setIsSaving(true);
    setMessage('Saving all records to Google Sheet...');
    
    try {
      const validRecords = records.filter(r => r.status === 'done');
      
      const response = await fetch(`${backendUrl}/save-bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validRecords),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Save failed');
      }
      
      const result = await response.json();
      setMessage(`Successfully saved ${result.count} records! ✨`);
      
      setTimeout(() => {
        setFiles([]);
        setRecords([]);
        setActiveTab('upload');
        setMessage('');
      }, 4000);
    } catch (error: any) {
      console.error(error);
      setMessage(`Error: ${error.message || 'Error saving to sheet'}`);
    } finally {
      setIsSaving(false);
    }
  };

  const updateRecord = (id: string, field: keyof InvoiceRecord, value: string) => {
    setRecords(records.map(r => r.id === id ? { ...r, [field]: value } : r));
  };

  return (
    <main className="h-screen bg-[#0a0a0c] text-white font-[family-name:var(--font-geist-sans)] p-4 flex flex-col items-center justify-center overflow-hidden">
      <div className="w-full max-w-6xl space-y-4">
        {/* Header */}
        <header className="space-y-1 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent"
          >
            Bill Genius Bulk
          </motion.h1>
          <p className="text-zinc-500 text-xs">
            High-precision bulk invoice extraction.
          </p>
        </header>

        {/* Main Interface */}
        <section className="relative px-4">
          <div className="absolute inset-x-0 top-0 h-64 bg-blue-500/5 blur-[100px] rounded-full pointer-events-none" />
          
          <div className="relative bg-zinc-900/40 backdrop-blur-2xl border border-zinc-800/50 rounded-2xl p-6 shadow-2xl overflow-hidden min-h-[400px] flex flex-col">
            
            {activeTab === 'upload' ? (
              <div className="flex-1 flex flex-col justify-center space-y-6">
                <div className="flex flex-col items-center justify-center border border-dashed border-zinc-700/50 rounded-xl p-12 transition-colors hover:border-blue-500/30 group bg-zinc-950/30">
                  <input
                    type="file"
                    multiple
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center space-y-4 text-center">
                    <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="space-y-1">
                      <p className="text-lg font-medium">
                        {files.length > 0 ? `${files.length} files ready` : 'Upload PDF invoices'}
                      </p>
                      <p className="text-xs text-zinc-500">Selection will start fresh on every upload</p>
                    </div>
                  </label>
                </div>

                <div className="flex justify-center">
                  <button
                    disabled={files.length === 0 || isProcessing}
                    onClick={processInvoices}
                    className="px-12 py-3 bg-blue-600 rounded-lg font-bold text-sm hover:bg-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-3 shadow-lg shadow-blue-500/20"
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                        <span>Processing Batch...</span>
                      </>
                    ) : (
                      <span>Start Extraction</span>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col space-y-4">
                <div className="flex justify-between items-center mb-2">
                  <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Extracted Results</h2>
                  <button 
                    onClick={() => setActiveTab('upload')}
                    className="text-[10px] text-zinc-500 hover:text-white transition-colors flex items-center space-x-1"
                  >
                    <span>← Back to Upload</span>
                  </button>
                </div>

                <div className="flex-1 overflow-auto border border-zinc-800 rounded-lg bg-zinc-950/20">
                  <table className="w-full text-[10px] text-left border-collapse">
                    <thead className="sticky top-0 bg-zinc-900 border-b border-zinc-800 z-10">
                      <tr>
                        <th className="px-3 py-2 text-zinc-500 font-bold uppercase tracking-tighter">Buyer Name</th>
                        <th className="px-3 py-2 text-zinc-500 font-bold uppercase tracking-tighter">Mobile</th>
                        <th className="px-3 py-2 text-zinc-500 font-bold uppercase tracking-tighter">Bill No</th>
                        <th className="px-3 py-2 text-zinc-500 font-bold uppercase tracking-tighter">Amount</th>
                        <th className="px-3 py-2 text-zinc-500 font-bold uppercase tracking-tighter">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                      {records.length === 0 && (
                        <tr>
                          <td colSpan={5} className="py-20 text-center text-zinc-600 italic">No records yet. Initializing...</td>
                        </tr>
                      )}
                      {records.map((record) => (
                        <tr key={record.id} className="hover:bg-zinc-800/10 transition-colors group">
                          <td className="px-3 py-1.5">
                            <input
                              className="w-full bg-transparent border-none focus:ring-1 focus:ring-blue-500/50 rounded px-1 py-0.5 text-zinc-200 outline-none"
                              value={record.buyer_name}
                              onChange={(e) => updateRecord(record.id!, 'buyer_name', e.target.value)}
                            />
                          </td>
                          <td className="px-3 py-1.5">
                            <input
                              className="w-full bg-transparent border-none focus:ring-1 focus:ring-blue-500/50 rounded px-1 py-0.5 text-zinc-200 outline-none"
                              value={record.mobile_no}
                              onChange={(e) => updateRecord(record.id!, 'mobile_no', e.target.value)}
                            />
                          </td>
                          <td className="px-3 py-1.5">
                            <input
                              className="w-full bg-transparent border-none focus:ring-1 focus:ring-blue-500/50 rounded px-1 py-0.5 text-zinc-200 outline-none"
                              value={record.bill_no}
                              onChange={(e) => updateRecord(record.id!, 'bill_no', e.target.value)}
                            />
                          </td>
                          <td className="px-3 py-1.5 font-mono text-blue-400">
                            <div className="flex items-center space-x-1">
                              <span>₹</span>
                              <input
                                className="w-16 bg-transparent border-none focus:ring-1 focus:ring-blue-500/50 rounded px-1 py-0.5 text-blue-400 outline-none"
                                value={record.total_amount}
                                onChange={(e) => updateRecord(record.id!, 'total_amount', e.target.value)}
                              />
                            </div>
                          </td>
                          <td className="px-3 py-1.5">
                            {record.status === 'done' ? (
                              <span className="text-[9px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-500 rounded-full font-bold border border-emerald-500/20">READY</span>
                            ) : (
                              <span className="text-[9px] px-1.5 py-0.5 bg-red-500/10 text-red-500 rounded-full font-bold border border-red-500/20" title={record.error}>ERROR</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="flex justify-end pt-2">
                  <button
                    disabled={isSaving || isProcessing || records.filter(r => r.status === 'done').length === 0}
                    onClick={saveToSheet}
                    className="px-10 py-2.5 bg-emerald-600 rounded-lg font-bold text-xs hover:bg-emerald-500 transition-all disabled:opacity-50 flex items-center space-x-2 shadow-lg shadow-emerald-500/10"
                  >
                    {isSaving ? (
                      <>
                        <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                        <span>Saving Batch...</span>
                      </>
                    ) : (
                      <span>Save {records.filter(r => r.status === 'done').length} Items to Sheet</span>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Status Message */}
        <div className="h-6">
          <AnimatePresence>
            {message && (
              <motion.div
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`text-center text-[10px] font-medium px-4 py-1 rounded-full w-max mx-auto border ${message.includes('Error') ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-blue-500/10 border-blue-500/20 text-blue-400'}`}
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
