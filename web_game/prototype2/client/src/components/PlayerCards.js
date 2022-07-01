import CardComp from "./CardComp";

export default function PlayerCards ( {player_cards} ) {
	return (
		<div className="player2_cards grid-container">
			{
				player_cards.map((e, i) => {
					return <CardComp rank={e.rank} suit={e.suit} color={e.color} key={i} />;
				})
			}	
		</div>
	)
}