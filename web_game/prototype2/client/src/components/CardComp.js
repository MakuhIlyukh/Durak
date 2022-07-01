

export default function CardComp({rank, suit, color}) {
	return (
		<div className={`card ${color}`} data-value={rank}>
			{suit}
		</div>
	)
}