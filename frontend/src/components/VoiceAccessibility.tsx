import React, { useState, useEffect, useRef } from 'react';

interface VoiceCommand {
  text: string;
  confidence?: number;
}

interface VoiceResponse {
  message: string;
  success: boolean;
  data?: any;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

const VoiceAccessibility: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{type: 'user' | 'system', text: string, timestamp: Date}>>([]);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [speechRecognition, setSpeechRecognition] = useState<any>(null);
  const [speechSynthesis, setSpeechSynthesis] = useState<SpeechSynthesis | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize speech recognition and synthesis
  useEffect(() => {
    // Check for speech recognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript;
        const confidence = event.results[0][0].confidence;
        
        addMessage('user', transcript);
        sendVoiceCommand(transcript, confidence);
      };
      
      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        addMessage('system', `Speech recognition error: ${event.error}`);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      setSpeechRecognition(recognition);
    } else {
      addMessage('system', 'Speech recognition not supported in this browser');
    }

    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      setSpeechSynthesis(window.speechSynthesis);
    } else {
      addMessage('system', 'Speech synthesis not supported in this browser');
    }

    // Initialize WebSocket connection
    initializeWebSocket();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const initializeWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/voice/ws');
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        addMessage('system', 'Connected to voice accessibility service');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        addMessage('system', 'Disconnected from voice accessibility service');
        setSessionId(null);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addMessage('system', 'Connection error to voice service');
      };
      
      setWebsocket(ws);
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      addMessage('system', 'Failed to connect to voice service. Make sure the backend is running.');
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'session_started':
        setSessionId(data.session_id);
        addMessage('system', data.message);
        speak(data.message);
        break;
      
      case 'command_response':
        const response: VoiceResponse = data.response;
        addMessage('system', response.message);
        speak(response.message);
        setIsProcessing(false);
        break;
      
      case 'error':
        addMessage('system', `Error: ${data.message}`);
        speak(`Error: ${data.message}`);
        setIsProcessing(false);
        break;
    }
  };

  const addMessage = (type: 'user' | 'system', text: string) => {
    setMessages(prev => [...prev, { type, text, timestamp: new Date() }]);
  };

  const speak = (text: string) => {
    if (speechSynthesis && text) {
      // Cancel any ongoing speech
      speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 1;
      
      speechSynthesis.speak(utterance);
    }
  };

  const startListening = () => {
    if (speechRecognition && !isListening && !isProcessing) {
      setIsListening(true);
      speechRecognition.start();
    }
  };

  const stopListening = () => {
    if (speechRecognition && isListening) {
      speechRecognition.stop();
      setIsListening(false);
    }
  };

  const sendVoiceCommand = (text: string, confidence?: number) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      setIsProcessing(true);
      websocket.send(JSON.stringify({
        type: 'voice_command',
        text: text,
        confidence: confidence
      }));
    } else {
      addMessage('system', 'Not connected to voice service');
    }
  };

  const testCommand = (command: string) => {
    addMessage('user', command);
    sendVoiceCommand(command);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Voice Accessibility Tool
        </h1>
        <p className="text-gray-600">
          Speak commands to control web browsers for enhanced accessibility
        </p>
      </div>

      {/* Connection Status */}
      <div className="mb-4 p-3 rounded-lg bg-gray-50">
        <div className="flex items-center justify-between">
          <span className="font-medium">
            Status: {sessionId ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
          {sessionId && (
            <span className="text-sm text-gray-500">
              Session: {sessionId.slice(0, 8)}...
            </span>
          )}
        </div>
      </div>

      {/* Voice Controls */}
      <div className="mb-6 flex gap-4">
        <button
          onClick={startListening}
          disabled={isListening || isProcessing || !sessionId}
          className={`px-6 py-3 rounded-lg font-medium transition-colors ${
            isListening
              ? 'bg-red-500 text-white'
              : isProcessing
              ? 'bg-yellow-500 text-white'
              : sessionId
              ? 'bg-blue-500 hover:bg-blue-600 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isListening ? '🎤 Listening...' : isProcessing ? '⏳ Processing...' : '🎤 Start Voice Command'}
        </button>

        {isListening && (
          <button
            onClick={stopListening}
            className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium"
          >
            Stop Listening
          </button>
        )}
      </div>

      {/* Quick Test Commands */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">Quick Test Commands:</h3>
        <div className="flex flex-wrap gap-2">
          {[
            'Go to Google',
            'Go to Amazon',
            'Search for wireless headphones',
            'Read the page'
          ].map((command) => (
            <button
              key={command}
              onClick={() => testCommand(command)}
              disabled={isProcessing || !sessionId}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white rounded-lg text-sm"
            >
              {command}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
        <h3 className="text-lg font-medium mb-3">Conversation:</h3>
        <div className="space-y-3">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-100 ml-8'
                  : 'bg-white mr-8'
              }`}
            >
              <div className="flex justify-between items-start">
                <span className={`font-medium ${
                  message.type === 'user' ? 'text-blue-800' : 'text-gray-800'
                }`}>
                  {message.type === 'user' ? '👤 You' : '🤖 System'}
                </span>
                <span className="text-xs text-gray-500">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <p className="mt-1 text-gray-700">{message.text}</p>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-800 mb-2">How to use:</h4>
        <ul className="text-blue-700 text-sm space-y-1">
          <li>• Click "Start Voice Command" and speak your request</li>
          <li>• Try commands like "Go to Google", "Search for cats", "Click login button"</li>
          <li>• Use "Read the page" to have content read aloud</li>
          <li>• The system will confirm actions and provide audio feedback</li>
        </ul>
      </div>
    </div>
  );
};

export default VoiceAccessibility;