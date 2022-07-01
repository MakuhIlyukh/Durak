import { useEffect, useState } from "react"
import { useGameInfo } from "../contexts/GameInfoProvider"
import { useSocket } from "../contexts/SocketProvider"
import CardComp from "./CardComp"
import EnemyCards from "./EnemyCards"
import EnemyTable from "./EnemyTable"
import PlayerCards from "./PlayerCards"
import PlayerTable from "./PlayerTable"
import { Card } from "../utils/cards"


export default function Game ( {compId, setCompId} ) {

	const gameInfo = useGameInfo()
	const sockRef = useSocket()

	const [playerCards, setPlayerCards] = useState([
		new Card('10', '♠'),
		new Card('J', '♣'),
		new Card('6', '♥')
	])
	const [playerTable, setPlayerTable] = useState([
		new Card('10', '♠'),
		new Card('J', '♣'),
		new Card('6', '♥')
	])
	const [enemyTable, setEnemyTable] = useState([
		new Card('10', '♠'),
		new Card('J', '♣'),
		new Card('6', '♥')
	])
	const [enemyCards, setEnemyCards] = useState(5)
	const [trumpCard, setTrumpCard] = useState(new Card('', 'X'))
	const [deckSize, setDeckSize] = useState(36)
	const [infoMes, setInfoMes] = useState("Загрузка игры")

	const [tempState, setTempState] = useState(0)

	useEffect(() => {

		sockRef.current.emit(
			'ready to play'
		)
	}, []) 

	useEffect(() => {
		console.log(tempState)

	}, [tempState])

	return (
		<>
			<>{ tempState }</>
			<button onClick={ () => {setTempState(prev => prev + 1)} }>hello wolrd</button>
			<div className="info-container">
				<div className="info-text">{infoMes}</div>
				<div className="text trump-text">Козырь: </div>
				<div className="trump">
					<CardComp rank={trumpCard.rank} suit={trumpCard.suit} color={trumpCard.color}/>
				</div>
				<div className="text deck-text">Колода:</div>
				<div className="card black deck-size">{deckSize}</div>
			</div>

			<div className="text">Карты Игрока 1:</div>

			{/* Карты противника на руке */}
			<EnemyCards n_cards={enemyCards} />

			<div className="text">Стол Игрока 1:</div>

			{/* Карты противника на столе */}
			<EnemyTable enemy_table_cards={enemyTable} />

			<div className="text">Стол Игрока 2:</div>

			{/* Карты игрока на столе */}
			<PlayerTable player_table_cards={playerTable} />

			<div className="text">Карты Игрока 2:</div>

			{/* Карты игрока на руке */}
			<PlayerCards player_cards={playerCards} />
		</>
	)
}