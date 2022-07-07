import { useSocket } from "../contexts/SocketProvider"

export default function CardComp({rank, suit, color, clickable, click_handler}) {
	return (
		<div className={`card ${color}`}
			 data-value={rank}
			 onClick={clickable ? (e) => {click_handler(rank, suit)} : (e) => {}}
			 style={clickable ? {cursor: 'pointer'} : {}} >
			{suit}
		</div>
	)
}