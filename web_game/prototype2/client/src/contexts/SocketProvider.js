import React, { useContext, useEffect, useRef} from 'react'
import io from 'socket.io-client'


const URI = 'http://localhost:5000'
// const URI = 'https://ilia-durak.herokuapp.com/'
// const URI = 'https://fd2f-92-42-30-161.ngrok.io'

const SocketContext = React.createContext()

export function useSocket() {
  return useContext(SocketContext)
}

export function SocketProvider({ children }) {
  // socket
  const sockRef = useRef() 

  // if strict mode enabled, then useEffect executes twice
  useEffect(() => {
    // connecting...
    sockRef.current = io(
      URI
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