import './App.css';
import Switcher from "./components/Switcher";
import { GameInfoProvider } from "./contexts/GameInfoProvider";
import { SocketProvider } from "./contexts/SocketProvider";


function App() {
  return (
    <SocketProvider >
      <GameInfoProvider>
        <div className="App">
          <Switcher />
        </div>
      </GameInfoProvider>
    </SocketProvider>
  );
}

export default App;
