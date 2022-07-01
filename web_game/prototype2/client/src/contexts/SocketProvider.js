import React, { useContext, useEffect, useRef} from 'react'
import io from 'socket.io-client'

const SocketContext = React.createContext()

export function useSocket() {
  return useContext(SocketContext)
}

export function SocketProvider({ children }) {
  // socket
  const sockRef = useRef() 

  useEffect(() => {
    // connecting...
    sockRef.current = io(
      'http://localhost:5000',
    );

    // cleanup
    return () => {
      // closing connection...
      sockRef.current.close();
    }
  }, [])

  return (
    <SocketContext.Provider value={sockRef}>
      {children}
    </SocketContext.Provider>
  )
}