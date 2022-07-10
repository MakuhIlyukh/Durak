import { useEffect, useState, useRef } from "react"
import { useGameInfo } from "../contexts/GameInfoProvider"
import { useSocket } from "../contexts/SocketProvider"
import CardComp from "./CardComp"
import EnemyCards from "./EnemyCards"
import EnemyTable from "./EnemyTable"
import PlayerCards from "./PlayerCards"
import PlayerTable from "./PlayerTable"
import { Card, objectsArrayToCards, objectToCard } from "../utils/cards"

const ATTACK = 'ATTACK'
const START_ATTACK = 'START_ATTACK'
const SUCC_ATTACK = 'SUCC_ATTACK'
const DEFENSE = 'DEFENSE'
const WIN = 'WIN'
const LOSS = 'LOSS'
const DRAW = 'DRAW'
const YOUR_TURN = 1

export default function Game ( {compId, setCompId} ) {

	const gameInfo = useGameInfo()
	const sockRef = useSocket()

	const [playerCards, setPlayerCards] = useState([
		new Card('10', '♠'),
		new Card('J', '♣'),
		new Card('6', '♥'),
		new Card('', 'F')
	])
	const [playerTable, setPlayerTable] = useState([
		new Card('10', '♠'),
		new Card('J', '♣'),
		new Card('6', '♥'),
	])
	const [enemyTable, setEnemyTable] = useState([
		new Card('10', '♠'),
		new Card('J', '♣'),
		new Card('6', '♥'),
	])
	const [enemyCards, setEnemyCards] = useState(5)
	const [trumpCard, setTrumpCard] = useState(new Card('', 'X'))
	const [deckSize, setDeckSize] = useState(36)
	const [infoMes, setInfoMes] = useState("Загрузка игры...")
	const [curColors, setCurColors] = useState(["green", "white"])
	const [gameState, setGameState] = useState("ATTACK")
	const [turn, setTurn] = useState(1)

	const flagRef = useRef(false)

	useEffect(() => {
		sockRef.current.on(
			"game state",
			({ 
				playerCardsResp,
				playerTableResp,
				enemyTableResp,
				enemyCardsResp,
				trumpCardResp,
				deckSizeResp,
				// infoMesResp,
				gameStateResp,
				turnResp,
			}) => {
				setPlayerCards([...objectsArrayToCards(playerCardsResp), new Card('', 'F')])
				setPlayerTable(objectsArrayToCards(playerTableResp))
				setEnemyTable(objectsArrayToCards(enemyTableResp))
				setEnemyCards(enemyCardsResp)
				setTrumpCard(objectToCard(trumpCardResp))
				setDeckSize(deckSizeResp)
				// setInfoMes(infoMesResp)
				setGameState(gameStateResp)
				setTurn(turnResp)
			}
		)

		sockRef.current.emit(
			'ready to play',
			{room_id: gameInfo.current['room_id']}
		)

		return () => {
			sockRef.current.off(
				"game state"
			);
		}
	}, [])

	useEffect(() => {
		console.log(`curColors[0]: ${curColors[0]}`)
		if (gameState === ATTACK && turn === YOUR_TURN) {
			setInfoMes("Ваша атака")
			setCurColors(['green', 'white'])
		} else if (gameState === ATTACK && turn !== YOUR_TURN) {
			setInfoMes("Ожидание атакующей карты соперника")
			setCurColors(['white', 'green'])
		} else if (gameState === DEFENSE && turn === YOUR_TURN) {
			setInfoMes("Ваша защита")
			setCurColors(['red', 'white'])
		} else if (gameState === DEFENSE && turn !== YOUR_TURN) {
			setInfoMes("Ожидание защищающей карты соперника")
			setCurColors(['white', 'red'])
		} else if (gameState === SUCC_ATTACK && turn === YOUR_TURN) {
			setInfoMes("Даете карты в догонку")
			setCurColors(['blue', 'white'])
		} else if (gameState === SUCC_ATTACK && turn !== YOUR_TURN) {
			setInfoMes("Берете карты в догонку")
			setCurColors(['white', 'blue'])
		} else if (gameState === START_ATTACK && turn === YOUR_TURN) {
			setInfoMes("Начало вашей атаки")
			setCurColors(['green', 'white'])
		} else if (gameState === START_ATTACK && turn !== YOUR_TURN) {
			setInfoMes("Начало атаки врага")
			setCurColors(['white', 'green'])
		} else if (gameState === DRAW) {
			setInfoMes("Ничья")
			setCurColors(['yellow', 'yellow'])
		} else if (gameState === WIN && turn === YOUR_TURN) {
			setInfoMes("Победа")
			setCurColors(['green', 'red'])
		} else if (gameState === WIN && turn !== YOUR_TURN) {
			setInfoMes("Проигрыш")
			setCurColors(['red', 'green'])
		} else if (gameState === LOSS && turn === YOUR_TURN) {
			setInfoMes("Проигрыш")
			setCurColors(['red', 'green'])
		} else if (gameState === LOSS && turn !== YOUR_TURN) {
			setInfoMes("Победа")
			setCurColors(['green', 'red'])
		} else {
			setInfoMes("Unkown situation")
		}
	}, [gameState])

	const click_handler = (rank, suit) => {
		if (turn !== YOUR_TURN) {
			return;
		}

		if (suit === 'F') {
			if (gameState === START_ATTACK) {
				return;
			} else if (gameState === ATTACK) {
				setTurn(1 - turn)
				setGameState(START_ATTACK)
			} else if (gameState === DEFENSE) {
				setTurn(1 - turn)
				setGameState(SUCC_ATTACK)
			} else if (gameState === SUCC_ATTACK) {
				setGameState(ATTACK)
			} else if (gameState === WIN || gameState === LOSS || gameState === DRAW) {
				return;
			}
		} else {
			if (gameState === START_ATTACK) {
				setTurn(1 - turn)
				setGameState(DEFENSE)
			} else if (gameState === ATTACK) {
				setTurn(1 - turn)
				setGameState(DEFENSE)
			} else if (gameState === DEFENSE) {
				setTurn(1 - turn)
				setGameState(ATTACK)
			} else if (gameState === SUCC_ATTACK) {
				setGameState(SUCC_ATTACK)
			} else if (gameState === WIN || gameState === LOSS || gameState === DRAW) {
				return;
			}
			setPlayerTable(cards => [...cards, new Card(rank, suit)])
			setPlayerCards(cards => cards.filter(card => {
				return card.rank !== rank || card.suit !== suit;
			}))
		}


		sockRef.current.emit(
			'step',
			{
				room_id: gameInfo.current['room_id'],
				rank: (suit === 'F'? null : rank),
				suit: (suit === 'F'? null : suit),
				action: (suit === 'F'? 'FINISH' : 'PUT')
			},
		)
	}

	return (
		<>
			<div>Комната: {gameInfo.current['room_id']}</div>
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
			<EnemyCards n_cards={enemyCards}
						curColor={curColors[1]} />

			<div className="text">Стол Игрока 1:</div>

			{/* Карты противника на столе */}
			<EnemyTable enemy_table_cards={enemyTable} />

			<div className="text">Стол Игрока 2:</div>

			{/* Карты игрока на столе */}
			<PlayerTable player_table_cards={playerTable} />

			<div className="text">Карты Игрока 2:</div>

			{/* Карты игрока на руке */}
			<PlayerCards player_cards={playerCards}
						 click_handler={click_handler}
						 curColor={curColors[0]} />
		</>
	)
}