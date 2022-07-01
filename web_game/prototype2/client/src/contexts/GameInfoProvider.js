import React, { useContext, useRef} from 'react'

const GameInfoContext = React.createContext()

export function useGameInfo() {
  return useContext(GameInfoContext)
}

export function GameInfoProvider({ children }) {
  const gameInfo = useRef({}) 

  return (
    <GameInfoContext.Provider value={gameInfo}>
      {children}
    </GameInfoContext.Provider>
  )
}