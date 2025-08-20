import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Generate from './pages/Generate'
import Scraper from './pages/Scraper'
import Deploy from './pages/Deploy'
import Settings from './pages/Settings'
import Chat from './pages/Chat'
import Monitoring from './pages/Monitoring'

import { useSystemStore } from './hooks/useSystemStore'

function App() {
  const { initialize, isInitialized } = useSystemStore()

  useEffect(() => {
    // Initialize the system on app startup
    initialize()
  }, [initialize])

  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 mb-4">
            🌊 SERRA ORGIN
          </div>
          <div className="text-slate-400 text-lg">Initializing framework...</div>
          <div className="mt-4">
            <div className="w-8 h-8 border-4 border-slate-600 border-t-cyan-400 rounded-full animate-spin mx-auto"></div>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Layout>
        <AnimatePresence mode="wait">
          <Routes>
            <Route
              path="/"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Dashboard />
                </motion.div>
              }
            />
            <Route
              path="/agents"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Agents />
                </motion.div>
              }
            />
            <Route
              path="/generate"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Generate />
                </motion.div>
              }
            />
            <Route
              path="/scraper"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Scraper />
                </motion.div>
              }
            />
            <Route
              path="/deploy"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Deploy />
                </motion.div>
              }
            />
            <Route
              path="/chat"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Chat />
                </motion.div>
              }
            />
            <Route
              path="/monitoring"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Monitoring />
                </motion.div>
              }
            />
            <Route
              path="/settings"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Settings />
                </motion.div>
              }
            />
          </Routes>
        </AnimatePresence>
      </Layout>
    </div>
  )
}

export default App
